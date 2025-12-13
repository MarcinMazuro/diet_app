import React, { useEffect, useState } from "react";
import {
  View,
  FlatList,
  ActivityIndicator,
  StyleSheet,
} from "react-native";
import RecipeCard from "../components/RecipeCard";
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
  const renderItem = React.useCallback(
    ({ item }: { item: Recipe }) => <RecipeCard recipe={item} />,
    []
  );

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" />
      </View>
    );
  }
  // Render recipe list with infinite scrolling
  return (
    <FlatList
      data={recipes} // Data source for the list
      keyExtractor={(item) => item.id.toString()} // Unique key for each item for choosing purposes and performance
      renderItem={renderItem} // Use memoized renderItem
      contentContainerStyle={styles.list}
      onEndReached={loadMore} // Trigger load more when reaching the end
      onEndReachedThreshold={0.5} // Load more when 50% from bottom
      initialNumToRender={10} // Initial items to render
      maxToRenderPerBatch={10} // Max items to render per batch
      windowSize={5} // Number of items outside of viewport to render
      ListFooterComponent={loadingMore ? <ActivityIndicator style={{ margin: 16 }} /> : null} // Show loading indicator at bottom when loading more
    />
  );
}

const styles = StyleSheet.create({
  list: { padding: 16 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
});