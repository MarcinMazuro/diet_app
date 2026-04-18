import React, { useEffect, useState, useCallback } from "react";
import {
  View,
  Text,
  Pressable,
  ActivityIndicator,
  Platform,
  Alert,
  ScrollView,
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
  const [plans, setPlans] = useState<Record<MealType, MealPlanItem[]>>({
    breakfast: [],
    lunch: [],
    dinner: [],
    snack: [],
  });
  const [showPicker, setShowPicker] = useState(false);

  useFocusEffect(
    useCallback(() => {
      loadPlan();
    }, [date])
  );

  const loadPlan = async () => {
    setLoading(true);
    try {
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

  const onChangeDate = (event: any, selectedDate?: Date) => {
    if (Platform.OS === "android") {
      setShowPicker(false);
      if (event.type === "dismissed") return;
    }

    if (selectedDate) setDate(selectedDate);

    if (Platform.OS === "ios") {
      setShowPicker(true);
    }
  };

  const handleDelete = async (planId: number, meal: MealType) => {
    Alert.alert(
      "Delete Meal",
      "Are you sure you want to delete this meal?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete",
          style: "destructive",
          onPress: async () => {
            try {
              await deleteMealPlanItem(planId);
              setPlans((prev) => ({
                ...prev,
                [meal]: prev[meal].filter((item) => item.plan_id !== planId),
              }));
            } catch (e) {
              console.error(e);
              Alert.alert("Error", "Failed to delete meal");
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 justify-center items-center">
        <ActivityIndicator size="large" color="#3b82f6" />
      </View>
    );
  }

  return (
    <ScrollView className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-5">
      <View className="rounded-[32px] bg-white border border-blue-200 shadow-lg p-6 mb-10">
        <View className="flex-row items-start justify-between gap-4">
          <View className="flex-1">
            <Text className="text-xs uppercase tracking-widest font-semibold text-blue-400">
              Your Meal Plan
            </Text>
            <Text className="mt-3 text-3xl font-bold text-blue-900">{date.toISOString().split("T")[0]}</Text>
            <Text className="mt-2 text-sm text-blue-600">
              Plan your meals and track your nutrition for the day.
            </Text>
          </View>
        </View>

        <View className="mt-6 flex-row justify-end gap-3">
          <Pressable
            onPress={() => setShowPicker(true)}
            className="flex-1 rounded-[24px] bg-blue-50 py-4 items-center justify-center border border-blue-200 active:opacity-80"
          >
            <Text className="text-base font-semibold text-blue-700">Change Date</Text>
          </Pressable>
          <Pressable
            onPress={() =>
              router.push({
                pathname: "/screens/planner/generate-plan" as any,
                params: {
                  date: date.toISOString().split("T")[0],
                  mode: "daily",
                },
              } as any)
            }
            className="flex-1 rounded-[24px] bg-blue-600 py-4 items-center justify-center active:opacity-80 shadow-md"
          >
            <Text className="text-base font-semibold text-white">Generate Day</Text>
          </Pressable>
        </View>

        {showPicker && (
          <View className="mt-4 overflow-hidden rounded-[24px] border border-blue-300">
            <DateTimePicker value={date} mode="date" display="default" onChange={onChangeDate} />
          </View>
        )}
      </View>

      {(["breakfast", "lunch", "dinner", "snack"] as const).map((meal) => (
        <View key={meal} className="mb-5 rounded-[32px] bg-white border border-blue-200 shadow-lg overflow-hidden">
          <View className="px-6 py-5 bg-gradient-to-r from-blue-50 to-indigo-50 border-b border-blue-100">
            <View className="flex-row items-center justify-between">
              <Text className="text-2xl font-bold text-blue-900">{meal.charAt(0).toUpperCase() + meal.slice(1)}</Text>
              <View className="flex-row items-center gap-2">
                <Pressable
                  onPress={() =>
                    router.push({
                      pathname: "/screens/planner/recipe-picker" as any,
                      params: {
                        date: date.toISOString().split("T")[0],
                        mealType: meal,
                      },
                    } as any)
                  }
                  className="rounded-[20px] bg-blue-600 px-5 py-2.5 active:opacity-80"
                >
                  <Text className="text-sm font-semibold text-white">Add</Text>
                </Pressable>
                <Pressable
                  onPress={() =>
                    router.push({
                      pathname: "/screens/planner/generate-plan" as any,
                      params: {
                        date: date.toISOString().split("T")[0],
                        mode: "single",
                        mealType: meal,
                      },
                    } as any)
                  }
                  className="rounded-[20px] bg-blue-100 px-5 py-2.5 active:opacity-80"
                >
                  <Text className="text-sm font-semibold text-blue-700">Generate</Text>
                </Pressable>
              </View>
            </View>
          </View>

          <View className="px-6 py-4">
            {plans[meal].length === 0 ? (
              <Text className="text-base text-blue-400 italic">No meals added</Text>
            ) : (
              plans[meal].map((item: MealPlanItem) => (
                <View
                  key={item.plan_id}
                  className="flex-row items-center justify-between gap-4 py-3 border-b border-blue-100 last:border-b-0"
                >
                  <Pressable
                    className="flex-1"
                    onPress={() => router.push(`/screens/recipe/${item.recipe_id}`)}
                  >
                    <Text className="text-lg font-semibold text-blue-900">{item.recipe_name}</Text>
                    {item.calories && (
                      <Text className="text-sm text-blue-600 mt-1">{Math.round(item.calories)} kcal</Text>
                    )}
                  </Pressable>
                  <Pressable
                    onPress={() => handleDelete(item.plan_id, meal)}
                    className="rounded-full bg-rose-100 p-2 active:opacity-80"
                  >
                    <Text className="text-base text-rose-500 font-bold">×</Text>
                  </Pressable>
                </View>
              ))
            )}
          </View>
        </View>
      ))}

      <View className="h-6" />
    </ScrollView>
  );
}

