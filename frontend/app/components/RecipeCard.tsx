import React from "react";
import { View, Text, Image, StyleSheet } from "react-native";
import { Recipe } from "@/services/recipeService";
import {Pressable} from "react-native";
import {useRouter} from "expo-router";

const RecipeCard = React.memo(({ recipe }: { recipe: Recipe }) => {
  const router = useRouter();
// Pressable routes to recipe details on press and sends recipe id as param
  return (
    <Pressable
      onPress={() =>
        router.push({
          pathname: "/recipes/[id]",
          params: { id: recipe.id.toString() },
        })
      }
      style={({ pressed }) => [
        styles.card,
        pressed && { opacity: 0.85 },
      ]}
    >
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
    </Pressable>
  );
});


export default RecipeCard;

const styles = StyleSheet.create({
  card: { backgroundColor: "#fff", borderRadius: 10, overflow: "hidden", marginBottom: 16, elevation: 2 },
  image: { width: "100%", height: 180 },
  info: { padding: 12 },
  name: { fontSize: 16, fontWeight: "bold", marginBottom: 4 },
  meta: { fontSize: 13, color: "#555" },
  categories: { marginTop: 4, fontSize: 12, color: "#888" },
});
