"""
Showcase: AI-Driven Recommendation Engine

Demonstrates how the multi-stage pipeline personalises meal recommendations
for three distinct user profiles over four consecutive days.

Run from the backend/ directory:
    python recommendations/management/showcase.py

All database writes are rolled back at the end — the real DB is untouched.
"""
import os
import sys
import datetime

# ── Django bootstrap ──────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

import django
django.setup()

# ── Imports (after setup) ─────────────────────────────────────────────────────
# noqa: E402 — intentionally after django.setup()
from django.db import transaction  # noqa: E402
from django.contrib.auth import get_user_model  # noqa: E402

from profiles.models import Profile  # noqa: E402
from recipes.models import Recipe  # noqa: E402
from recommendations.models import Meal, Rating, MealType, MealSource  # noqa: E402
from recommendations.services.recommender_engine import RecommenderEngine  # noqa: E402
from recommendations.services.recipe_scorer import RecipeScorer, W_MACRO, W_PREF, W_DIV  # noqa: E402
from recommendations.services.user_context import UserContext  # noqa: E402
from recommendations.services.feature_builder import invalidate_cache  # noqa: E402

User = get_user_model()

# ── Visual helpers ────────────────────────────────────────────────────────────
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
DIM    = "\033[2m"
RESET  = "\033[0m"
RED    = "\033[91m"

def _bar(value, width=20):
    filled = round(value * width)
    return f"{'█' * filled}{'░' * (width - filled)}"

def _section(title, color=CYAN):
    width = 72
    print(f"\n{color}{BOLD}{'─' * width}{RESET}")
    print(f"{color}{BOLD}  {title}{RESET}")
    print(f"{color}{BOLD}{'─' * width}{RESET}")

def _header(title):
    print(f"\n{BOLD}{YELLOW}{'═' * 72}{RESET}")
    print(f"{BOLD}{YELLOW}  {title}{RESET}")
    print(f"{BOLD}{YELLOW}{'═' * 72}{RESET}\n")


# ── Profile factory ───────────────────────────────────────────────────────────

def _make_profile(username, gender, dob, weight, height, goal, activity, calories, protein, carbs, fat):
    """Create a temporary User + Profile without triggering the auto-save signal's side effects."""
    user = User.objects.create_user(
        username=username,
        email=f"{username}@showcase.local",
        password="showcase",
    )
    p = user.profile
    p.gender      = gender
    p.date_of_birth = dob
    p.weight      = weight
    p.height      = height
    p.nutritional_goal  = goal
    p.physical_activity = activity
    # Pre-computed macro targets (approximate Mifflin-St Jeor + goal adjustment)
    p.daily_calories     = calories
    p.daily_protein      = protein
    p.daily_carbohydrates = carbs
    p.daily_fat          = fat
    p.save()
    return p


# ── Rating helper ─────────────────────────────────────────────────────────────

def _seed_ratings(profiles_recipes):
    """
    profiles_recipes: list of (profile, [(recipe, rating_int), ...])
    Last rating wins when the same recipe appears twice (loves vs dislikes overlap).
    """
    for profile, ratings in profiles_recipes:
        # Deduplicate: last entry per recipe wins
        deduped = {}
        for recipe, stars in ratings:
            deduped[recipe.id] = (recipe, stars)
        for recipe, stars in deduped.values():
            Rating.objects.update_or_create(
                profile=profile,
                recipe=recipe,
                defaults={"rating": stars},
            )


# ── Recommendation runner ─────────────────────────────────────────────────────

def _plan_day(engine, profile, date):
    """Run all four meal slots and record Meal objects. Returns dict slot→recipe."""
    planned = []
    plan = {}
    for slot in [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER, MealType.SNACK]:
        recipe = engine.find_best_recipe(
            profile=profile,
            meal_type=slot,
            date=date,
            already_planned=planned,
        )
        if recipe:
            Meal.objects.update_or_create(
                profile=profile,
                date=date,
                meal_type=slot,
                defaults={"recipe": recipe, "source": MealSource.AI_GENERATED},
            )
            planned.append(recipe)
        plan[slot] = recipe
    return plan


