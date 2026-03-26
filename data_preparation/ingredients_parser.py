from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from ingredient_parser import parse_ingredient


def _safe_float(value: Any) -> float | None:
    if isinstance(value, Fraction):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _amount_to_dict(amount: Any) -> dict[str, Any]:
    unit_value = getattr(amount, "unit", None)
    unit_text = str(unit_value) if unit_value is not None else ""
    unit_system = getattr(getattr(amount, "unit_system", None), "value", None)

    amount_dict = {
        "text": getattr(amount, "text", None),
        "quantity": _safe_float(getattr(amount, "quantity", None)),
        "quantity_max": _safe_float(getattr(amount, "quantity_max", None)),
        "unit": unit_text,
        "unit_system": unit_system,
        "approximate": bool(getattr(amount, "APPROXIMATE", False)),
        "singular": bool(getattr(amount, "SINGULAR", False)),
        "range": bool(getattr(amount, "RANGE", False)),
        "multiplier": bool(getattr(amount, "MULTIPLIER", False)),
        "prepared_ingredient": bool(getattr(amount, "PREPARED_INGREDIENT", False)),
        "confidence": getattr(amount, "confidence", None),
    }

    grams = None
    try:
        converted = amount.convert_to("gram")
        grams = float(converted.quantity)
    except Exception:
        grams = None

    amount_dict["quantity_in_grams"] = grams
    return amount_dict


def _foundation_food_to_dict(item: Any) -> dict[str, Any]:
    return {
        "fdc_id": getattr(item, "fdc_id", None),
        "description": getattr(item, "text", None),
        "confidence": getattr(item, "confidence", None),
        "category": getattr(item, "category", None),
        "data_type": getattr(item, "data_type", None),
        "url": getattr(item, "url", None),
        "name_index": getattr(item, "name_index", None),
    }


def standardize_ingredient(raw_ingredient: str) -> dict[str, Any]:
    parsed = parse_ingredient(raw_ingredient, foundation_foods=True)

    names = [item.text for item in parsed.name]
    name_confidences = [item.confidence for item in parsed.name]
    canonical_name = names[0] if names else parsed.sentence
    amounts = [_amount_to_dict(amount) for amount in parsed.amount]
    foundation_foods = [_foundation_food_to_dict(item) for item in parsed.foundation_foods]

    confidence_values = [v for v in name_confidences if isinstance(v, (float, int))]
    confidence_values.extend(
        [a["confidence"] for a in amounts if isinstance(a.get("confidence"), (float, int))]
    )
    parse_confidence = (
        round(sum(confidence_values) / len(confidence_values), 4)
        if confidence_values
        else None
    )

    return {
        "raw_text": raw_ingredient,
        "normalized_sentence": parsed.sentence,
        "canonical_name": canonical_name,
        "name_candidates": names,
        "preparation": parsed.preparation.text if parsed.preparation else None,
        "comment": parsed.comment.text if parsed.comment else None,
        "purpose": parsed.purpose.text if parsed.purpose else None,
        "size": parsed.size.text if parsed.size else None,
        "amounts": amounts,
        "primary_amount": amounts[0] if amounts else None,
        "fdc_candidates": foundation_foods,
        "fdc_best_match": foundation_foods[0] if foundation_foods else None,
        "usda_search_query": canonical_name,
        "parse_confidence": parse_confidence,
        "parse_success": True,
    }


def standardize_recipes(input_path: Path, output_path: Path) -> tuple[int, int]:
    recipes = json.loads(input_path.read_text(encoding="utf-8"))
    total_ingredients = 0
    parse_errors = 0

    for index, recipe in enumerate(recipes, start=1):
        standardized_ingredients = []

        for raw_ingredient in recipe.get("ingredients", []):
            total_ingredients += 1
            try:
                standardized_ingredients.append(standardize_ingredient(raw_ingredient))
            except Exception as error:
                parse_errors += 1
                standardized_ingredients.append(
                    {
                        "raw_text": raw_ingredient,
                        "normalized_sentence": raw_ingredient,
                        "canonical_name": raw_ingredient,
                        "name_candidates": [],
                        "preparation": None,
                        "comment": None,
                        "purpose": None,
                        "size": None,
                        "amounts": [],
                        "primary_amount": None,
                        "fdc_candidates": [],
                        "fdc_best_match": None,
                        "usda_search_query": raw_ingredient,
                        "parse_confidence": None,
                        "parse_success": False,
                        "parse_error": str(error),
                    }
                )

        recipe["standardized_ingredients"] = standardized_ingredients

        if index % 500 == 0:
            print(f"Przetworzono {index} przepisów...")

    output_path.write_text(
        json.dumps(recipes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return total_ingredients, parse_errors


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Standaryzacja składników do formatu pod USDA FoodData Central"
    )
    parser.add_argument(
        "--input",
        default="data/bbcgoodfood_recipes_clean.json",
        help="Ścieżka do wejściowego JSON z przepisami",
    )
    parser.add_argument(
        "--output",
        default="data/bbcgoodfood_recipes_standardized.json",
        help="Ścieżka do wyjściowego JSON z polem standardized_ingredients",
    )
    return parser


def main() -> None:
    parser = build_argument_parser()
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    total_ingredients, parse_errors = standardize_recipes(input_path, output_path)

    print("\nStandaryzacja zakończona")
    print(f"Input: {input_path}")
    print(f"Output: {output_path}")
    print(f"Liczba składników: {total_ingredients}")
    print(f"Błędy parsowania: {parse_errors}")


if __name__ == "__main__":
    main()