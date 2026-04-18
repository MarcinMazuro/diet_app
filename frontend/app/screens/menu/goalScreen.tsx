import React, { useEffect, useState } from "react";
import { extractMacroPercentages } from "@/utils/helper";
import {
  View,
  Text,
  TextInput,
  ActivityIndicator,
  Alert,
  ScrollView,
  Pressable,
} from "react-native";
import { getProfile } from "@/services/profileService";
import { updateMacroPercentages } from "@/services/goalService";


export default function GoalScreen() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [profile, setProfile] = useState<any>(null);

  const [protein, setProtein] = useState("");
  const [carbs, setCarbs] = useState("");
  const [fat, setFat] = useState("");

  const fmt = (n: any) => (n ? parseInt(n).toString() : "0");

  const updateMacroInputs = (macros: any) => {
    const mapping: { [key: string]: any } = {
      protein: macros?.protein?.percentage ?? 0,
      carbs: macros?.carbohydrates?.percentage ?? 0,
      fat: macros?.fat?.percentage ?? 0,
    };

    setProtein(Math.round(mapping.protein).toString());
    setCarbs(Math.round(mapping.carbs).toString());
    setFat(Math.round(mapping.fat).toString());
  };

  const loadProfile = async () => {
    try {
      setLoading(true);

      const p = await getProfile();
      const hasCustom =
        p.custom_protein_percentage != null ||
        p.custom_carb_percentage != null ||
        p.custom_fat_percentage != null;

      const data = await updateMacroPercentages(
        hasCustom ? parseFloat(p.custom_protein_percentage ?? "0") : undefined,
        hasCustom ? parseFloat(p.custom_carb_percentage ?? "0") : undefined,
        hasCustom ? parseFloat(p.custom_fat_percentage ?? "0") : undefined
      );

      const { proteinPct, carbsPct, fatPct } = extractMacroPercentages(data);

      setProtein(Math.round(proteinPct).toString());
      setCarbs(Math.round(carbsPct).toString());
      setFat(Math.round(fatPct).toString());
      setProfile(data);
    } catch (err) {
      Alert.alert("Błąd", err instanceof Error ? err.message : "Wystąpił błąd");
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    const p = parseInt(protein) || 0;
    const c = parseInt(carbs) || 0;
    const f = parseInt(fat) || 0;
    const sum = p + c + f;

    if (sum !== 100) {
      Alert.alert("Error", `Macro percentages must sum to 100%. Currently: ${sum}%`);
      return;
    }

    setSaving(true);
    try {
      const updated = await updateMacroPercentages(
        parseFloat((p / 100).toFixed(2)),
        parseFloat((c / 100).toFixed(2)),
        parseFloat((f / 100).toFixed(2))
      );

      Alert.alert("Success", "Macros have been updated.");
      setProfile(updated);
      updateMacroInputs(updated?.calculations?.macros);
    } catch (err) {
      Alert.alert("Error", err instanceof Error ? err.message : "An error occurred");
    } finally {
      setSaving(false);
    }
  };

  const handleReset = async () => {
    setSaving(true);
    try {
      const updated = await updateMacroPercentages();
      setProfile(updated);
      updateMacroInputs(updated?.calculations?.macros);
      Alert.alert("Reset", "Macros restored to default values.");
    } catch (err) {
      Alert.alert("Error", err instanceof Error ? err.message : "An error occurred");
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  if (loading) {
    return (
      <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 justify-center items-center">
        <ActivityIndicator size="large" color="#3b82f6" />
      </View>
    );
  }

  const kcal =
    profile?.calculations?.recommended_daily_calories ??
    profile?.recommended_daily_calories ??
    null;

  return (
    <ScrollView className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100" contentContainerStyle={{ padding: 20 }}>
      <View className="rounded-[36px] bg-white border border-blue-200 shadow-lg p-8 mb-6">
        <Text className="text-xs uppercase tracking-widest font-semibold text-blue-400">Calorie Goal</Text>
        {kcal && (
          <Text className="mt-4 text-5xl font-black text-blue-900 tracking-tighter">
            {fmt(kcal)} kcal
          </Text>
        )}
        <Text className="mt-4 text-base text-blue-600 leading-relaxed">
          Adjust the macronutrients in your diet to maintain a healthy balance.
        </Text>
      </View>

      <MacroRow
        label="Protein"
        value={protein}
        onChange={setProtein}
        grams={profile?.calculations?.macros?.protein?.grams}
      />
      <MacroRow
        label="Carbohydrates"
        value={carbs}
        onChange={setCarbs}
        grams={profile?.calculations?.macros?.carbohydrates?.grams}
      />
      <MacroRow
        label="Fat"
        value={fat}
        onChange={setFat}
        grams={profile?.calculations?.macros?.fat?.grams}
      />

      <View className="mt-6 gap-4">
        {saving ? (
          <ActivityIndicator size="large" color="#3b82f6" />
        ) : (
          <>
            <Pressable
              onPress={handleSave}
              className="rounded-[28px] bg-blue-600 py-5 items-center justify-center active:opacity-80 shadow-md"
            >
              <Text className="text-lg font-semibold text-white">Save Changes</Text>
            </Pressable>
            <Pressable
              onPress={handleReset}
              className="rounded-[28px] bg-blue-100 py-5 items-center justify-center active:opacity-80"
            >
              <Text className="text-lg font-semibold text-blue-700">Reset to Default</Text>
            </Pressable>
          </>
        )}
      </View>
    </ScrollView>
  );
}

function MacroRow({ label, value, onChange, grams }: any) {
  const displayGrams = grams != null ? grams.toFixed(1) : "0";

  return (
    <View className="rounded-[36px] bg-white border border-blue-200 shadow-lg p-6 mb-5">
      <View className="flex-row items-center justify-between gap-4 mb-4">
        <View>
          <Text className="text-sm uppercase tracking-widest font-semibold text-blue-400">{label}</Text>
          <Text className="mt-2 text-2xl font-bold text-blue-900">{displayGrams} g</Text>
        </View>
        <Text className="text-xs font-semibold text-blue-500">Estimated</Text>
      </View>
      <TextInput
        value={value}
        onChangeText={(val) => onChange(val.replace(/[^0-9]/g, ""))}
        keyboardType="number-pad"
        placeholder="0"
        placeholderTextColor="#64748b"
        className="rounded-[24px] border border-blue-300 bg-blue-50 px-5 py-4 text-blue-900 text-base"
      />
    </View>
  );
}

