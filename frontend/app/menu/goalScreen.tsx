import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  TextInput,
  Button,
  ActivityIndicator,
  Alert,
  ScrollView,
  StyleSheet,
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

  function fmt(n: any) {
    return n ? parseInt(n).toString() : "0";
  }

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


  // Load profile and set initial macro percentages
  const loadProfile = async () => {
    try {
      setLoading(true);
      const p = await getProfile();

      const prot = Math.round((parseFloat(p.custom_protein_percentage ?? "0") || 0) * 100);
      const carb = Math.round((parseFloat(p.custom_carb_percentage ?? "0") || 0) * 100);
      const f = Math.round((parseFloat(p.custom_fat_percentage ?? "0") || 0) * 100);

      setProtein(prot.toString());
      setCarbs(carb.toString());
      setFat(f.toString());

      if (prot + carb + f > 0) {
        const res = await updateMacroPercentages(
          parseFloat((prot / 100).toFixed(2)),
          parseFloat((carb / 100).toFixed(2)),
          parseFloat((f / 100).toFixed(2))
        );
        setProfile(res);
      } else {
        setProfile(p);
      }
    } catch (err) {
      Alert.alert("Error", err instanceof Error ? err.message : "Error");
    } finally {
      setLoading(false);
    }
  };
  // Save updated macro percentages
  const handleSave = async () => {
    const p = parseInt(protein) || 0;
    const c = parseInt(carbs) || 0;
    const f = parseInt(fat) || 0;
    // Validate sum equals 100
    const sum = p + c + f;
    if (sum !== 100) {
      Alert.alert("Error", `The sum of protein, carbs and fat must be 100%. Currently: ${sum}%`);
      return;
    }

    setSaving(true);
    try {
      const updated = await updateMacroPercentages(
        parseFloat((p / 100).toFixed(2)),
        parseFloat((c / 100).toFixed(2)),
        parseFloat((f / 100).toFixed(2))
      );

      Alert.alert("Success", "Macros updated");
      setProfile(updated);
      // Update inputs to reflect any backend adjustments
      updateMacroInputs(updated?.calculations?.macros);
    } catch (err) {
      Alert.alert("Error", err instanceof Error ? err.message : "Error");
    } finally {
      setSaving(false);
    }
  };

  // Reset to default macros
  const handleReset = async () => {
    setSaving(true);
    try {
      // No parameters to reset
      const updated = await updateMacroPercentages();
      setProfile(updated);

      updateMacroInputs(updated?.calculations?.macros);

      Alert.alert("Reset", "Macros reset to default values");
    } catch (err) {
      Alert.alert("Error", err instanceof Error ? err.message : "Error");
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }
  // Recommended daily calories
  const kcal =
    profile?.calculations?.recommended_daily_calories ??
    profile?.recommended_daily_calories ??
    null;

  return (
    <ScrollView style={styles.container}>
      {kcal && <Text style={styles.title}>Daily Calories: {fmt(kcal)} kcal</Text>}

      <MacroRow
        label="Protein %"
        value={protein}
        onChange={setProtein}
        grams={profile?.calculations?.macros?.protein?.grams}
      />

      <MacroRow
        label="Carbs %"
        value={carbs}
        onChange={setCarbs}
        grams={profile?.calculations?.macros?.carbohydrates?.grams}
      />

      <MacroRow
        label="Fat %"
        value={fat}
        onChange={setFat}
        grams={profile?.calculations?.macros?.fat?.grams}
      />

      {saving ? (
        <ActivityIndicator size="large" />
      ) : (
        <>
          <Button title="Update" onPress={handleSave} />
          <View style={{ marginTop: 10 }} />
          <Button title="Reset" onPress={handleReset} color="#888" />
        </>
      )}
    </ScrollView>
  );
}
// Component for a single macro row
function MacroRow({ label, value, onChange, grams }: any) {
  const displayGrams = grams != null ? grams.toFixed(1) : "0";
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <TextInput
        value={value}
        onChangeText={(val) => onChange(val.replace(/[^0-9]/g, ""))}
        keyboardType="number-pad"
        style={styles.input}
      />
      <Text style={styles.gramsText}>{displayGrams} g</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  title: { fontSize: 20, fontWeight: "bold", marginBottom: 16, textAlign: "center" },
  row: { marginBottom: 16 },
  label: { fontSize: 14, marginBottom: 6 },
  input: { borderWidth: 1, padding: 8, borderRadius: 6 },
  gramsText: { fontSize: 14, color: "#555", marginTop: 4 },
});
