import { ENDPOINTS } from "@/config/api";
import { apiFetch } from "@/services/apiClient";

export type MealType = "breakfast" | "lunch" | "dinner" | "snack";

export interface MealPlanItem {
  plan_id: number;
  recipe_id: number;
  recipe_name: string;
  meal_type: MealType;
  date: string;
}

/* 🔹 GET meal plan by date */
export async function getMealPlanByDate(date: string): Promise<MealPlanItem[]> {
  const res = await apiFetch(`${ENDPOINTS.MEAL_PLANS}?date=${date}`);
  const data = await res.json();
  return data.plans as MealPlanItem[];
}

/* 🔹 ADD recipe to meal plan */
export async function addMealToPlan(params: {
  recipeId: number;
  date: string;
  mealType: MealType;
}) {
  return apiFetch(ENDPOINTS.MEAL_PLANS, {
    method: "POST",
    body: JSON.stringify({
      recipe_id: params.recipeId,
      date: params.date,
      meal_type: params.mealType,
    }),
  });
}
