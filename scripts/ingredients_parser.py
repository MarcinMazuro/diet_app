from fractions import Fraction
from ingredient_parser import parse_ingredient
import json
import pandas as pd
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
    with open("data/parsed_ingredients.json", "w") as file:
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



def main():
   # recipes = select_recipes()

   with open("data/bbcgoodfood_recipes_clean.json", "r") as file:
        recipes = pd.read_json(file)
        recipes.dropna(inplace=True)
        print(len(recipes))
        parse_ingredients(recipes)
        #analyze_ingredients("data/parsed_ingredients.json")


if __name__ == "__main__":
    main()