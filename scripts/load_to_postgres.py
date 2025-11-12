import json
import psycopg2
from psycopg2.extras import execute_values


def load_filtered_recipes(file_path='data/bbcgoodfood_recipes_clean.json'):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_desired_categories(file_path='data/categories.json'):
    with open(file_path, 'r', encoding='utf-8') as f:
        categories_dict = json.load(f)

    return categories_dict


def get_all_categories_with_types(categories_dict):
    """Returns a list of tuples (category_name, category_type)"""
    all_categories = []
    for category_type, category_list in categories_dict.items():
        for category in category_list:
            all_categories.append((category, category_type))
    return all_categories

def prepare_recipes_for_db(filtered_recipes):
    """
    Prepares data from bbcgoodfood_recipes_clean.json to match the Recipes table format
    """
    prepared_data = []

    for recipe in filtered_recipes:
        recipe_data = (
            recipe.get('name'),                    # name
            recipe.get('url'),                     # source
            recipe.get('description'),              # description
            recipe.get('instructions', []),         # directions
            recipe.get('servings'),                 # servings
            recipe.get('total_minutes'),            # preparation_time
            recipe.get('fiber'),                    # fiber
            recipe.get('calories'),                 # calories
            recipe.get('fat'),                      # fat
            recipe.get('saturated_fat'),            # saturated_fat
            recipe.get('sugar'),                  # carbohydrates
            recipe.get('protein'),                  # protein
            recipe.get('sodium'),                   # sodium
            recipe.get('image_url')                 # image_url
        )
        prepared_data.append(recipe_data)

    return prepared_data


def insert_categories(cursor, categories_with_types):
    """Inserts categories with types and returns mapping name_lowercase->id

    Args:
        categories_with_types: list of tuples (category_name, category_type)

    Returns:
        dict: mapping {category_name_lowercase: category_id}
    """
    category_map = {}

    for category, category_type in categories_with_types:
        cursor.execute(
            'INSERT INTO "Categories" (name, type) VALUES (%s, %s) ON CONFLICT (name) DO UPDATE SET type = EXCLUDED.type RETURNING id',
            (category, category_type)
        )
        category_id = cursor.fetchone()[0]
        # Use lowercase as key in mapping
        category_map[category.lower()] = category_id

    return category_map


def insert_recipe_categories(cursor, recipe_id, categories, category_map):
    """Inserts recipe-category associations

    Args:
        cursor: database cursor
        recipe_id: recipe ID
        categories: list of categories from recipe (may contain uppercase letters)
        category_map: mapping name_lowercase -> category_id
    """
    if not categories:
        return

    # Map categories to IDs using lowercase
    data = []
    for cat in categories:
        cat_lower = cat.lower()
        if cat_lower in category_map:
            data.append((recipe_id, category_map[cat_lower]))

    if data:
        execute_values(
            cursor,
            'INSERT INTO "Recipes_Categories" (recipe_id, category_id) VALUES %s ON CONFLICT DO NOTHING',
            data
        )


def insert_recipes(filtered_recipes, conn_params):
    """
    Uploads recipes with categories to PostgreSQL database
    """
    # Load categories from categories.json
    categories_dict = load_desired_categories('data/categories.json')
    categories_with_types = get_all_categories_with_types(categories_dict)

    prepared_data = prepare_recipes_for_db(filtered_recipes)

    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    try:
        # Insert all categories from categories.json to Categories table
        category_map = insert_categories(cursor, categories_with_types)
        print(f"Inserted {len(category_map)} categories into Categories table")

        # Insert recipes and link with categories
        skipped_categories = 0
        total_links = 0

        for i, recipe_tuple in enumerate(prepared_data):
            cursor.execute(
                """
                INSERT INTO "Recipes"
                (name, source, description, directions, servings, preparation_time, fiber, 
                 calories, fat, saturated_fat, carbohydrates, protein, sodium, image_url)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """,
                recipe_tuple
            )
            recipe_id = cursor.fetchone()[0]

            recipe_categories = filtered_recipes[i].get('categories', [])

            total_links += len(recipe_categories)

            # Link recipe with categories in Recipes_Categories table
            insert_recipe_categories(cursor, recipe_id, recipe_categories, category_map)

        conn.commit()
        print(f"Uploaded {len(prepared_data)} recipes to database")
        print(f"Created {total_links} recipe-category links in Recipes_Categories table")
    except Exception as e:
        conn.rollback()
        print(f"Error during data upload: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    filtered_recipes = load_filtered_recipes('data/bbcgoodfood_recipes_clean.json')

    conn_params = {
        'host': 'localhost',
        'database': '',
        'user': '',
        'password': ''
    }

    insert_recipes(filtered_recipes, conn_params)
