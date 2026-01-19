import React, { useEffect, useState } from "react";
import { View, Text, TextInput, Button, ActivityIndicator, Alert, ScrollView, Platform, TouchableOpacity } from "react-native";
import RNPickerSelect from "react-native-picker-select";
import DateTimePicker from '@react-native-community/datetimepicker';
import { getProfile, updateProfile, ProfileData } from "@/services/profileService";

export default function ProfileScreen() {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [formData, setFormData] = useState<ProfileData>({
        first_name: "",
        last_name: "",
        weight: "",
        height: "",
        date_of_birth: "",
        gender: "",
        nutritional_goal: "",
        physical_activity: "",
    });

    

    const fetchProfile = async () => {
        try {
            const data = await getProfile();
            setFormData({
                first_name: data.first_name ?? "",
                last_name: data.last_name ?? "",
                weight: data.weight?.toString() ?? "",
                height: data.height?.toString() ?? "",
                date_of_birth: data.date_of_birth ?? "",
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

    const IsAnyDataEmpty = (data: ProfileData) => {
    return Object.entries(data).some(([_, value]) => {
        if (typeof value === "string") return value.trim() === "";
        return value === null || value === undefined;
    });
    };

    const [showDatePicker, setShowDatePicker] = useState(false);

    const pad = (n: number) => (n < 10 ? `0${n}` : `${n}`);
    const formatDate = (date: Date) => `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
    const parseDateString = (s: string) => {
        if (!s) return new Date();
        const parts = s.split("-");
        if (parts.length !== 3) return new Date(s);
        const y = Number(parts[0]);
        const m = Number(parts[1]) - 1;
        const d = Number(parts[2]);
        return new Date(y, m, d);
    };


    const handleSave = async () => {
        if (IsAnyDataEmpty(formData)) {
            Alert.alert("Error", "Please fill in all fields before saving.");
            return;
        }
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

            <Text>Date of birth (YYYY-MM-DD)</Text>
            <TouchableOpacity onPress={() => setShowDatePicker(true)} style={{ borderWidth: 1, padding: 8, marginVertical: 6 }}>
                <Text>{formData.date_of_birth ? formData.date_of_birth : "Tap to select date"}</Text>
            </TouchableOpacity>
            {showDatePicker && (
                <DateTimePicker
                    value={formData.date_of_birth ? parseDateString(formData.date_of_birth) : new Date()}
                    mode="date"
                    display={Platform.OS === 'ios' ? 'spinner' : 'default'}
                    maximumDate={new Date()}
                    onChange={(event, selectedDate) => {
                        if (Platform.OS === 'android') {
                            setShowDatePicker(false);
                            if (selectedDate) {
                                setFormData((prev) => ({ ...prev, date_of_birth: formatDate(selectedDate) }));
                            }
                            return;
                        }
                        if (selectedDate) {
                            setFormData((prev) => ({ ...prev, date_of_birth: formatDate(selectedDate) }));
                        }
                    }}
                />
            )}

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
                    { label: "Other", value: "O" }
                ]}
                placeholder={{ label: "Choose gender...", value: null }}
            />

            <Text style={{ marginTop: 12 }}>Diet goal</Text>
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

            <Text style={{ marginTop: 12 }}>Physical activity</Text>
            <RNPickerSelect
                onValueChange={(value) => setFormData((prev) => ({ ...prev, physical_activity: value }))}
                value={formData.physical_activity}
                items={[
                    { label: "Sedentary (little or no exercise)", value: "SEDENTARY" },
                    { label: "Lightly active (light exercise/sports 1–3 days/week)", value: "LOW" },
                    { label: "Moderately active (moderate exercise/sports 3–5 days/week)", value: "MODERATE" },
                    { label: "Very active (hard exercise/sports 6–7 days/week)", value: "HIGH" },
                    { label: "Extra active (very hard exercise/sports & physical job)", value: "VERY_HIGH" },
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