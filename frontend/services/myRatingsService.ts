import { apiFetch } from "@/services/apiClient";
import { ENDPOINTS } from "@/config/api";

export type MyRating = {
  recipe_id: number;
  recipe_name: string;
  rating: number;
  interacted_at: string;
};

export async function getMyRatings(): Promise<MyRating[]> {
  const res = await apiFetch(ENDPOINTS.RATINGS, { method: "GET" });

  if (!res.ok) throw new Error("Failed to fetch my ratings");

  const data = await res.json();
  return data.ratings;
}
