import { View, Text, StyleSheet, Pressable, ActivityIndicator } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { useState } from "react";
import { addMealToPlan } from "@/services/mealPlanService";
import { MealType } from "@/services/mealPlanService";



type Params = {
  recipeId: string;
  recipeName: string;
  date: string;
  mealType: string;
};

export default function ConfirmAddScreen() {
  const router = useRouter();
  const { recipeId, recipeName, date, mealType } =
    useLocalSearchParams<Params>();

  const [loading, setLoading] = useState(false);

  const handleConfirm = async () => {
    try {
      setLoading(true);
      await addMealToPlan({
        recipeId: Number(recipeId),
        date,
        mealType: mealType as MealType,
      });

      router.back(); // back to previous screen (planner)
    } catch (e) {
      console.error(e);
      alert("Failed to add meal");
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Add meal to planner</Text>

      <View style={styles.card}>
        <Text style={styles.label}>Recipe</Text>
        <Text style={styles.value}>{recipeName}</Text>

        <Text style={styles.label}>Date</Text>
        <Text style={styles.value}>{date}</Text>

        <Text style={styles.label}>Meal type</Text>
        <Text style={styles.value}>{mealType}</Text>
      </View>

      {loading ? (
        <ActivityIndicator />
      ) : (
        <View style={styles.actions}>
          <Pressable style={styles.cancel} onPress={() => router.back()}>
            <Text style={styles.cancelText}>Cancel</Text>
          </Pressable>

          <Pressable style={styles.confirm} onPress={handleConfirm}>
            <Text style={styles.confirmText}>Add</Text>
          </Pressable>
        </View>
      )}
    </View>
  );
}
const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    justifyContent: "center",
  },
  title: {
    fontSize: 22,
    fontWeight: "bold",
    marginBottom: 24,
    textAlign: "center",
  },
  card: {
    backgroundColor: "#f3f3f3",
    borderRadius: 10,
    padding: 16,
    marginBottom: 24,
  },
  label: {
    fontSize: 12,
    color: "#666",
    marginTop: 8,
  },
  value: {
    fontSize: 16,
    fontWeight: "500",
  },
  actions: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  cancel: {
    padding: 14,
  },
  cancelText: {
    color: "#888",
    fontSize: 16,
  },
  confirm: {
    backgroundColor: "green",
    padding: 14,
    borderRadius: 8,
  },
  confirmText: {
    color: "#fff",
    fontSize: 16,
    fontWeight: "bold",
  },
});
