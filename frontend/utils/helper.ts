// utils/profileHelpers.ts  (możesz też trzymać w tym samym pliku jeśli wolisz)
import { ProfileData } from "@/services/profileService";

export function extractMacroPercentages(profile: ProfileData | any) {
    // profile może być standardowym ProfileData lub odpowiedzią kalkulacji z backendu
    const p: any = profile;

    // preferuj wartości z calculations.macros jeśli istnieją
    const calc = p?.calculations?.macros;
    if (calc) {
        return {
            proteinPct: (calc.protein?.percentage ?? 0) * 1,
            carbsPct: (calc.carbohydrates?.percentage ?? 0) * 1,
            fatPct: (calc.fat?.percentage ?? 0) * 1,
        };
    }

    // fallback: użyj pól custom_* (mogą być stringami "0.40")
    const prot = parseFloat(p?.custom_protein_percentage ?? "0") * 100;
    const carb = parseFloat(p?.custom_carb_percentage ?? "0") * 100;
    const fat = parseFloat(p?.custom_fat_percentage ?? "0") * 100;

    return {
        proteinPct: prot || 0,
        carbsPct: carb || 0,
        fatPct: fat || 0,
    };
}