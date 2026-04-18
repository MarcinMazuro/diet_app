import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  TextInput,
  ActivityIndicator,
  Alert,
  ScrollView,
  Platform,
  Pressable,
} from "react-native";
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
      Alert.alert("Błąd", err instanceof Error ? err.message : "Błąd pobierania profilu");
    } finally {
      setLoading(false);
    }
  };

  const isAnyDataEmpty = (data: ProfileData) =>
    Object.entries(data).some(([_, value]) => {
      if (typeof value === "string") return value.trim() === "";
      return value === null || value === undefined;
    });

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
    if (isAnyDataEmpty(formData)) {
      Alert.alert("Error", "Please fill in all fields before saving.");
      return;
    }

    setSaving(true);
    try {
      await updateProfile(formData);
      Alert.alert("Success", "Profile has been updated.");
    } catch (err) {
      Alert.alert("Error", err instanceof Error ? err.message : "Profile update error");
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  if (loading) {
    return (
      <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 justify-center items-center">
        <ActivityIndicator size="large" color="#3b82f6" />
      </View>
    );
  }

  const pickerStyle = {
    inputIOS: {
      borderRadius: 24,
      backgroundColor: "#eff6ff",
      paddingVertical: 16,
      paddingHorizontal: 20,
      fontSize: 16,
      color: "#1e40af",
    },
    inputAndroid: {
      borderRadius: 24,
      backgroundColor: "#eff6ff",
      paddingVertical: 16,
      paddingHorizontal: 20,
      fontSize: 16,
      color: "#1e40af",
    },
    placeholder: {
      color: "#64748b",
    },
  };

  return (
    <ScrollView className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100" contentContainerStyle={{ padding: 20 }}>
      <Text className="text-4xl font-black text-blue-900 mb-6">My Profile</Text>

      <View className="rounded-[36px] bg-white border border-blue-200 shadow-lg p-8 gap-5 mb-6">
        <FormField label="First Name">
          <TextInput
            value={formData.first_name}
            onChangeText={(text) => setFormData((prev) => ({ ...prev, first_name: text }))}
            placeholder="First Name"
            placeholderTextColor="#64748b"
            className="rounded-[24px] border border-blue-300 bg-blue-50 px-5 py-4 text-blue-900 text-base"
          />
        </FormField>

        <FormField label="Last Name">
          <TextInput
            value={formData.last_name}
            onChangeText={(text) => setFormData((prev) => ({ ...prev, last_name: text }))}
            placeholder="Last Name"
            placeholderTextColor="#64748b"
            className="rounded-[24px] border border-blue-300 bg-blue-50 px-5 py-4 text-blue-900 text-base"
          />
        </FormField>

        <FormField label="Date of Birth">
          <Pressable
            onPress={() => setShowDatePicker(true)}
            className="rounded-[24px] border border-blue-300 bg-blue-50 px-5 py-4"
          >
            <Text className="text-blue-700">{formData.date_of_birth || "Select date"}</Text>
          </Pressable>
          {showDatePicker && (
            <View className="overflow-hidden rounded-[24px] border border-blue-300 mt-3">
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
            </View>
          )}
        </FormField>

        <FormField label="Weight (kg)">
          <TextInput
            value={formData.weight}
            onChangeText={(text) => setFormData((prev) => ({ ...prev, weight: text }))}
            keyboardType="numeric"
            placeholder="Weight"
            placeholderTextColor="#64748b"
            className="rounded-[24px] border border-blue-300 bg-blue-50 px-5 py-4 text-blue-900 text-base"
          />
        </FormField>

        <FormField label="Height (cm)">
          <TextInput
            value={formData.height}
            onChangeText={(text) => setFormData((prev) => ({ ...prev, height: text }))}
            keyboardType="numeric"
            placeholder="Height"
            placeholderTextColor="#64748b"
            className="rounded-[24px] border border-blue-300 bg-blue-50 px-5 py-4 text-blue-900 text-base"
          />
        </FormField>

        <FormField label="Gender">
          <RNPickerSelect
            onValueChange={(value) => setFormData((prev) => ({ ...prev, gender: value }))}
            value={formData.gender}
            items={[
              { label: "Male", value: "M" },
              { label: "Female", value: "F" },
              { label: "Other", value: "O" },
            ]}
            placeholder={{ label: "Select gender...", value: null }}
            style={pickerStyle}
          />
        </FormField>

        <FormField label="Nutritional Goal">
          <RNPickerSelect
            onValueChange={(value) => setFormData((prev) => ({ ...prev, nutritional_goal: value }))}
            value={formData.nutritional_goal}
            items={[
              { label: "Maintain weight", value: "MAINTAIN" },
              { label: "Lose weight", value: "LOSE" },
              { label: "Build muscle", value: "GAIN" },
            ]}
            placeholder={{ label: "Select goal...", value: null }}
            style={pickerStyle}
          />
        </FormField>

        <FormField label="Physical Activity">
          <RNPickerSelect
            onValueChange={(value) => setFormData((prev) => ({ ...prev, physical_activity: value }))}
            value={formData.physical_activity}
            items={[
              { label: "Sedentary lifestyle", value: "SEDENTARY" },
              { label: "Lightly active", value: "LOW" },
              { label: "Moderately active", value: "MODERATE" },
              { label: "Very active", value: "HIGH" },
              { label: "Extremely active", value: "VERY_HIGH" },
            ]}
            placeholder={{ label: "Select level...", value: null }}
            style={pickerStyle}
          />
        </FormField>

        <View className="mt-6 gap-4">
          {saving ? (
            <ActivityIndicator size="large" color="#3b82f6" />
          ) : (
            <Pressable
              onPress={handleSave}
              className="rounded-[28px] bg-blue-600 py-5 items-center justify-center active:opacity-80 shadow-md"
            >
              <Text className="text-lg font-semibold text-white">Save Changes</Text>
            </Pressable>
          )}
        </View>
      </View>
    </ScrollView>
  );
}

function FormField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <View>
      <Text className="text-sm font-semibold text-blue-700 mb-3">{label}</Text>
      {children}
    </View>
  );
}
