
import { View, Text, Pressable, ActivityIndicator } from "react-native";
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
    <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 p-6 justify-center">
      <View className="rounded-[36px] bg-white border border-blue-200 shadow-lg p-8 mb-8">
        <Text className="text-3xl font-bold text-blue-900 text-center mb-8">
          Add meal to planner
        </Text>

        <View className="rounded-[32px] bg-blue-50 border border-blue-200 p-6 mb-8">
          <Text className="text-sm uppercase tracking-widest font-semibold text-blue-500 mt-2">
            Recipe
          </Text>
          <Text className="text-lg font-medium text-blue-900 mt-3">
            {recipeName}
          </Text>

          <Text className="text-sm uppercase tracking-widest font-semibold text-blue-500 mt-6">
            Date
          </Text>
          <Text className="text-lg font-medium text-blue-900 mt-3">{date}</Text>

          <Text className="text-sm uppercase tracking-widest font-semibold text-blue-500 mt-6">
            Meal type
          </Text>
          <Text className="text-lg font-medium text-blue-900 mt-3">{mealType}</Text>
        </View>

        {loading ? (
          <View className="items-center">
            <ActivityIndicator size="large" color="#3b82f6" />
          </View>
        ) : (
          <View className="flex-row justify-between gap-4">
            <Pressable
              className="flex-1 rounded-[28px] border border-blue-300 bg-white py-5 items-center shadow-md"
              onPress={() => router.back()}
            >
              <Text className="text-lg font-medium text-blue-600">Cancel</Text>
            </Pressable>
            <Pressable
              className="flex-1 rounded-[28px] bg-blue-600 py-5 items-center shadow-md"
              onPress={handleConfirm}
            >
              <Text className="text-lg font-semibold text-white">Add</Text>
            </Pressable>
          </View>
        )}
      </View>
    </View>
  );
}
