import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  Pressable,
  ActivityIndicator,
  StyleSheet,
} from "react-native";
import { useRouter } from "expo-router";
import { getMealPlanByDate } from "@/services/mealPlanService";
import { groupByMealType } from "@/utils/groupMealPlans";
import { MealPlanItem, MealType } from "@/services/mealPlanService";
const today = new Date().toISOString().split("T")[0];

export default function MealPlanScreen() {
  const router = useRouter();
  const [date, setDate] = useState(today);
  const [loading, setLoading] = useState(true);
  const [plans, setPlans] = useState<Record<MealType, MealPlanItem[]>>({
  breakfast: [],
  lunch: [],
  dinner: [],
  snack: [],
});



  const loadPlan = async () => {
    setLoading(true);
    try {
      const data = await getMealPlanByDate(date);
      setPlans(groupByMealType(data));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPlan();
  }, [date]);

  if (loading) {
    return <ActivityIndicator style={{ marginTop: 40 }} />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Meal plan – {date}</Text>

      {(["breakfast", "lunch", "dinner", "snack"] as const).map((meal) => (
        <View key={meal} style={styles.section}>
          <View style={styles.header}>
            <Text style={styles.mealTitle}>{meal.toUpperCase()}</Text>
            <Pressable onPress={() => alert("TODO: add recipe")}>
              <Text style={styles.add}>＋</Text>
            </Pressable>
          </View>

          {plans[meal].length === 0 && (
            <Text style={styles.empty}>No meals</Text>
          )}

          {plans[meal].map((item: any) => (
            <Pressable
              key={item.plan_id}
              onPress={() => router.push(`/screens/recipe/${item.recipe_id}`)}
            >
              <Text style={styles.recipe}>{item.recipe_name}</Text>
            </Pressable>
          ))}
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    padding: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: "bold",
    marginBottom: 16,
  },
  section: {
    marginBottom: 20,
    padding: 12,
    borderRadius: 10,
    backgroundColor: "#f3f3f3",
  },
  header: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 8,
  },
  mealTitle: {
    fontSize: 16,
    fontWeight: "bold",
  },
  add: {
    fontSize: 22,
    color: "green",
  },
  recipe: {
    paddingVertical: 6,
    fontSize: 15,
  },
  empty: {
    fontStyle: "italic",
    color: "#666",
  },
});