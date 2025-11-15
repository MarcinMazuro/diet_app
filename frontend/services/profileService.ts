// services/profileService.ts
import { ENDPOINTS } from "@/config/api";
import { apiFetch } from "@/services/apiClient";

export type ProfileData = {
    first_name: string;
    last_name: string;
    weight: string;
    height: string;
    date_of_birth: string;
    gender: string;
    nutritional_goal: string;
    physical_activity: string;
};

export async function getProfile(): Promise<ProfileData> {
    const response = await apiFetch(ENDPOINTS.ME);
    if (!response.ok) throw new Error("Cannot fetch profile data");
    return await response.json();
}

export async function updateProfile(profileData: ProfileData) {
    const response = await apiFetch(ENDPOINTS.ME, {
        method: "PATCH",
        body: JSON.stringify(profileData),
    });
    if (!response.ok) throw new Error("Update failed");
    return await response.json();
}
