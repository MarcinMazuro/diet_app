import React, { useEffect, useLayoutEffect, useState } from "react";
import {
  View,
  Text,
  Image,
  ScrollView,
  ActivityIndicator,
  StyleSheet,
  Pressable,
} from "react-native";
import { useLocalSearchParams, useNavigation } from "expo-router";
import { getRecipeById, RecipeDetails } from "@/services/recipeDetailsService";
// Import rating service and RatingStars component
import RatingStars from "@/app/components/RatingStars";
import {
  getRating,
  createRating,
  updateRating,
  deleteRating,
} from "@/services/ratingService";
import { useRouter } from "expo-router";

export default function RecipeDetailsScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const navigation = useNavigation();

  const [recipe, setRecipe] = useState<RecipeDetails | null>(null);
  const [loading, setLoading] = useState(true);
  // Rating state
  const [rating, setRating] = useState<number | null>(null);
  const [ratingLoading, setRatingLoading] = useState(true);


  const loadData = async () => {
    if (!id) return;
    setLoading(true);
    setRatingLoading(true);
    try {
      const recipeData = await getRecipeById(id);
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

  // Handle rating change
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

// Handle rating deletion
const handleDeleteRating = async () => {
  if (!recipe) return;
  setRatingLoading(true);
  try {
    await deleteRating(recipe.id);

    setRating(null);  // reset rating state
    //await loadData();
  } catch (e) {
    console.error(e);
  } finally {
    setRatingLoading(false);

  }
};
  // Change header title to recipe name
  useLayoutEffect(() => {
    if (recipe) {
      navigation.setOptions({
        title: recipe.name,
      });
    }
  }, [navigation, recipe]);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }
 // Show message if recipe not found (id is invalid)
  if (!recipe) {
    return (
      <View style={styles.center}>
        <Text>Recipe not found</Text>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.container}>

    <View>
      {ratingLoading ? (
        <ActivityIndicator />
      ) : (
        <>
          <RatingStars value={rating ?? 0} onChange={handleRate} disabled={ratingLoading} />

          {rating !== null && (

            <Pressable onPress={handleDeleteRating}>
              <Text style={{ color: "red", marginTop: 8 }}>
                Remove rating
              </Text>
            </Pressable>
            
          )}
        </>
      )}
    </View>


      <Image source={{ uri: recipe.image_url }} style={styles.image} />

      <Text style={styles.sectionTitle}>Description</Text>
      <Text style={styles.text}>{recipe.description}</Text>

      <Text style={styles.sectionTitle}>Ingredients</Text>
      {recipe.ingredients.map((i, idx) => (
        <Text key={idx} style={styles.listItem}>• {i}</Text>
      ))}

      <Text style={styles.sectionTitle}>Directions</Text>
      {recipe.directions.map((d, idx) => (
        <Text key={idx} style={styles.listItem}>
          {idx + 1}. {d}
        </Text>
      ))}

      <Text style={styles.sectionTitle}>Nutrition</Text>
      <Text style={styles.text}>
        Calories: {recipe.calories} kcal{"\n"}
        Protein: {recipe.protein} g{"\n"}
        Fat: {recipe.fat} g{"\n"}
        Carbs: {recipe.carbohydrate} g{"\n"}
        Sugar: {recipe.sugar} g
      </Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 16 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  image: { width: "100%", height: 220, borderRadius: 12, marginBottom: 16 },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    marginTop: 16,
    marginBottom: 8,
  },
  text: { fontSize: 14, color: "#444" },
  listItem: { fontSize: 14, marginBottom: 4 },
});
