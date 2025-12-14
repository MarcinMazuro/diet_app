import React, { useEffect, useLayoutEffect, useState } from "react";
import {
  View,
  Text,
  Image,
  ScrollView,
  ActivityIndicator,
  StyleSheet,
} from "react-native";
import { useLocalSearchParams, useNavigation } from "expo-router";
import { getRecipeById, RecipeDetails } from "@/services/recipeDetailsService";

export default function RecipeDetailsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const navigation = useNavigation();

  const [recipe, setRecipe] = useState<RecipeDetails | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
// Fetch recipe details by ID
    getRecipeById(id)
      .then(setRecipe)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [id]);

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
