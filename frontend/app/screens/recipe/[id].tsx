import React, { useEffect, useLayoutEffect, useState } from "react";
import {
  View,
  Text,
  Image,
  ScrollView,
  ActivityIndicator,
  Pressable,
} from "react-native";
import { useLocalSearchParams, useNavigation, useRouter } from "expo-router";
import { getRecipeById, RecipeDetails } from "@/services/recipeDetailsService";
import RatingStars from "@/components/RatingStars";
import {
  getRating,
  createRating,
  updateRating,
  deleteRating,
} from "@/services/ratingService";
import { addMealToPlan, MealType } from "@/services/mealPlanService";
import { API_URL } from "@/config/api"; 

export default function RecipeDetailsScreen() {
  const { id, fromPlanner, date, mealType } = useLocalSearchParams<{ id: string; fromPlanner?: string; date?: string; mealType?: string }>();
  const navigation = useNavigation();
  const router = useRouter();

  const [recipe, setRecipe] = useState<RecipeDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [rating, setRating] = useState<number | null>(null);
  const [ratingLoading, setRatingLoading] = useState(true);
  const [addingToMeal, setAddingToMeal] = useState(false);

  const isFromPlanner = fromPlanner === "true";

  const loadData = async () => {
    if (!id) return;
    setLoading(true);
    setRatingLoading(true);
    try {
      const recipeData = await getRecipeById(id as string);
      
      // FIX: Naprawiamy ucięty URL prosto z backendu, zanim trafi do stanu.
      // Dzięki temu w strukturze widoku (JSX) mamy czysty kod, identyczny z RecipeCard.
      if (recipeData.image_url && !recipeData.image_url.startsWith("http")) {
        const baseUrl = API_URL.endsWith("/") ? API_URL.slice(0, -1) : API_URL;
        const path = recipeData.image_url.startsWith("/") ? recipeData.image_url : `/${recipeData.image_url}`;
        recipeData.image_url = `${baseUrl}${path}`;
      }

      setRecipe(recipeData);
      
      const ratingData = await getRating(recipeData.id);
      setRating(ratingData?.rating ?? null);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
      setRatingLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleRate = async (value: number) => {
    if (!recipe) return;
    setRatingLoading(true);
    try {
      if (rating === null) {
        await createRating(recipe.id, value);
      } else {
        await updateRating(recipe.id, value);
      }
      setRating(value);
    } catch (e) {
      console.error(e);
    } finally {
      setRatingLoading(false);
    }
  };

  const handleDeleteRating = async () => {
    if (!recipe) return;
    setRatingLoading(true);
    try {
      await deleteRating(recipe.id);
      setRating(null);
    } catch (e) {
      console.error(e);
    } finally {
      setRatingLoading(false);
    }
  };

  const handleAddToMeal = async () => {
    if (!recipe || !date || !mealType) return;
    setAddingToMeal(true);
    try {
      await addMealToPlan({
        recipeId: recipe.id,
        date,
        mealType: mealType as MealType,
      });
      router.back();
    } catch (e) {
      console.error(e);
      alert("Failed to add meal");
    } finally {
      setAddingToMeal(false);
    }
  };

  useLayoutEffect(() => {
    if (recipe) {
      navigation.setOptions({ title: recipe.name });
    }
  }, [navigation, recipe]);

  if (loading) {
    return (
      <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 justify-center items-center">
        <ActivityIndicator size="large" color="#3b82f6" />
      </View>
    );
  }

  if (!recipe) {
    return (
      <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 justify-center items-center px-6">
        <Text className="text-base text-blue-500">Recipe not found</Text>
      </View>
    );
  }

  return (
    <ScrollView className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100" contentContainerStyle={{ padding: 20 }}>
      <View className="rounded-[36px] bg-white border border-blue-200 shadow-lg p-6 mb-6">
        <View className="mb-5 gap-4">
          <Text className="text-4xl font-black text-blue-900">{recipe.name}</Text>
          <Text className="text-base text-blue-600">Healthy recipe with quick instructions and full nutritional values.</Text>
        </View>

        {/* IDENTYCZNIE JAK W RECIPE CARD */}
        {/* TWARDO WYMUSZONE WYMIARY I ADRES */}
        <View style={{ marginBottom: 24, borderRadius: 32, overflow: "hidden", backgroundColor: "#dbeafe" }}>
          {recipe.image_url ? (
            <Image 
              source={{ 
                uri: recipe.image_url.startsWith("http") 
                  ? recipe.image_url 
                  : `${API_URL}${recipe.image_url.startsWith("/") ? "" : "/"}${recipe.image_url}` 
              }} 
              style={{ width: "100%", height: 300 }} // To ratuje sytuację!
              resizeMode="cover"
            />
          ) : (
            <View style={{ height: 300, justifyContent: "center", alignItems: "center" }}>
              <Text>Brak zdjęcia</Text>
            </View>
          )}
        </View>

        <View className="mb-6 gap-4">
          {isFromPlanner ? (
            <Pressable
              onPress={handleAddToMeal}
              disabled={addingToMeal}
              className="rounded-[28px] bg-blue-600 py-6 items-center shadow-md active:opacity-80"
            >
              {addingToMeal ? (
                <ActivityIndicator size="small" color="#ffffff" />
              ) : (
                <Text className="text-xl font-bold text-white">Add to Plan</Text>
              )}
            </Pressable>
          ) : (
            <>
              {ratingLoading ? (
                <ActivityIndicator size="small" color="#3b82f6" />
              ) : (
                <>
                  <RatingStars value={rating ?? 0} onChange={handleRate} disabled={ratingLoading} />
                  {rating !== null && (
                    <Pressable onPress={handleDeleteRating} className="mt-3">
                      <Text className="text-sm font-semibold text-rose-500">Remove rating</Text>
                    </Pressable>
                  )}
                </>
              )}
            </>
          )}
        </View>
      </View>

      <View className="rounded-[36px] bg-white border border-blue-200 shadow-lg p-6 mb-6 gap-5">
        <View>
          <Text className="text-2xl font-bold text-blue-900">Description</Text>
          <Text className="mt-3 text-base leading-7 text-blue-700">{recipe.description}</Text>
        </View>

        <View>
          <Text className="text-2xl font-bold text-blue-900">Ingredients</Text>
          {recipe.ingredients.map((ingredient, idx) => (
            <Text key={idx} className="mt-3 text-base text-blue-700">• {ingredient}</Text>
          ))}
        </View>

        <View>
          <Text className="text-2xl font-bold text-blue-900">Preparation</Text>
          {recipe.directions.map((direction, idx) => (
            <Text key={idx} className="mt-3 text-base leading-7 text-blue-700">
              {idx + 1}. {direction}
            </Text>
          ))}
        </View>
      </View>

      <View className="rounded-[32px] bg-white border border-slate-100 shadow-sm p-5 gap-3">
        <Text className="text-xl font-bold text-slate-800">Wartości odżywcze</Text>
        <Text className="text-sm leading-6 text-slate-600">
          Kalorie: <Text className="font-semibold text-slate-800">{recipe.calories} kcal</Text>
        </Text>
        <Text className="text-sm leading-6 text-slate-600">Białko: {recipe.protein} g</Text>
        <Text className="text-sm leading-6 text-slate-600">Tłuszcz: {recipe.fat} g</Text>
        <Text className="text-sm leading-6 text-slate-600">Węglowodany: {recipe.carbohydrate} g</Text>
        <Text className="text-sm leading-6 text-slate-600">Cukier: {recipe.sugar} g</Text>
      </View>
    </ScrollView>
  );
}