def _score_breakdown(engine, profile, recipe, meal_type, date):
    """Return (total, s_macro, s_pref, s_div) for a single recipe."""
    context = UserContext.from_profile(profile, date)
    feature_cache = engine._get_feature_cache()
    scorer = RecipeScorer(feature_cache=feature_cache)
    s_macro = scorer.macro_score(recipe, profile, meal_type)
    s_pref  = scorer.preference_score(recipe, context)
    s_div   = scorer.diversity_score(recipe, context, [], date)
    total   = W_MACRO * s_macro + W_PREF * s_pref + W_DIV * s_div
    return total, s_macro, s_pref, s_div


# ── Pretty print helpers ──────────────────────────────────────────────────────

def _print_profile_row(label, profile):
    goal_map = {"LOSE": "Lose Weight", "GAIN": "Gain Weight", "MAINTAIN": "Maintain"}
    goal_colors = {"LOSE": RED, "GAIN": GREEN, "MAINTAIN": CYAN}
    goal = profile.nutritional_goal or "N/A"
    goal_str = f"{goal_colors.get(goal, RESET)}{goal_map.get(goal, goal)}{RESET}"

    print(
        f"  {BOLD}{label:<14}{RESET}"
        f"  {goal_str:<30}"
        f"  {BOLD}{profile.daily_calories:.0f} kcal{RESET}"
        f"  {DIM}{profile.weight} kg  {profile.height} cm{RESET}"
    )


def _print_recipe_row(slot, recipe, engine, profile, date):
    if recipe is None:
        print(f"    {DIM}{slot:<10}  — no match found{RESET}")
        return

    total, s_macro, s_pref, s_div = _score_breakdown(engine, profile, recipe, slot, date)

    name = recipe.name[:38].ljust(38)
    kcal = f"{recipe.calories:.0f} kcal"
    macros = (
        f"P:{recipe.protein:.0f}g "
        f"C:{recipe.carbohydrate:.0f}g "
        f"F:{recipe.fat:.0f}g"
    )
    bar = _bar(total)
    score_str = f"{total:.2f}  [{bar}]"

    print(f"    {CYAN}{slot:<10}{RESET}  {BOLD}{name}{RESET}")
    print(
        f"               {DIM}{kcal:<12}{macros:<28}{RESET}"
        f"  score {GREEN}{score_str}{RESET}"
    )
    print(
        f"               {DIM}macro {s_macro:.2f}  pref {s_pref:.2f}  div {s_div:.2f}{RESET}"
    )


def _print_day(day_num, date, plans, engine, profiles):
    _section(f"DAY {day_num}  —  {date.strftime('%A, %d %b %Y')}", MAGENTA)
    for label, profile in profiles:
        print(f"\n  {BOLD}{YELLOW}{label}{RESET}  "
              f"{DIM}(goal: {profile.nutritional_goal}){RESET}")
        for slot in [MealType.BREAKFAST, MealType.LUNCH, MealType.DINNER, MealType.SNACK]:
            recipe = plans[label].get(slot)
            _print_recipe_row(slot, recipe, engine, profile, date)


# ── Main showcase ─────────────────────────────────────────────────────────────

def run():
    TODAY = datetime.date(2026, 5, 11)
    DAYS  = [TODAY - datetime.timedelta(days=3 - i) for i in range(4)]
    # DAYS = [May 8, May 9, May 10, May 11]

    _header("AI RECOMMENDATION ENGINE — 4-DAY SHOWCASE")

    # ── Check recipe data ──────────────────────────────────────────────────────
    recipe_count = Recipe.objects.count()
    if recipe_count == 0:
        print(f"{RED}  ERROR: No recipes in the database.{RESET}")
        print("  Run:  python manage.py load_recipes")
        return

    print(f"  {DIM}Database: {recipe_count} recipes loaded{RESET}\n")

    # ── Wrap in atomic block, force rollback at the end — DB stays clean ──────
    try:
        with transaction.atomic():
            _run_showcase(DAYS)
            transaction.set_rollback(True)
    finally:
        invalidate_cache()
        print(f"\n{DIM}  [All showcase data rolled back — database unchanged]{RESET}\n")


