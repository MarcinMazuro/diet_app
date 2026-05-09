import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

STANDARDIZED_PATH = Path(__file__).parent / "data" / "bbcgoodfood_recipes_standardized.json"
OUTPUT_PATH = Path(__file__).parent / "data" / "fdc_nutrients.json"
FDC_API_BASE = "https://api.nal.usda.gov/fdc/v1"
BATCH_SIZE = 20
REQUEST_DELAY = 0.1  # seconds between requests


def extract_unique_fdc_ids(standardized_path: Path) -> list[int]:
    print(f"Reading {standardized_path}...")
    with open(standardized_path, encoding="utf-8") as f:
        recipes = json.load(f)

    fdc_ids = set()
    for recipe in recipes:
        for ing in recipe.get("standardized_ingredients", []):
            match = ing.get("fdc_best_match")
            if match and match.get("fdc_id"):
                fdc_ids.add(int(match["fdc_id"]))

    print(f"Found {len(fdc_ids)} unique FDC IDs across {len(recipes)} recipes")
    return sorted(fdc_ids)


def load_existing_cache(output_path: Path) -> dict:
    if output_path.exists():
        with open(output_path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def fetch_batch(fdc_ids: list[int], api_key: str) -> dict:
    ids_param = ",".join(str(i) for i in fdc_ids)
    url = f"{FDC_API_BASE}/foods"
    params = {"fdcIds": ids_param, "format": "abridged", "api_key": api_key}

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def parse_foods_response(foods: list) -> dict:
    result = {}
    for food in foods:
        fdc_id = str(food.get("fdcId"))
        if not fdc_id:
            continue
        nutrients = [
            {
                "id": n["number"],
                "name": n.get("name"),
                "unit": n.get("unitName"),
                "value": n.get("amount"),
            }
            for n in food.get("foodNutrients", [])
            if n.get("amount") is not None and n.get("number")
        ]
        result[fdc_id] = {
            "description": food.get("description"),
            "data_type": food.get("dataType"),
            "nutrients": nutrients,
        }
    return result


def save_cache(cache: dict, output_path: Path) -> None:
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def fetch_all_nutrients(fdc_ids: list[int], api_key: str, output_path: Path) -> dict:
    cache = load_existing_cache(output_path)

    ids_to_fetch = [i for i in fdc_ids if str(i) not in cache]
    print(f"Already cached: {len(cache)}, to fetch: {len(ids_to_fetch)}")

    if not ids_to_fetch:
        print("All IDs already cached.")
        return cache

    batches = [ids_to_fetch[i:i + BATCH_SIZE] for i in range(0, len(ids_to_fetch), BATCH_SIZE)]
    total_batches = len(batches)

    for batch_num, batch in enumerate(batches, 1):
        print(f"  Batch {batch_num}/{total_batches} ({len(batch)} IDs)...", end=" ", flush=True)
        try:
            foods = fetch_batch(batch, api_key)
            parsed = parse_foods_response(foods)
            cache.update(parsed)
            print(f"OK ({len(parsed)} returned)")
        except requests.HTTPError as e:
            print(f"HTTP ERROR {e.response.status_code}: {e}")
            if e.response.status_code == 429:
                print("Rate limited — waiting 60s...")
                time.sleep(60)
        except requests.RequestException as e:
            print(f"ERROR: {e}")

        if batch_num % 10 == 0:
            save_cache(cache, output_path)
            print(f"  Saved cache ({len(cache)} entries)")

        time.sleep(REQUEST_DELAY)

    save_cache(cache, output_path)
    return cache


def main():
    api_key = os.getenv("FDC_API_KEY")
    if not api_key:
        raise SystemExit(
            "FDC_API_KEY not set. Add it to .env or pass as env var.\n"
            "Get a free key at: https://fdc.nal.usda.gov/api-key-signup.html"
        )

    fdc_ids = extract_unique_fdc_ids(STANDARDIZED_PATH)
    cache = fetch_all_nutrients(fdc_ids, api_key, OUTPUT_PATH)

    print(f"\nDone. {len(cache)} FDC entries saved to {OUTPUT_PATH}")

    # Summary of nutrients available
    all_nutrient_names = set()
    for entry in cache.values():
        for n in entry.get("nutrients", []):
            if n.get("name"):
                all_nutrient_names.add(n["name"])
    print(f"Unique nutrient types: {len(all_nutrient_names)}")
    print("Sample nutrients:", sorted(all_nutrient_names)[:10])


if __name__ == "__main__":
    main()
