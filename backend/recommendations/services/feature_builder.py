import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler

from recipes.models import Recipe


# Module-level cache; populated lazily on first call to build_matrix().
_CACHE: dict[int, np.ndarray] | None = None

MACRO_FIELDS = ['calories', 'protein', 'carbohydrate', 'fat', 'fiber', 'sodium', 'preparation_time']
MAX_TFIDF_FEATURES = 200


def build_matrix() -> dict[int, np.ndarray]:
    """
    Build (or return cached) a feature vector for every recipe.

    Vector layout:
        [normalized_macros..., cuisine_one_hot..., diet_one_hot..., ingredient_tfidf...]

    Returns dict: recipe_id → np.ndarray (float32, shape [D])
    """
    global _CACHE
    if _CACHE is not None:
        return _CACHE

    recipes = list(
        Recipe.objects.prefetch_related('categories', 'structured_ingredients__ingredient')
        .only(*MACRO_FIELDS, 'id', 'name')
        .all()
    )

    if not recipes:
        _CACHE = {}
        return _CACHE

    # ── Macro features ────────────────────────────────────────────────────────
    macro_matrix = np.array(
        [[float(getattr(r, f) or 0) for f in MACRO_FIELDS] for r in recipes],
        dtype=np.float32,
    )
    scaler = StandardScaler()
    macro_matrix = scaler.fit_transform(macro_matrix).astype(np.float32)

    # ── Category one-hot (cuisine + diet) ─────────────────────────────────────
    all_cuisines: set[str] = set()
    all_diets: set[str] = set()
    recipe_categories: dict[int, tuple[set, set]] = {}

    for r in recipes:
        cuisines, diets = set(), set()
        for cat in r.categories.all():
            if cat.type == 'cuisine':
                all_cuisines.add(cat.name)
                cuisines.add(cat.name)
            elif cat.type == 'diet':
                all_diets.add(cat.name)
                diets.add(cat.name)
        recipe_categories[r.id] = (cuisines, diets)

    cuisine_index = {name: i for i, name in enumerate(sorted(all_cuisines))}
    diet_index = {name: i for i, name in enumerate(sorted(all_diets))}
    n_cuisines = len(cuisine_index)
    n_diets = len(diet_index)

    category_matrix = np.zeros((len(recipes), n_cuisines + n_diets), dtype=np.float32)
    for row, r in enumerate(recipes):
        cuisines, diets = recipe_categories[r.id]
        for c in cuisines:
            category_matrix[row, cuisine_index[c]] = 1.0
        for d in diets:
            category_matrix[row, n_cuisines + diet_index[d]] = 1.0

    # ── Ingredient TF-IDF ─────────────────────────────────────────────────────
    ingredient_docs = []
    for r in recipes:
        names = [
            ri.ingredient.canonical_name
            for ri in r.structured_ingredients.all()
            if ri.ingredient_id
        ]
        ingredient_docs.append(' '.join(names) if names else '')

    if any(ingredient_docs):
        vectorizer = TfidfVectorizer(max_features=MAX_TFIDF_FEATURES)
        tfidf_matrix = vectorizer.fit_transform(ingredient_docs).toarray().astype(np.float32)
    else:
        tfidf_matrix = np.zeros((len(recipes), 1), dtype=np.float32)

    # ── Concatenate and cache ─────────────────────────────────────────────────
    full_matrix = np.concatenate([macro_matrix, category_matrix, tfidf_matrix], axis=1)

    _CACHE = {r.id: full_matrix[i] for i, r in enumerate(recipes)}
    return _CACHE


def invalidate_cache() -> None:
    """Call after bulk recipe updates to force a rebuild on next request."""
    global _CACHE
    _CACHE = None
