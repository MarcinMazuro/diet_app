from ingredient_parser import parse_ingredient
import json
import pandas as pd
from fractions import Fraction

def serialize_ingredient(obj):
    if hasattr(obj, '__dict__'):
        result = {}
        for key, value in obj.__dict__.items():
            if isinstance(value, list):
                result[key] = [serialize_ingredient(item) for item in value]
            elif isinstance(value, Fraction):
                result[key] = float(value)
            elif hasattr(value, '__dict__'):
                result[key] = serialize_ingredient(value)
            else:
                result[key] = str(value) if not isinstance(value, (str, int, float, bool, type(None))) else value
        return result
    elif isinstance(obj, list):
        return [serialize_ingredient(item) for item in obj]
    elif isinstance(obj, Fraction):
        return float(obj)
    else:
        return str(obj) if not isinstance(obj, (str, int, float, bool, type(None))) else obj



def parse_ingredients(recipes):
    parsed_ingredients = []
    id_counter = 0
    for ingredient_list in recipes["ingredients"]:
        id_counter += 1
        for ingredient in ingredient_list:
            try:
                parsed_ing = parse_ingredient(ingredient)
                parsed_ingredients.append({id_counter: serialize_ingredient(parsed_ing)})
                if id_counter % 1000 == 0:
                    print(f"Przetworzono {id_counter} list składników")
            except Exception as e:
                # Skip ingredients that cause parsing errors
                continue
    with open("/parsed_ingredients.json", "w") as file:
        json.dump(parsed_ingredients, file, indent=4)

def analyze_ingredients(json_file_path):
    with open(json_file_path, "r") as file:
        parsed_ingredients = json.load(file)

    unique_names = set()
    unique_sentences = set()

    for item in parsed_ingredients:
        for recipe_id, ingredient_data in item.items():
            if 'sentence' in ingredient_data:
                    unique_sentences.add(ingredient_data['sentence'].lower())
            if 'name' in ingredient_data and isinstance(ingredient_data['name'], list):
                for name_obj in ingredient_data['name']:
                    if isinstance(name_obj, dict) and 'text' in name_obj:
                        unique_names.add(name_obj['text'].lower())

    print(f"Number of unique ingrediens: {len(unique_names)}")
    print(f"Number of unique ingredient full names: {len(unique_sentences)}")

    print(f"Number of ingredients: {len(parsed_ingredients)}")

# recipes extract
import re
from math import ceil

DURATION_RE = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', re.I)
NUMBER_RE = re.compile(r'[-+]?\d*\.?\d+')

def parse_iso_duration_to_minutes(iso: str):
    if not iso or not isinstance(iso, str):
        return None
    m = DURATION_RE.match(iso.strip())
    if not m:
        return None
    hours = int(m.group(1)) if m.group(1) else 0
    minutes = int(m.group(2)) if m.group(2) else 0
    seconds = int(m.group(3)) if m.group(3) else 0
    total = hours * 60 + minutes + ceil(seconds / 60) if seconds else hours * 60 + minutes
    return total

def extract_first_image_url(images):
    if isinstance(images, list) and images:
        first = images[0]
        if isinstance(first, dict):
            url = first.get('url')
            return url.split('?')[0]
        return str(first)
    return None

def extract_number(value):
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, list) and value:
        value = value[0]
    if not isinstance(value, str):
        value = str(value)
    m = NUMBER_RE.search(value)
    return float(m.group(0)) if m else None

def join_if_list(field, sep=' | '):
    if field is None:
        return None
    if isinstance(field, list):
        return sep.join(str(x) for x in field)
    return str(field)

def process_recipes_to_df(recipes):
    """
    Input: list of recipe dicts
    Output: pandas.DataFrame with flattened columns:
      url, name, description, image_url, author, prep_minutes, cook_minutes, total_minutes,
      servings, calories, protein_g, fat_g, saturated_fat_g, fiber_g, sugar_g, sodium_mg,
      ingredients_text, instructions_text, keywords_text, category
    """
    rows = []
    for r in recipes:
        row = {}
        row['url'] = r.get('url')
        row['name'] = r.get('name')
        row['description'] = r.get('description')
        row['image_url'] = extract_first_image_url(r.get('image'))
        row['total_minutes'] = parse_iso_duration_to_minutes(r.get('total_time'))
        # servings -> int if possible
        serv = r.get('servings')
        try:
            row['servings'] = int(str(serv).strip()) if serv is not None and str(serv).strip().isdigit() else serv
        except Exception:
            row['servings'] = serv

        # nutrition: calories (int), protein/fat/... from lists or values
        row['calories'] = extract_number(r.get('calories'))
        row['protein'] = extract_number(r.get('protein'))
        row['fat'] = extract_number(r.get('fat'))
        row['saturated_fat'] = extract_number(r.get('saturated_fat'))
        row['fiber'] = extract_number(r.get('fiber'))
        row['sugar'] = extract_number(r.get('sugar'))
        row['sodium'] = extract_number(r.get('sodium'))

        row['ingredients'] = r.get('ingredients')
        row['instructions'] = r.get('instructions')

        categories = set()
        for key in ('category', 'cuisine'):
            vals = r.get(key, [])
            if isinstance(vals, str) and vals != '':
                vals = [v.strip() for v in vals.split(',')]
            for v in vals:
                if isinstance(v, str) and v:
                    categories.add(v.lower())
        row['categories'] = categories


        rows.append(row)


    df = pd.DataFrame(rows)
    # optional: cast some numeric columns to numeric dtype
    numeric_cols = ['prep_minutes', 'cook_minutes', 'total_minutes', 'servings',
                    'calories', 'protein_g', 'fat_g', 'saturated_fat_g', 'fiber_g', 'sugar_g', 'sodium']
    for c in numeric_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    return df


def print_categories(df):
    categories = set()
    for category in df['categories']:
        for c in category:
            categories.add(c)
    print(len(categories), "\n")
    print(categories)

def main():
   # recipes = select_recipes()
   # parse_ingredients(recipes)
   # analyze_ingredients("./archive_not_used/parsed_ingredients.json")
   with open("data/bbcgoodfood_full_recipes.json", "r") as file:
        df = process_recipes_to_df(json.load(file))
        df.dropna(inplace=True)
        print(len(df))
        print_categories(df)
   df.to_json("data/bbcgoodfood_recipes_clean.json",
              orient='records',
              indent=2,
              force_ascii=False)
if __name__ == "__main__":
    main()