def _run_showcase(days):
    # ── Create profiles ────────────────────────────────────────────────────────
    _section("PROFILES")

    alice = _make_profile(
        "alice_showcase", "F",
        datetime.date(1997, 4, 15),
        weight=58, height=165,
        goal=Profile.NutritionalGoal.LOSE_WEIGHT,
        activity=Profile.PhysicalActivity.MODERATE,
        calories=1620, protein=130, carbs=150, fat=52,
    )

    bob = _make_profile(
        "bob_showcase", "M",
        datetime.date(1999, 8, 20),
        weight=88, height=183,
        goal=Profile.NutritionalGoal.GAIN_WEIGHT,
        activity=Profile.PhysicalActivity.HIGH,
        calories=3150, protein=175, carbs=390, fat=88,
    )

    carol = _make_profile(
        "carol_showcase", "M",
        datetime.date(1991, 11, 3),
        weight=74, height=178,
        goal=Profile.NutritionalGoal.MAINTAIN_WEIGHT,
        activity=Profile.PhysicalActivity.MODERATE,
        calories=2380, protein=148, carbs=270, fat=72,
    )

    profiles = [
        ("Alice",  alice),
        ("Bob",    bob),
        ("Carol",  carol),
    ]

    for label, p in profiles:
        _print_profile_row(label, p)

    # ── Seed ratings ───────────────────────────────────────────────────────────
    _section("MOCK RATINGS")

    # Query real recipes and bucket them by macro profile
    all_recipes = list(Recipe.objects.all()[:200])

    # Classify by protein density (protein / calories)
    def protein_density(r):
        return float(r.protein or 0) / max(float(r.calories or 1), 1)

    def calorie_density(r):
        return float(r.calories or 0)

    def carb_density(r):
        return float(r.carbohydrate or 0) / max(float(r.calories or 1), 1)

    sorted_by_protein = sorted(all_recipes, key=protein_density, reverse=True)
    sorted_by_calories = sorted(all_recipes, key=calorie_density, reverse=True)
    sorted_by_carbs = sorted(all_recipes, key=carb_density, reverse=True)

    # Alice: loves high-protein, low-cal recipes; dislikes heavy carb dishes
    alice_loves  = sorted_by_protein[:6]                # lean protein
    alice_dislikes = sorted_by_carbs[:3]                # carb-heavy → rated 1-2

    # Bob: loves high-calorie, high-protein (bulking); dislikes tiny snacks
    bob_loves    = sorted_by_calories[:4]               # calorie-dense
    bob_loves   += sorted_by_protein[:3]                # also protein-dense
    bob_dislikes = sorted(all_recipes, key=calorie_density)[:3]  # low-cal

    # Carol: rates balanced, moderate-calorie recipes highly
    mid_cal = sorted(all_recipes, key=lambda r: abs(float(r.calories or 0) - 600))
    carol_loves  = mid_cal[:6]
    carol_dislikes = sorted_by_calories[:2]             # too calorie-dense

    alice_ratings = [(r, 5) for r in alice_loves] + [(r, 2) for r in alice_dislikes]
    bob_ratings   = [(r, 5) for r in bob_loves]   + [(r, 1) for r in bob_dislikes]
    carol_ratings = [(r, 5) for r in carol_loves] + [(r, 2) for r in carol_dislikes]

    _seed_ratings([
        (alice, alice_ratings),
        (bob,   bob_ratings),
        (carol, carol_ratings),
    ])

    def _summarise_ratings(label, loves, dislikes):
        print(f"  {BOLD}{label:<8}{RESET}", end="")
        print(f"  {GREEN}Liked{RESET}  ({len(loves)} recipes): "
              f"{', '.join(r.name[:22] for r in loves[:3])}{'…' if len(loves) > 3 else ''}")
        print(f"          {RED}Disliked{RESET} ({len(dislikes)} recipes): "
              f"{', '.join(r.name[:22] for r in dislikes[:3])}")

    _summarise_ratings("Alice",  alice_loves,   alice_dislikes)
    print()
    _summarise_ratings("Bob",    bob_loves,     bob_dislikes)
    print()
    _summarise_ratings("Carol",  carol_loves,   carol_dislikes)

    # ── Run 4-day simulation ───────────────────────────────────────────────────
    _section("4-DAY RECOMMENDATION SIMULATION")

    engine = RecommenderEngine()
    all_day_plans = []  # list of {label: {slot: recipe}} per day

    for day_num, date in enumerate(days, start=1):
        day_result = {}
        for label, profile in profiles:
            # Invalidate feature cache between users so context is fresh
            day_result[label] = _plan_day(engine, profile, date)
        all_day_plans.append((day_num, date, day_result))

    for day_num, date, plans in all_day_plans:
        _print_day(day_num, date, plans, engine, profiles)

    # ── Personalisation summary ────────────────────────────────────────────────
    _section("PERSONALISATION DIVERGENCE SUMMARY", CYAN)

    print(
        f"  This table shows the {BOLD}preference score (S_pref){RESET} for each user on Day 4."
    )
    print(
        f"  {DIM}S_pref = cosine similarity(candidate, rating-weighted taste centroid).{RESET}"
    )
    print(
        f"  {DIM}A higher spread between users on the same recipe = stronger personalisation.{RESET}\n"
    )

    # Pick the Day-4 breakfast recipes for each user and compute cross-scores
    _, day4_date, day4_plans = all_day_plans[-1]
    context_a = UserContext.from_profile(alice, day4_date)
    context_b = UserContext.from_profile(bob,   day4_date)
    context_c = UserContext.from_profile(carol, day4_date)

    feature_cache = engine._get_feature_cache()
    scorer = RecipeScorer(feature_cache=feature_cache)

    print(f"  {'Recipe':<42}  {'Alice S_pref':>12}  {'Bob S_pref':>10}  {'Carol S_pref':>12}")
    print(f"  {'─' * 42}  {'─' * 12}  {'─' * 10}  {'─' * 12}")

    seen = set()
    for label, profile in profiles:
        recipe = day4_plans[label].get(MealType.BREAKFAST)
        if recipe and recipe.id not in seen:
            seen.add(recipe.id)
            sa = scorer.preference_score(recipe, context_a)
            sb = scorer.preference_score(recipe, context_b)
            sc = scorer.preference_score(recipe, context_c)
            spread = max(sa, sb, sc) - min(sa, sb, sc)
            spread_bar = _bar(spread, width=10)
            print(
                f"  {recipe.name[:40]:<42}"
                f"  {sa:>12.3f}"
                f"  {sb:>10.3f}"
                f"  {sc:>12.3f}"
                f"  {DIM}spread {spread_bar}{RESET}"
            )

    # ── Recency effect ─────────────────────────────────────────────────────────
    _section("RECENCY EFFECT — Alice's Day 1 breakfasts vs Day 4", CYAN)
    print(
        f"  Recipes eaten in the last 5 days are excluded (hard constraint).\n"
        f"  The diversity score {BOLD}S_div{RESET} decays exponentially for recently-eaten meals:\n"
        f"  {DIM}S_div = (1 − exp(−days_since / 3))  ×  (1 − 0.5 × ingredient_overlap){RESET}\n"
    )

    alice_context_day4 = UserContext.from_profile(alice, day4_date)
    seen_names = set()
    for day_num, date, plans in all_day_plans:
        recipe = plans["Alice"].get(MealType.BREAKFAST)
        if recipe is None:
            continue
        days_since = (day4_date - date).days
        s_div = scorer.diversity_score(recipe, alice_context_day4, [], day4_date)
        recency_note = (
            f"{GREEN}fresh (not in recency window){RESET}"
            if days_since > 5
            else f"{YELLOW}within recency window → excluded next cycle{RESET}"
        )
        flag = " ←" if recipe.name in seen_names else ""
        seen_names.add(recipe.name)
        print(
            f"  Day {day_num} ({date})  {recipe.name[:35]:<35}"
            f"  {days_since} days ago  S_div={s_div:.3f}  {recency_note}{flag}"
        )


if __name__ == "__main__":
    run()
