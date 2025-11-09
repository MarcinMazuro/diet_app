// app/profileScreen.tsx
import React, { useEffect, useState } from "react";
import { View, Text, TextInput, Button, ActivityIndicator, Alert, ScrollView } from "react-native";
import RNPickerSelect from "react-native-picker-select";
import { getProfile, updateProfile, ProfileData } from "@/services/profileService";

export default function ProfileScreen() {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [formData, setFormData] = useState<ProfileData>({
        first_name: "",
        last_name: "",
        weight: "",
        height: "",
        gender: "",
        nutritional_goal: "",
        physical_activity: "",
    });

    // Fetch profile data
    const fetchProfile = async () => {
        try {
            const data = await getProfile();
            setFormData({
                first_name: data.first_name ?? "",
                last_name: data.last_name ?? "",
                weight: data.weight?.toString() ?? "",
                height: data.height?.toString() ?? "",
                gender: data.gender ?? "",
                nutritional_goal: data.nutritional_goal ?? "",
                physical_activity: data.physical_activity ?? "",
            });
        } catch (err) {
            Alert.alert("Error", err instanceof Error ? err.message : "Error fetching profile");
        } finally {
            setLoading(false);
        }
    };

    // Save profile data
    const handleSave = async () => {
        setSaving(true);
        try {
            await updateProfile(formData);
            Alert.alert("Success", "Profile has been updated successfully");
        } catch (err) {
            Alert.alert("Error", err instanceof Error ? err.message : "Error updating profile");
        } finally {
            setSaving(false);
        }
    };

    useEffect(() => {
        fetchProfile();
    }, []);

    if (loading) {
        return (
            <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
                <ActivityIndicator size="large" />
            </View>
        );
    }

    return (
        <ScrollView contentContainerStyle={{ padding: 16 }}>
            <Text style={{ fontSize: 20, fontWeight: "bold", marginBottom: 16 }}>My Profile</Text>

            <Text>First name</Text>
            <TextInput
                value={formData.first_name}
                onChangeText={(text) => setFormData((prev) => ({ ...prev, first_name: text }))}
                style={{ borderWidth: 1, padding: 8, marginVertical: 6 }}
            />

            <Text>Last name</Text>
            <TextInput
                value={formData.last_name}
                onChangeText={(text) => setFormData((prev) => ({ ...prev, last_name: text }))}
                style={{ borderWidth: 1, padding: 8, marginVertical: 6 }}
            />

            <Text>Weight (kg)</Text>
            <TextInput
                value={formData.weight}
                onChangeText={(text) => setFormData((prev) => ({ ...prev, weight: text }))}
                keyboardType="numeric"
                style={{ borderWidth: 1, padding: 8, marginVertical: 6 }}
            />

            <Text>Height (cm)</Text>
            <TextInput
                value={formData.height}
                onChangeText={(text) => setFormData((prev) => ({ ...prev, height: text }))}
                keyboardType="numeric"
                style={{ borderWidth: 1, padding: 8, marginVertical: 6 }}
            />

            {/* GENDER PICKER */}
            <Text>Gender</Text>
            <RNPickerSelect
                onValueChange={(value) => setFormData((prev) => ({ ...prev, gender: value }))}
                value={formData.gender}
                items={[
                    { label: "Male", value: "M" },
                    { label: "Female", value: "F" },
                    { label: "Transgender", value: "T" },
                    { label: "Non-binary", value: "NB" },
                    { label: "Agender", value: "AG" },
                    { label: "Genderfluid", value: "GF" },
                    { label: "Bigender", value: "BI" },
                    { label: "Pangender", value: "PAN" },
                    { label: "Genderqueer", value: "GQ" },
                    { label: "Demiboy", value: "DB" },
                    { label: "Demigirl", value: "DG" },
                    { label: "Androgyne", value: "AN" },
                    { label: "Neutrois", value: "NE" },
                    { label: "Trigender", value: "TRI" },
                    { label: "Genderflux", value: "GX" },
                    { label: "Xenogender", value: "XE" },
                    { label: "Two-Spirit", value: "2S" },
                    { label: "Aliagender", value: "AL" },
                    { label: "Graygender", value: "GG" },
                    { label: "Polygender", value: "PO" },
                    { label: "Helboj", value: "HB" },
                    { label: "Other", value: "O" },
                ]}
                placeholder={{ label: "Choose gender...", value: null }}
            />

            {/* NUTRITIONAL GOAL PICKER */}
            <Text>Diet goal</Text>
            <RNPickerSelect
                onValueChange={(value) => setFormData((prev) => ({ ...prev, nutritional_goal: value }))}
                value={formData.nutritional_goal}
                items={[
                    { label: "Maintain weight", value: "MAINTAIN" },
                    { label: "Lose weight", value: "LOSE" },
                    { label: "Gain muscle mass", value: "GAIN" },
                ]}
                placeholder={{ label: "Choose goal...", value: null }}
            />

            {/* PHYSICAL ACTIVITY PICKER */}
            <Text>Physical activity</Text>
            <RNPickerSelect
                onValueChange={(value) => setFormData((prev) => ({ ...prev, physical_activity: value }))}
                value={formData.physical_activity}
                items={[
                    { label: "Sedentary (little or no exercise)", value: "SEDENTARY" },
                    { label: "Lightly active (light exercise/sports 1–3 days/week)", value: "LIGHT" },
                    { label: "Moderately active (moderate exercise/sports 3–5 days/week)", value: "MODERATE" },
                    { label: "Very active (hard exercise/sports 6–7 days/week)", value: "VERY" },
                    { label: "Extra active (very hard exercise/sports & physical job)", value: "EXTRA" },
                ]}
                placeholder={{ label: "Choose activity level...", value: null }}
            />

            <View style={{ marginTop: 24 }}>
                {saving ? (
                    <ActivityIndicator size="large" />
                ) : (
                    <Button title="Save changes" onPress={handleSave} />
                )}
            </View>
        </ScrollView>
    );
}
