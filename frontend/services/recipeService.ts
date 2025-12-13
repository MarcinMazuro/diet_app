import { apiFetch } from "@/services/apiClient";
import { ENDPOINTS } from "@/config/api";

export type RecipeCategory = {
  id: number;
  name: string;
  type: string;
};

export type Recipe = {
  id: number;
  name: string;
  preparation_time: number;
  calories: number;
  image_url: string;
  categories: RecipeCategory[];
  servings: number;
};

export type RecipesResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Recipe[];
};

export type GetRecipesParams = {
  page?: number;
  pageSize?: number;
  ordering?: string;
  name?: string;
  minCalories?: number;
  maxCalories?: number;
  category?: string;
};

export async function getRecipes(
  params: GetRecipesParams = {}
): Promise<RecipesResponse> {
  const query = new URLSearchParams();

  if (params.page) query.append("page", String(params.page));
  if (params.pageSize) query.append("page_size", String(params.pageSize));
  if (params.ordering) query.append("ordering", params.ordering);
  if (params.name) query.append("name", params.name);
  if (params.minCalories) query.append("min_calories", String(params.minCalories));
  if (params.maxCalories) query.append("max_calories", String(params.maxCalories));
  if (params.category) query.append("category", params.category);

  const url = `${ENDPOINTS.RECIPES}?${query.toString()}`;

  const res = await apiFetch(url, {
    method: "GET",
  });
  if (!res.ok) {
    throw new Error("Failed to fetch recipes");
  }

  return res.json();
}
