import { View, Text, Pressable, ActivityIndicator, ScrollView } from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import {
  generateMeal,
  generateDailyPlan,
  MealType,
} from "@/services/mealPlanService";
import { useState } from "react";

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
    <ScrollView className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <View className="rounded-[36px] bg-white border border-blue-200 shadow-lg p-8 gap-8">
        <View className="items-center gap-4">
          <View className="w-16 h-16 rounded-full bg-blue-100 items-center justify-center">
            <Text className="text-3xl">🍽️</Text>
          </View>
          <Text className="text-4xl font-bold text-blue-900 text-center">Generate Meal Plan</Text>
          <Text className="text-lg text-blue-600 text-center leading-relaxed">
            Let AI create a personalized meal plan for your selected date and preferences.
          </Text>
        </View>

        <View className="bg-blue-50 rounded-[28px] p-6 gap-6">
          <View className="flex-row justify-between items-center">
            <Text className="text-lg font-semibold text-blue-900">Date</Text>
            <Text className="text-lg text-blue-700">{date}</Text>
          </View>
          <View className="flex-row justify-between items-center">
            <Text className="text-lg font-semibold text-blue-900">Mode</Text>
            <Text className="text-lg text-blue-700">
              {mode === "daily" ? "Full Day Plan" : `${mealType?.toUpperCase()} Meal`}
            </Text>
          </View>
        </View>

        {loading && (
          <View className="items-center gap-4">
            <ActivityIndicator size="large" color="#3b82f6" />
            <Text className="text-lg text-blue-600">Generating your perfect meal plan...</Text>
          </View>
        )}

        {!done ? (
          <Pressable
            className="rounded-[28px] bg-blue-600 py-16 items-center shadow-md active:opacity-80"
            onPress={handleGenerate}
            disabled={loading}
          >
            <Text className="text-2xl font-bold text-white">Generate Plan</Text>
          </Pressable>
        ) : (
          <View className="items-center gap-6">
            <View className="w-16 h-16 rounded-full bg-green-100 items-center justify-center">
              <Text className="text-3xl">✅</Text>
            </View>
            <Text className="text-xl font-semibold text-green-700 text-center">
              Your meal plan has been generated successfully!
            </Text>
            <Pressable
              className="rounded-[28px] bg-blue-600 py-5 px-8 shadow-md active:opacity-80"
              onPress={() => router.back()}
            >
              <Text className="text-lg font-semibold text-white">View My Plan</Text>
            </Pressable>
          </View>
        )}
      </View>
    </ScrollView>
  );
}
