import { apiFetch } from "@/services/apiClient";
import { ENDPOINTS } from "@/config/api";

export type RatingResponse = {
  rating_id: number;
  recipe_id: number;
  recipe_name: string;
  rating: number;
  interacted_at?: string;
};

export async function getRating(recipeId: number): Promise<RatingResponse | null> {
  const res = await apiFetch(
    `${ENDPOINTS.RATINGS}${recipeId}/`,
    { method: "GET" }
  );

  if (res.status === 404) return null;
  if (!res.ok) throw new Error("Failed to fetch rating");

  return res.json();
}

export async function createRating(recipeId: number, rating: number) {
  const res = await apiFetch(ENDPOINTS.RATINGS, {
    method: "POST",
    body: JSON.stringify({
      recipe_id: recipeId,
      rating,
    }),
  });

  if (!res.ok) throw new Error("Failed to create rating");
  return res.json();
}

export async function updateRating(recipeId: number, rating: number) {
  const res = await apiFetch(
    `${ENDPOINTS.RATINGS}${recipeId}/`,
    {
      method: "PATCH",
      body: JSON.stringify({ rating }),
    }
  );

  if (!res.ok) throw new Error("Failed to update rating");
  return res.json();
}

export async function deleteRating(recipeId: number) {
  const res = await apiFetch(`${ENDPOINTS.RATINGS}${recipeId}/`, { method: "DELETE" });
  if (!res.ok) throw new Error("Failed to delete rating");
  return;
}