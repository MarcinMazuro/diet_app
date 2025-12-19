import { apiFetch } from "@/services/apiClient";
import { ENDPOINTS } from "@/config/api";

export type MealType = "breakfast" | "lunch" | "dinner" | "snack";

export type MealPlanItem = {
  plan_id: number;
  recipe_id: number;
  recipe_name: string;
  date: string;
  meal_type: MealType;
  source: string;
};
export async function getMealPlanByDate(date: string) {
  const res = await apiFetch(
    `${ENDPOINTS.MEAL_PLANS}?date=${date}`,
    { method: "GET" }
  );

  if (!res.ok) throw new Error("Failed to fetch meal plan");
  const data = await res.json();
  return data.plans as MealPlanItem[];
}
