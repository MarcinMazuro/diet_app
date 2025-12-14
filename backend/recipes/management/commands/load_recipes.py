from django.core.management.base import BaseCommand
from django.db import transaction

from recipes.models import Recipe, Category, RecipeCategory
import json
import os


class Command(BaseCommand):
    help = 'Load recipes and categories from JSON files into database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--recipes',
            type=str,
            default='../data_preparation/data/bbcgoodfood_recipes_clean.json',
            help='Path to recipes JSON file (relative to backend dir)'
        )
        parser.add_argument(
            '--categories',
            type=str,
            default='../data_preparation/data/categories.json',
            help='Path to categories JSON file (relative to backend dir)'
        )

    def handle(self, *args, **options):
        recipes_path = options['recipes']
        categories_path = options['categories']

        # Get base directory (backend folder)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        recipes_full_path = os.path.join(base_dir, recipes_path)
        categories_full_path = os.path.join(base_dir, categories_path)

        self.stdout.write(f'Loading categories from: {categories_full_path}')
        categories_dict = self.load_categories(categories_full_path)
        category_map = self.insert_categories(categories_dict)

        self.stdout.write(f'Loading recipes from: {recipes_full_path}')
        recipes = self.load_recipes(recipes_full_path)

        self.remove_stale_recipes(recipes)

        self.insert_recipes(recipes, category_map)

        self.stdout.write(self.style.SUCCESS('Successfully loaded all data!'))

    def load_categories(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            raise
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Invalid JSON in categories file: {e}'))
            raise

    def load_recipes(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            raise
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Invalid JSON in recipes file: {e}'))
            raise

    def remove_stale_recipes(self, recipes_data):
        """
        Delete recipes that are no longer present in the provided recipes_data.
        """
        sources_in_file = {r.get('url') for r in recipes_data if r.get('url')}

        if not sources_in_file:
            self.stdout.write('No source URLs found in JSON; skipping stale deletion.')
            return

        # Delete recipes which are not not in recipe file
        qs = Recipe.objects.exclude(source__in=sources_in_file)
        stale_count = qs.count()
        if stale_count:
            with transaction.atomic():
                qs.delete()
            self.stdout.write(self.style.WARNING(f'Deleted {stale_count} stale recipes not present in JSON'))
        else:
            self.stdout.write('No stale recipes to delete.')


    def insert_categories(self, categories_dict):
        """Inserts categories with types and returns mapping name_lowercase->Category object"""
        category_map = {}

        for category_type, category_list in categories_dict.items():
            for category_name in category_list:
                category, created = Category.objects.update_or_create(
                    name=category_name,
                    defaults={'type': category_type}
                )
                category_map[category_name.lower()] = category
                if created:
                    self.stdout.write(f'  Created category: {category_name} ({category_type})')

        self.stdout.write(self.style.SUCCESS(f'Loaded {len(category_map)} categories'))
        return category_map

    def insert_recipes(self, recipes_data, category_map):
        """Inserts recipes with their categories"""
        created_count = 0
        updated_count = 0
        links_count = 0

        for i, recipe_data in enumerate(recipes_data, 1):
            recipe, created = Recipe.objects.update_or_create(
                name=recipe_data.get('name'),
                defaults={
                    'source': recipe_data.get('url'),
                    'description': recipe_data.get('description'),
                    'ingredients': recipe_data.get('ingredients', []),
                    'directions': recipe_data.get('instructions', []),
                    'servings': recipe_data.get('servings'),
                    'preparation_time': recipe_data.get('total_minutes'),
                    'fiber': recipe_data.get('fiber'),
                    'calories': recipe_data.get('calories'),
                    'fat': recipe_data.get('fat'),
                    'saturated_fat': recipe_data.get('saturated_fat'),
                    'carbohydrate': recipe_data.get('carbohydrate'),
                    'sugar': recipe_data.get('sugar'),
                    'protein': recipe_data.get('protein'),
                    'sodium': recipe_data.get('sodium'),
                    'image_url': recipe_data.get('image_url')
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

            # Link categories
            for category_name in recipe_data.get('categories', []):
                category_lower = category_name.lower()
                if category_lower in category_map:
                    _, link_created = RecipeCategory.objects.get_or_create(
                        recipe=recipe,
                        category=category_map[category_lower]
                    )
                    if link_created:
                        links_count += 1

            # Progress indicator
            if i % 100 == 0:
                self.stdout.write(f'  Processed {i} recipes...')

        self.stdout.write(self.style.SUCCESS(f'Created {created_count} new recipes'))
        self.stdout.write(self.style.SUCCESS(f'Updated {updated_count} existing recipes'))
        self.stdout.write(self.style.SUCCESS(f'Created {links_count} recipe-category links'))

