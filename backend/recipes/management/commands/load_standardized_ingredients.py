import json
import os

from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import (
    Ingredient,
    IngredientNutrient,
    Nutrient,
    Recipe,
    RecipeIngredient,
)


class Command(BaseCommand):
    help = 'Load structured ingredient and nutrient data from standardized JSON files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--standardized',
            type=str,
            default='../data_preparation/data/bbcgoodfood_recipes_standardized.json',
            help='Path to standardized recipes JSON (relative to backend/)'
        )
        parser.add_argument(
            '--nutrients',
            type=str,
            default='../data_preparation/data/fdc_nutrients.json',
            help='Path to FDC nutrients JSON (relative to backend/)'
        )

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        standardized_path = os.path.join(base_dir, options['standardized'])
        nutrients_path = os.path.join(base_dir, options['nutrients'])

        self.stdout.write('Reading JSON files...')
        fdc_nutrients = self._load_fdc_nutrients(nutrients_path)
        recipes_data = self._load_json(standardized_path)

        # Phase 1: upsert Nutrient catalog
        nutrient_map = self._upsert_nutrients(fdc_nutrients)

        # Phase 2: upsert all Ingredient records in one pass
        ingredient_map = self._upsert_ingredients(recipes_data)

        # Phase 3: load RecipeIngredient records
        ri_count = self._load_recipe_ingredients(recipes_data, ingredient_map)

        # Phase 4: load IngredientNutrient records (once per unique ingredient)
        in_count = self._load_ingredient_nutrients(ingredient_map, fdc_nutrients, nutrient_map)

        # Phase 5: pre-calculate and store aggregated nutrients on each Recipe
        recipe_count = self._calculate_aggregated_nutrients()

        self.stdout.write(self.style.SUCCESS(
            f'Done. Ingredients: {len(ingredient_map)}, RecipeIngredients: {ri_count}, '
            f'NutrientValues: {in_count}, Nutrient types: {len(nutrient_map)}, '
            f'Recipes updated: {recipe_count}'
        ))

    # ------------------------------------------------------------------ helpers

    def _load_json(self, path: str):
        try:
            with open(path, encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {path}'))
            raise

    def _load_fdc_nutrients(self, path: str) -> dict:
        if not os.path.exists(path):
            self.stdout.write(self.style.WARNING(
                f'Nutrients file not found: {path}\n'
                'Run data_preparation/fetch_fdc_nutrients.py first.\n'
                'Continuing without micronutrient data.'
            ))
            return {}
        return self._load_json(path)

    def _upsert_nutrients(self, fdc_nutrients: dict) -> dict[str, Nutrient]:
        if not fdc_nutrients:
            return {}

        defs: dict[str, dict] = {}
        for entry in fdc_nutrients.values():
            for n in entry.get('nutrients', []):
                nid = n.get('id')
                if nid and nid not in defs:
                    defs[nid] = {'name': n['name'], 'unit': n['unit']}

        nutrient_map: dict[str, Nutrient] = {}
        for fdc_nutrient_id, attrs in defs.items():
            obj, _ = Nutrient.objects.update_or_create(
                fdc_nutrient_id=str(fdc_nutrient_id),
                defaults={'name': attrs['name'], 'unit': attrs['unit']}
            )
            nutrient_map[str(fdc_nutrient_id)] = obj

        self.stdout.write(self.style.SUCCESS(f'Nutrient types: {len(nutrient_map)}'))
        return nutrient_map

    def _upsert_ingredients(self, recipes_data: list) -> dict[str, Ingredient]:
        """Collect all unique ingredients from JSON, bulk-create new ones, return full map."""
        # Collect unique ingredients from JSON
        unique: dict[str, dict] = {}  # canonical_name → {fdc_id, fdc_description, fdc_category}
        for recipe in recipes_data:
            for ing in recipe.get('standardized_ingredients', []):
                if not ing.get('parse_success'):
                    continue
                name = (ing.get('canonical_name') or '').strip()
                if not name or name in unique:
                    continue
                match = ing.get('fdc_best_match') or {}
                unique[name] = {
                    'fdc_id': match.get('fdc_id'),
                    'fdc_description': match.get('description'),
                    'fdc_category': match.get('category'),
                }

        # Load already-existing ingredients
        existing = {obj.canonical_name: obj for obj in Ingredient.objects.filter(canonical_name__in=unique.keys())}

        # Create new ingredients
        new_names = [n for n in unique if n not in existing]
        if new_names:
            new_objs = [
                Ingredient(
                    canonical_name=name,
                    fdc_id=unique[name]['fdc_id'],
                    fdc_description=unique[name]['fdc_description'],
                    fdc_category=unique[name]['fdc_category'],
                )
                for name in new_names
            ]
            Ingredient.objects.bulk_create(new_objs, ignore_conflicts=True)
            # Re-fetch to get DB IDs
            new_created = {obj.canonical_name: obj for obj in Ingredient.objects.filter(canonical_name__in=new_names)}
            existing.update(new_created)

        self.stdout.write(self.style.SUCCESS(f'Ingredients in DB: {len(existing)} (new: {len(new_names)})'))
        return existing

    def _load_recipe_ingredients(self, recipes_data: list, ingredient_map: dict[str, Ingredient]) -> int:
        recipe_by_url = {r.source: r for r in Recipe.objects.only('id', 'source') if r.source}

        # Delete all existing RecipeIngredient records for matched recipes in one query
        matched_recipes = [recipe_by_url[r['url']] for r in recipes_data if r.get('url') in recipe_by_url]
        if matched_recipes:
            RecipeIngredient.objects.filter(recipe__in=matched_recipes).delete()

        all_ri: list[RecipeIngredient] = []
        skipped = 0

        for i, recipe_data in enumerate(recipes_data, 1):
            recipe = recipe_by_url.get(recipe_data.get('url'))
            if recipe is None:
                skipped += 1
                continue

            for ing in recipe_data.get('standardized_ingredients', []):
                if not ing.get('parse_success'):
                    continue
                name = (ing.get('canonical_name') or '').strip()
                ingredient = ingredient_map.get(name)
                if not ingredient:
                    continue

                primary = ing.get('primary_amount') or {}
                all_ri.append(RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient,
                    raw_text=(ing.get('raw_text') or '')[:500],
                    quantity_in_grams=primary.get('quantity_in_grams'),
                    preparation=ing.get('preparation'),
                    parse_confidence=ing.get('parse_confidence'),
                ))

            if i % 500 == 0:
                self.stdout.write(f'  Building RecipeIngredients: {i}/{len(recipes_data)}...')

        with transaction.atomic():
            RecipeIngredient.objects.bulk_create(all_ri, batch_size=2000)

        self.stdout.write(self.style.SUCCESS(
            f'RecipeIngredients: {len(all_ri)} (skipped {skipped} unmatched recipes)'
        ))
        return len(all_ri)

    def _load_ingredient_nutrients(
        self,
        ingredient_map: dict[str, Ingredient],
        fdc_nutrients: dict,
        nutrient_map: dict[str, Nutrient],
    ) -> int:
        if not fdc_nutrients or not nutrient_map:
            return 0

        # Build fdc_id → [Ingredient, ...] — multiple canonical names can share one FDC ID
        fdc_to_ingredients: dict[str, list[Ingredient]] = {}
        for ingredient in ingredient_map.values():
            if ingredient.fdc_id:
                fdc_to_ingredients.setdefault(str(ingredient.fdc_id), []).append(ingredient)

        # Delete existing IngredientNutrient records for these ingredients
        IngredientNutrient.objects.filter(ingredient__in=ingredient_map.values()).delete()

        all_in: list[IngredientNutrient] = []

        for fdc_id_str, ingredients in fdc_to_ingredients.items():
            entry = fdc_nutrients.get(fdc_id_str)
            if not entry:
                continue
            nutrient_rows = [
                (str(n.get('id', '')), n.get('value'))
                for n in entry.get('nutrients', [])
                if n.get('value') is not None and str(n.get('id', '')) in nutrient_map
            ]
            for ingredient in ingredients:
                for nid, value in nutrient_rows:
                    all_in.append(IngredientNutrient(
                        ingredient=ingredient,
                        nutrient=nutrient_map[nid],
                        value_per_100g=value,
                    ))

        with transaction.atomic():
            IngredientNutrient.objects.bulk_create(all_in, batch_size=5000)

        self.stdout.write(self.style.SUCCESS(f'IngredientNutrient values: {len(all_in)}'))
        return len(all_in)

    def _calculate_aggregated_nutrients(self) -> int:
        recipes = Recipe.objects.prefetch_related(
            'structured_ingredients__ingredient__nutrient_values__nutrient'
        ).all()

        to_update = []
        for recipe in recipes:
            totals: dict[str, float] = {}
            units: dict[str, str] = {}

            for ri in recipe.structured_ingredients.all():
                if ri.quantity_in_grams is None:
                    continue
                factor = ri.quantity_in_grams / 100
                for iv in ri.ingredient.nutrient_values.all():
                    name = iv.nutrient.name
                    totals[name] = totals.get(name, 0.0) + iv.value_per_100g * factor
                    units[name] = iv.nutrient.unit

            recipe.aggregated_nutrients = [
                {'name': name, 'unit': units[name], 'value': round(total, 3)}
                for name, total in sorted(totals.items())
            ]
            to_update.append(recipe)

        with transaction.atomic():
            Recipe.objects.bulk_update(to_update, ['aggregated_nutrients'], batch_size=500)

        self.stdout.write(self.style.SUCCESS(f'Recipes with aggregated nutrients: {len(to_update)}'))
        return len(to_update)
