import React, { useEffect, useState } from "react";
import { View, Text, Button, ActivityIndicator, StyleSheet } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import {
  generateMeal,
  generateDailyPlan,
  MealType,
} from "@/services/mealPlanService";

export default function GeneratePlanScreen() {
  const router = useRouter();
  const { date, mode, mealType } = useLocalSearchParams<{
    date: string;
    mode: "daily" | "single";
    mealType?: MealType;
  }>();

  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      if (mode === "daily") {
        await generateDailyPlan(date);
      } else if (mode === "single" && mealType) {
        await generateMeal({ date, mealType });
      }
      setDone(true);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Generate meal plan</Text>

      <Text>Date: {date}</Text>

      {mode === "daily" ? (
        <Text>Mode: Full day</Text>
      ) : (
        <Text>Meal: {mealType?.toUpperCase()}</Text>
      )}

      {loading && <ActivityIndicator style={{ marginVertical: 20 }} />}

      {!done ? (
        <Button title="⚡ Generate" onPress={handleGenerate} />
      ) : (
        <Button
          title="✅ Go back to planner"
          onPress={() => router.back()}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, padding: 20, justifyContent: "center" },
  title: { fontSize: 20, fontWeight: "bold", marginBottom: 12 },
});
