import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  Pressable,
  ActivityIndicator,
  StyleSheet,
  Button,
  Platform,
} from "react-native";
import DateTimePicker from "@react-native-community/datetimepicker";
import { useRouter } from "expo-router";
import { getMealPlanByDate } from "@/services/mealPlanService";
import { groupByMealType } from "@/utils/groupMealPlans";
import { MealPlanItem, MealType } from "@/services/mealPlanService";

export default function MealPlanScreen() {
  const router = useRouter();
  const [date, setDate] = useState(new Date());
  const [loading, setLoading] = useState(true);
  // All meal plans for the selected date, grouped by meal type 
  const [plans, setPlans] = useState<Record<MealType, MealPlanItem[]>>({
  breakfast: [],
  lunch: [],
  dinner: [],
  snack: [],
  });
  // Date picker visibility (for Android)
  const [showPicker, setShowPicker] = useState(false);

  const loadPlan = async () => {
    setLoading(true);
    try {
      // Format date as YYYY-MM-DD
      const isoDate = date.toISOString().split("T")[0];
      const data = await getMealPlanByDate(isoDate);
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
  // Date picker change handler 
const onChangeDate = (event: any, selectedDate?: Date) => {
  // Android: if dismissed, don't update date
  if (Platform.OS === "android") {
    setShowPicker(false);
    if (event.type === "dismissed") return; // do not update date
  }

  if (selectedDate) setDate(selectedDate);

  // iOS
  if (Platform.OS === "ios") {
    setShowPicker(true); // keep picker open on iOS (if false it closes immediately)
  }
};

  if (loading) return <ActivityIndicator style={{ marginTop: 40 }} />;

  return (
    <View style={styles.container}>
      {/* Picker */}
      <View style={{ marginBottom: 12, alignItems: "center", flexDirection: "row", justifyContent: "space-between" }}>
        <Text style={styles.title}>Date: {date.toISOString().split("T")[0]}</Text>
        <Button
          title={`change date`}
          onPress={() => setShowPicker(true)}
        />
        {showPicker && (
          <DateTimePicker
            value={date}
            mode="date"
            display="default"
            onChange={onChangeDate}
          />
          
        )}
        

      </View>


      {/* Meals */}
      {(["breakfast", "lunch", "dinner", "snack"] as const).map((meal) => (
        <View key={meal} style={styles.section}>
          <View style={styles.header}>
            <Text style={styles.mealTitle}>{meal.toUpperCase()}</Text>
            <Pressable onPress={() => alert("TODO: add recipe")}>
              <Text style={styles.add}>＋</Text>
            </Pressable>
          </View>

          {plans[meal].length === 0 && <Text style={styles.empty}>No meals</Text>}

          {plans[meal].map((item: MealPlanItem) => (
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
