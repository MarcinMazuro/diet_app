from recipes.models import Recipe
from .recipe_scorer import _ingredient_overlap

# Ingredient Jaccard threshold above which a candidate is skipped in favour of the next
OVERLAP_THRESHOLD = 0.40


class DiversityLayer:
    """
    Re-ranks a pre-scored list of candidates so the chosen recipe has
    minimal ingredient overlap with the meals already planned for the day.
    """

    def rerank_for_day(
        self,
        top_candidates: list[tuple],
        already_planned: list,
    ) -> Recipe:
        """
        Parameters
        ----------
        top_candidates : list of (Recipe, score) sorted descending by score
        already_planned : list of Recipe objects already assigned today

        Returns the highest-scoring recipe whose ingredient overlap with
        already-planned meals is below OVERLAP_THRESHOLD.  Falls back to the
        top-scoring candidate if all candidates exceed the threshold.
        """
        if not already_planned:
            return top_candidates[0][0]

        for recipe, _score in top_candidates:
            if _ingredient_overlap(recipe, already_planned) < OVERLAP_THRESHOLD:
                return recipe

        # All candidates overlap too much — return best score regardless
        return top_candidates[0][0]
