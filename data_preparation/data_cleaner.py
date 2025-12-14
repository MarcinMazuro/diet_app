import json
import pandas as pd
import re
from math import ceil

DURATION_RE = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', re.I)
NUMBER_RE = re.compile(r'[-+]?\d*\.?\d+')

DISH_TYPES = ["afternoon tea",
    "breakfast",
    "brunch",
    "buffet",
    "dinner",
    "fish course",
    "lunch",
    "main course",
    "picnic",
    "starter",
    "supper"]

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

def filter_keywords(recipe):
    keywords = set()
    vals = recipe.get('keywords', [])
    if isinstance(vals, str) and vals != '':
        vals = [v.strip() for v in vals.split(',')]
    for v in vals:
        if isinstance(v, str) and v:
            if "vegan" in v.lower():
                print(v + " -> vegan")
                keywords.add("vegan")
            if "vegetarian" in v.lower():
                print(v + " -> vegetarian")
                keywords.add("vegetarian")
            if "gluten" in v.lower():
                print(v + " -> gluten")
                keywords.add("gluten-free")
            if "protein" in v.lower():
                print(v + " -> high-protein")
                keywords.add("high-protein")
            if "low carb" in v.lower() or "low-carbohydrate" in v.lower():
                print(v + " -> low-carbohydrate")
                keywords.add("low-carbohydrate")
            if "keto" in v.lower():
                print(v + " -> keto")
                keywords.add("keto")
            if "low fat" in v.lower() or "low-fat" in v.lower():
                print(v + " -> low-fat")
                keywords.add("low-fat")
    return keywords

def has_dish_type(categories):
    for dt in DISH_TYPES:
        if dt in categories:
            return True
    return False

def print_stats(df):

    print(df.head())
    print("Recipes: ", len(df))

    dinner_mask = df['categories'].astype(str).str.contains("dinner", case=False, na=False, regex=False)
    breakfast_mask = df['categories'].astype(str).str.contains("breakfast", case=False, na=False, regex=False)
    lunch_mask = df['categories'].astype(str).str.contains("lunch", case=False)
    snack_mask = df['categories'].astype(str).str.contains("snack", case=False)

    print("dinner count ", dinner_mask.sum())
    print("breakfast count ", breakfast_mask.sum())
    print("lunch count ", lunch_mask.sum())
    print("snack count ", snack_mask.sum())

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
        row['carbohydrate'] = extract_number(r.get('carbohydrate'))
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

        filtered_keywords = filter_keywords(r)
        categories.update(filtered_keywords)
        row['categories'] = categories

        if has_dish_type(row['categories']):
            rows.append(row)


    df = pd.DataFrame(rows)
    # optional: cast some numeric columns to numeric dtype
    numeric_cols = ['prep_minutes', 'cook_minutes', 'total_minutes', 'servings',
                    'calories', 'protein', 'fat', 'saturated_fat', 'fiber', 'sugar','carbohydrate', 'sodium']
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
 #   print(categories)

def main():
   # recipes = select_recipes()
   # parse_ingredients(recipes)
   # analyze_ingredients("./archive/parsed_ingredients.json")
   with open("data/bbcgoodfood_full_recipes.json", "r") as file:
        df = process_recipes_to_df(json.load(file))
        df.dropna(inplace=True)
        print_stats(df)

   df.to_json("data/bbcgoodfood_recipes_clean.json",
              orient='records',
              indent=2,
              force_ascii=False)
if __name__ == "__main__":
    main()