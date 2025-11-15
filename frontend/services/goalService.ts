import { ENDPOINTS } from "@/config/api";
import { apiFetch } from "@/services/apiClient";

export type MacroData = {
  protein: {
    grams: number;
    per_kg: number;
    percentage: number;
  };
  carbohydrates: {
    grams: number;
    percentage: number;
  };
  fat: {
    grams: number;
    percentage: number;
  };
};

export type GoalData = {
  method: string;
  method_reason: string;
  calorie_adjustment_used: number;
  basic_data: {
    age: number;
    weight: number;
    height: number;
    bmi: number;
    gender: string;
    physical_activity: string;
    nutritional_goal: string;
  };
  calculations: {
    ppm: number;
    pal: number;
    cpm: number;
    recommended_daily_calories: number;
    macros: MacroData;
  };
  saved_to_profile: boolean;
  last_updated: string;
};

export async function calculateMacros(): Promise<GoalData> {
  try {
    console.log("Fetching macros from:", ENDPOINTS.CALCULATE_MACROS);
    
    const response = await apiFetch(ENDPOINTS.CALCULATE_MACROS, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    });

    console.log("Response status:", response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error("Error response:", errorText);
      throw new Error(`Server error: ${response.status}`);
    }
    
    const data = await response.json();
    console.log("Macros data:", data);
    return data;
  } catch (err) {
    console.error("Calculate macros error:", err);
    throw err;
  }
}

export async function updateMacroPercentages(
  proteinPercentage: number,
  carbPercentage: number,
  fatPercentage: number
): Promise<GoalData> {
  try {
    const total = proteinPercentage + carbPercentage + fatPercentage;
    if (Math.abs(total - 100) > 0.1) {
      throw new Error(`Percentages must sum to 100% (current: ${total.toFixed(1)}%)`);
    }

    console.log("Updating macros with:", {
      custom_protein_percentage: proteinPercentage / 100,
      custom_carb_percentage: carbPercentage / 100,
      custom_fat_percentage: fatPercentage / 100,
    });

    const response = await apiFetch(ENDPOINTS.CALCULATE_MACROS, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        custom_protein_percentage: proteinPercentage / 100,
        custom_carb_percentage: carbPercentage / 100,
        custom_fat_percentage: fatPercentage / 100,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("Error response:", errorText);
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (err) {
    console.error("Update macros error:", err);
    throw err;
  }
}