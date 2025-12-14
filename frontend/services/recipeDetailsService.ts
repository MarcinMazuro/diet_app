import { apiFetch } from "@/services/apiClient";
import { ENDPOINTS } from "@/config/api";

export type RecipeDetails = {
  id: number;
  name: string;
  description: string;
  source: string;
  image_url: string;
  categories: { id: number; name: string; type: string }[];
  ingredients: string[];
  directions: string[];
  servings: number;
  preparation_time: number;
  calories: number;
  protein: number;
  fat: number;
  carbohydrate: number;
  sugar: number;
  fiber: number;
  sodium: number;
};

export async function getRecipeById(id: string): Promise<RecipeDetails> {
  const res = await apiFetch(`${ENDPOINTS.RECIPES}${id}/`, {
    method: "GET",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch recipe details");
  }

  return res.json();
}
