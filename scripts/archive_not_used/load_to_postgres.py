import json
import psycopg2
from psycopg2.extras import execute_values


def load_filtered_recipes(file_path='filtered_recipes.json'):
    """Wczytuje dane z pliku JSON"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_desired_categories(file_path='archive_not_used/desired_categories.json'):
    """Wczytuje dozwolone kategorie z pliku JSON

    Returns:
        dict: Słownik {type: [categories]} oraz set wszystkich kategorii
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        categories_dict = json.load(f)

    return categories_dict


def get_all_categories_with_types(categories_dict):
    """Zwraca listę krotek (category_name, category_type)"""
    all_categories = []
    for category_type, category_list in categories_dict.items():
        for category in category_list:
            all_categories.append((category, category_type))
    return all_categories


def filter_categories(recipe_categories, categories_dict):
    """Filtruje kategorie przepisu - tylko te z desired_categories

    Args:
        recipe_categories: lista kategorii z przepisu
        categories_dict: słownik {type: [categories]} z desired_categories
    """
    if not isinstance(recipe_categories, list):
        return []

    # Zbierz wszystkie dozwolone kategorie z słownika (lowercase)
    all_allowed = set()
    for category_list in categories_dict.values():
        all_allowed.update([cat.lower() for cat in category_list])

    # Porównuj bez względu na wielkość liter
    return [cat for cat in recipe_categories if cat.lower() in all_allowed]


def prepare_recipes_for_db(filtered_recipes):
    """
    Przygotowuje dane z filtered_recipes do formatu zgodnego z tabelą Recipes
    """
    prepared_data = []

    for recipe in filtered_recipes:
        recipe_data = (
            recipe.get('title'),
            recipe.get('desc'),
            recipe.get('rating'),
            recipe.get('directions', []),
            recipe.get('calories'),
            recipe.get('fat'),
            recipe.get('carbohydrates'),
            recipe.get('protein'),
            recipe.get('sodium')
        )
        prepared_data.append(recipe_data)

    return prepared_data


def insert_categories(cursor, categories_with_types):
    """Wstawia kategorie z typami i zwraca mapowanie nazwa_lowercase->id

    Args:
        categories_with_types: lista krotek (category_name, category_type)

    Returns:
        dict: mapowanie {category_name_lowercase: category_id}
    """
    category_map = {}

    for category, category_type in categories_with_types:
        cursor.execute(
            'INSERT INTO "Categories" (name, type) VALUES (%s, %s) ON CONFLICT (name) DO UPDATE SET type = EXCLUDED.type RETURNING id',
            (category, category_type)
        )
        category_id = cursor.fetchone()[0]
        # Używaj lowercase jako klucza w mapowaniu
        category_map[category.lower()] = category_id

    return category_map


def insert_recipe_categories(cursor, recipe_id, categories, category_map):
    """Wstawia powiązania przepis-kategoria

    Args:
        cursor: cursor bazy danych
        recipe_id: ID przepisu
        categories: lista kategorii z przepisu (mogą być z wielkimi literami)
        category_map: mapowanie nazwa_lowercase -> category_id
    """
    if not categories:
        return

    # Mapuj kategorie do ID używając lowercase
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


def populate_categories_from_desired(conn_params):
    """
    Wstawia wszystkie kategorie z desired_categories.json do tabeli Categories
    """
    categories_dict = load_desired_categories('desired_categories.json')
    categories_with_types = get_all_categories_with_types(categories_dict)
    print(f"Wczytano {len(categories_with_types)} kategorii z desired_categories.json")

    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    try:
        category_map = insert_categories(cursor, categories_with_types)
        conn.commit()
        print(f"Wstawiono {len(category_map)} kategorii do tabeli Categories")
        return category_map
    except Exception as e:
        conn.rollback()
        print(f"Błąd podczas wstawiania kategorii: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


def insert_recipes_to_db(filtered_recipes, conn_params):
    """
    Wgrywa przepisy z kategoriami do bazy danych PostgreSQL
    """
    # Wczytaj kategorie z desired_categories.json
    categories_dict = load_desired_categories('desired_categories.json')
    categories_with_types = get_all_categories_with_types(categories_dict)

    prepared_data = prepare_recipes_for_db(filtered_recipes)

    conn = psycopg2.connect(**conn_params)
    cursor = conn.cursor()

    try:
        # Wstaw wszystkie kategorie z desired_categories.json do tabeli Categories
        category_map = insert_categories(cursor, categories_with_types)
        print(f"Wstawiono {len(category_map)} kategorii do tabeli Categories")

        # Wstaw przepisy i połącz z kategoriami
        skipped_categories = 0
        total_links = 0

        for i, recipe_tuple in enumerate(prepared_data):
            cursor.execute(
                """
                INSERT INTO "Recipes"
                (name, description, rating, directions, calories, fat, carbohydrates, protein, sodium)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """,
                recipe_tuple
            )
            recipe_id = cursor.fetchone()[0]

            # Przefiltruj kategorie przepisu - tylko te które są w desired_categories
            recipe_categories = filtered_recipes[i].get('categories', [])
            filtered_cats = filter_categories(recipe_categories, categories_dict)

            skipped = len(recipe_categories) - len(filtered_cats)
            skipped_categories += skipped
            total_links += len(filtered_cats)

            # Połącz przepis z kategoriami w tabeli Recipes_Categories
            insert_recipe_categories(cursor, recipe_id, filtered_cats, category_map)

        conn.commit()
        print(f"Wgrano {len(prepared_data)} przepisów do bazy danych")
        print(f"Utworzono {total_links} połączeń przepis-kategoria w tabeli Recipes_Categories")
        print(f"Pominięto {skipped_categories} kategorii spoza desired_categories.json")
    except Exception as e:
        conn.rollback()
        print(f"Błąd podczas wgrywania danych: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    filtered_recipes = load_filtered_recipes('filtered_recipes.json')

    conn_params = {
        'host': 'localhost',
        'database': '',
        'user': '',
        'password': ''
    }

    insert_recipes_to_db(filtered_recipes, conn_params)
