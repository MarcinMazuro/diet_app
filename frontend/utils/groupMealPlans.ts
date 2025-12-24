import { MealPlanItem, MealType } from "@/services/mealPlanService";

export function groupByMealType(plans: MealPlanItem[]) {
  const initial: Record<MealType, MealPlanItem[]> = {
    breakfast: [],
    lunch: [],
    dinner: [],
    snack: [],
  };

  return plans.reduce<Record<MealType, MealPlanItem[]>>((acc, plan) => {
    acc[plan.meal_type].push(plan);
    return acc;
  }, initial);
}