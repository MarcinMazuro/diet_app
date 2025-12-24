import React, { useEffect, useState, useCallback } from "react";
import {
  View,
  Text,
  Pressable,
  ActivityIndicator,
  StyleSheet,
  Button,
  Platform,
  Alert
} from "react-native";
import DateTimePicker from "@react-native-community/datetimepicker";
import { useRouter } from "expo-router";
import { getMealPlanByDate, deleteMealPlanItem } from "@/services/mealPlanService";
import { groupByMealType } from "@/utils/groupMealPlans";
import { MealPlanItem, MealType } from "@/services/mealPlanService";
import { useFocusEffect } from "expo-router";



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

  // Reload when screen is focused (e.g., after adding a meal)
  useFocusEffect(
    useCallback(() => {
      loadPlan();
    }, [date])
  );

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

const handleDelete = async (planId: number, meal: MealType) => {
  Alert.alert(
    "Remove meal",
    "Are you sure you want to remove this meal?",
    [
      { text: "Cancel", style: "cancel" },
      {
        text: "Remove",
        style: "destructive",
        onPress: async () => {
          try {
            await deleteMealPlanItem(planId);

            // 🔥 lokalna aktualizacja stanu (bez reloadu)
            setPlans((prev) => ({
              ...prev,
              [meal]: prev[meal].filter((item) => item.plan_id !== planId),
            }));
          } catch (e) {
            console.error(e);
            Alert.alert("Error", "Could not remove meal");
          }
        },
      },
    ]
  );
};


  if (loading) return <ActivityIndicator style={{ marginTop: 40 }} />;

  return (
    



    <View style={styles.container}>
        
      {/* Picker */}
      <View style={{ marginBottom: 12, alignItems: "center", flexDirection: "row", justifyContent: "space-between" }}>
        <Text style={styles.title}>Date: {date.toISOString().split("T")[0]}</Text>
        <Button
          title="⚡Generate"
          onPress={() =>
            router.push({
              pathname: "/screens/planner/generate-plan",
              params: {
                date: date.toISOString().split("T")[0],
                mode: "daily",
              },
            })
          }
        />
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
    {/* Header */}
    <View style={styles.header}>
      <Text style={styles.mealTitle}>{meal.toUpperCase()}</Text>
      <View style={styles.actions}>
        <Pressable
          onPress={() =>
            router.push({
              pathname: "/screens/planner/generate-plan",
              params: {
                date: date.toISOString().split("T")[0],
                mode: "single",
                mealType: meal,
              },
            })
          }
        >
          <Text style={styles.generate}>⚡</Text>
        </Pressable>

        {/*ADD MANUALLY */}
        <Pressable
          onPress={() =>
            router.push({
              pathname: "/screens/planner/recipe-picker",
              params: {
                date: date.toISOString().split("T")[0],
                mealType: meal,
              },
            })
          }
        >
          <Text style={styles.add}>＋</Text>
        </Pressable>
      </View>
    </View>

    {/* Empty */}
    {plans[meal].length === 0 && (
      <Text style={styles.empty}>No meals</Text>
    )}

    {/* Meals list */}
    {plans[meal].map((item: MealPlanItem) => (
      <View key={item.plan_id} style={styles.recipeRow}>
        <Pressable
          style={{ flex: 1 }}
          onPress={() => router.push(`/screens/recipe/${item.recipe_id}`)}
        >
          <Text style={styles.recipe}>{item.recipe_name}</Text>
        </Pressable>

        <Pressable onPress={() => handleDelete(item.plan_id, meal)}>
          <Text style={styles.delete}>🗑️</Text>
        </Pressable>
      </View>
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
  recipeRow: {
  flexDirection: "row",
  alignItems: "center",
  justifyContent: "space-between",
},

delete: {
  fontSize: 18,
  color: "red",
  paddingHorizontal: 8,
},

actions: {
  flexDirection: "row",
  gap: 12,
  alignItems: "center",
},

generate: {
  fontSize: 18,
},


});
