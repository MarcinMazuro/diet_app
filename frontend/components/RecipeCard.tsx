import React from "react";
import { View, Text, Image, Pressable } from "react-native";
import { Recipe } from "@/services/recipeService";
import { useRouter } from "expo-router";

const RecipeCard = React.memo(({ recipe }: { recipe: Recipe }) => {
  const router = useRouter();
  return (
    <Pressable
      onPress={() => router.push(`/screens/recipe/${recipe.id}`)}
      className="mb-5 overflow-hidden rounded-[36px] bg-white shadow-lg border border-blue-200"
      style={({ pressed }) => ({ opacity: pressed ? 0.85 : 1 })}
    >
      <Image source={{ uri: recipe.image_url }} className="h-48 w-full" />

      <View className="p-6">
        <Text className="text-lg font-semibold text-blue-900 mb-2">{recipe.name}</Text>

        <Text className="text-base text-blue-600 mb-3">
          {recipe.calories} kcal • {recipe.preparation_time} min • {recipe.servings} servings
        </Text>

        {recipe.categories.length > 0 && (
          <Text className="text-sm text-blue-500">
            {recipe.categories.map((c) => c.name).join(", ")}
          </Text>
        )}
      </View>
    </Pressable>
  );
});

export default React.memo(RecipeCard);
