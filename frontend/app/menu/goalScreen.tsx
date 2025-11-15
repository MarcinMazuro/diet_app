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
import { calculateMacros, updateMacroPercentages, GoalData } from "@/services/goalService";

export default function GoalScreen() {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [goalData, setGoalData] = useState<GoalData | null>(null);
  const [protein, setProtein] = useState("25.9");
  const [carbs, setCarbs] = useState("48.1");
  const [fat, setFat] = useState("25.9");

  const fetchMacros = async () => {
    try {
      setLoading(true);
      const data = await calculateMacros();
      setGoalData(data);
      setProtein(data.calculations.macros.protein.percentage.toFixed(1));
      setCarbs(data.calculations.macros.carbohydrates.percentage.toFixed(1));
      setFat(data.calculations.macros.fat.percentage.toFixed(1));
    } catch (err) {
      Alert.alert("Error", err instanceof Error ? err.message : "Error");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateMacros = async () => {
    setSaving(true);
    try {
      const p = parseFloat(protein);
      const c = parseFloat(carbs);
      const f = parseFloat(fat);
      const data = await updateMacroPercentages(p, c, f);
      setGoalData(data);
      setProtein(data.calculations.macros.protein.percentage.toFixed(1));
      setCarbs(data.calculations.macros.carbohydrates.percentage.toFixed(1));
      setFat(data.calculations.macros.fat.percentage.toFixed(1));
      Alert.alert("Success", "Macros updated");
    } catch (err) {
      Alert.alert("Error", err instanceof Error ? err.message : "Error");
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    fetchMacros();
  }, []);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  if (!goalData) {
    return (
      <View style={styles.center}>
        <Text>No data</Text>
      </View>
    );
  }

  const { calculations } = goalData;
  const proteinGrams = calculations.macros.protein.grams;
  const carbsGrams = calculations.macros.carbohydrates.grams;
  const fatGrams = calculations.macros.fat.grams;

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>
        Daily Calories: {calculations.recommended_daily_calories.toFixed(0)} kcal
      </Text>

      <View style={styles.row}>
        <View style={styles.inputCol}>
          <Text style={styles.label}>Protein %:</Text>
          <TextInput
            value={protein}
            onChangeText={setProtein}
            keyboardType="decimal-pad"
            style={styles.input}
          />
        </View>
        <View style={styles.gramsCol}>
          <Text style={styles.label}>Protein (g)</Text>
          <Text style={styles.gramsValue}>{proteinGrams.toFixed(0)} g</Text>
        </View>
      </View>

      <View style={styles.row}>
        <View style={styles.inputCol}>
          <Text style={styles.label}>Carbs %:</Text>
          <TextInput
            value={carbs}
            onChangeText={setCarbs}
            keyboardType="decimal-pad"
            style={styles.input}
          />
        </View>
        <View style={styles.gramsCol}>
          <Text style={styles.label}>Carbs (g)</Text>
          <Text style={styles.gramsValue}>{carbsGrams.toFixed(0)} g</Text>
        </View>
      </View>

      <View style={styles.row}>
        <View style={styles.inputCol}>
          <Text style={styles.label}>Fat %:</Text>
          <TextInput
            value={fat}
            onChangeText={setFat}
            keyboardType="decimal-pad"
            style={styles.input}
          />
        </View>
        <View style={styles.gramsCol}>
          <Text style={styles.label}>Fat (g)</Text>
          <Text style={styles.gramsValue}>{fatGrams.toFixed(0)} g</Text>
        </View>
      </View>

      {saving ? (
        <ActivityIndicator size="large" />
      ) : (
        <Button title="Update Macros" onPress={handleUpdateMacros} />
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  title: { fontSize: 20, fontWeight: "bold", marginBottom: 16, textAlign: "center" },
  row: { flexDirection: "row", alignItems: "center", marginBottom: 12 },
  inputCol: { flex: 1, marginRight: 12 },
  gramsCol: { width: 90, alignItems: "center" },
  input: { borderWidth: 1, padding: 8, borderRadius: 6 },
  label: { fontSize: 12, marginBottom: 6 },
  gramsValue: { fontSize: 16, fontWeight: "600", color: "#333" },
});