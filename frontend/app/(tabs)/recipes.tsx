import React, { useEffect, useState } from "react";
import {
  View,
  Text,
  FlatList,
  Image,
  ActivityIndicator,
  StyleSheet,
  TouchableOpacity,
} from "react-native";

import { getRecipes, Recipe } from "@/services/recipeService";

export default function RecipesScreen() {
  // All loaded pages (dynamicly expanded)
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  // Load first page on mount
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  // If there is a next page
  const [hasNext, setHasNext] = useState(true);

  const PAGE_SIZE = 10;

  const loadRecipes = async (pageToLoad = 1, append = false) => {
    try {
      pageToLoad === 1 ? setLoading(true) : setLoadingMore(true);

      const data = await getRecipes({
        page: pageToLoad,
        pageSize: PAGE_SIZE,
        ordering: "name",
      });

      setHasNext(Boolean(data.next));
      setPage(pageToLoad);

      setRecipes((prev) =>
        append ? [...prev, ...data.results] : data.results
      );
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  useEffect(() => {
    loadRecipes();
  }, []);

  const loadMore = () => {
    if (!loadingMore && hasNext) {
      // Dynamicly load next page
      loadRecipes(page + 1, true);
    }
  };
  // Render individual recipe item
  const renderItem = ({ item }: { item: Recipe }) => (
    <View style={styles.card}>
      <Image source={{ uri: item.image_url }} style={styles.image} />
      <View style={styles.info}>
        <Text style={styles.name}>{item.name}</Text>
        <Text style={styles.meta}>
          {item.calories} kcal • {item.preparation_time} min • {item.servings} servings
        </Text>
        {item.categories.length > 0 && (
          <Text style={styles.categories}>
            {item.categories.map((c) => c.name).join(", ")}
          </Text>
        )}
      </View>
    </View>
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <FlatList
      data={recipes}
      keyExtractor={(item) => item.id.toString()}
      renderItem={renderItem}
      contentContainerStyle={styles.list}
      onEndReached={loadMore}
      onEndReachedThreshold={0.5}
      ListFooterComponent={
        loadingMore ? <ActivityIndicator style={{ margin: 16 }} /> : null
      }
    />
  );
}

const styles = StyleSheet.create({
  list: {
    padding: 16,
  },
  center: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
  },
  card: {
    backgroundColor: "#fff",
    borderRadius: 10,
    overflow: "hidden",
    marginBottom: 16,
    elevation: 2,
  },
  image: {
    width: "100%",
    height: 180,
  },
  info: {
    padding: 12,
  },
  name: {
    fontSize: 16,
    fontWeight: "bold",
    marginBottom: 4,
  },
  meta: {
    fontSize: 13,
    color: "#555",
  },
  categories: {
    marginTop: 4,
    fontSize: 12,
    color: "#888",
  },
});
