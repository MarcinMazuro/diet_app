// services/goalService.ts
import { apiFetch } from "@/services/apiClient";
import { ENDPOINTS } from "@/config/api";

export type GoalData = any;

// Calculate macros based on current profile
export async function updateMacroPercentages(
  proteinPct?: number,
  carbPct?: number,
  fatPct?: number
): Promise<GoalData> {
  // Create body only if at least one parameter is provided (rest API allows omitting all)
  const body =
    proteinPct != null || carbPct != null || fatPct != null
      ? {
          custom_protein_percentage:
            proteinPct != null ? parseFloat(proteinPct.toFixed(2)) : undefined,
          custom_carb_percentage:
            carbPct != null ? parseFloat(carbPct.toFixed(2)) : undefined,
          custom_fat_percentage:
            fatPct != null ? parseFloat(fatPct.toFixed(2)) : undefined,
        }
      : undefined;

  const res = await apiFetch(ENDPOINTS.CALCULATE_MACROS, {
    method: "POST",
    ...(body ? { body: JSON.stringify(body) } : {}), // set body only if defined
  });

  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
