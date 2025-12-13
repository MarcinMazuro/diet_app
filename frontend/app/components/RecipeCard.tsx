import React from "react";
import { View, Text, Image, StyleSheet } from "react-native";
import { Recipe } from "@/services/recipeService";

const RecipeCard = React.memo(({ recipe }: { recipe: Recipe }) => (
  <View style={styles.card}>
    <Image source={{ uri: recipe.image_url }} style={styles.image} /> 
    <View style={styles.info}>
      <Text style={styles.name}>{recipe.name}</Text>
      <Text style={styles.meta}>
        {recipe.calories} kcal • {recipe.preparation_time} min • {recipe.servings} servings
      </Text>
      {recipe.categories.length > 0 && (
        <Text style={styles.categories}>
          {recipe.categories.map((c) => c.name).join(", ")}
        </Text>
      )}
    </View>
  </View>
));

export default RecipeCard;

const styles = StyleSheet.create({
  card: { backgroundColor: "#fff", borderRadius: 10, overflow: "hidden", marginBottom: 16, elevation: 2 },
  image: { width: "100%", height: 180 },
  info: { padding: 12 },
  name: { fontSize: 16, fontWeight: "bold", marginBottom: 4 },
  meta: { fontSize: 13, color: "#555" },
  categories: { marginTop: 4, fontSize: 12, color: "#888" },
});
