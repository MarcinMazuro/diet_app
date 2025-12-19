import React, { useEffect, useState } from "react";
import {
  View,
  FlatList,
  ActivityIndicator,
  TextInput,
  Button,
  Modal,
  Text,
  StyleSheet,
} from "react-native";
import RecipeCard from "@/components/RecipeCard";
import FilterModal from "@/components/FilterModal";
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

  const [searchName, setSearchName] = useState("");
  const [filtersVisible, setFiltersVisible] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | undefined>();
  const [minCalories, setMinCalories] = useState<number | undefined>();
  const [maxCalories, setMaxCalories] = useState<number | undefined>();


  const PAGE_SIZE = 10;

  const loadRecipes = async (pageToLoad = 1, append = false) => {
    try {
      pageToLoad === 1 ? setLoading(true) : setLoadingMore(true);

      const data = await getRecipes({
        page: pageToLoad,
        pageSize: PAGE_SIZE,
        ordering: "name",
        name: searchName || undefined,
        category: selectedCategory,
        minCalories,
        maxCalories,
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
    loadRecipes(1, false);
  }, [selectedCategory, minCalories, maxCalories]);

  const loadMore = () => {
    if (!loadingMore && hasNext) {
      // Dynamicly load next page
      loadRecipes(page + 1, true);
    }
  };

  // Handle applying filters from modal
  const handleApplyFilters = (category?: string, min?: number, max?: number) => {
    setSelectedCategory(category);
    setMinCalories(min);
    setMaxCalories(max);
    setFiltersVisible(false);
  };
  // Handle resetting filters from modal
  const handleResetFilters = () => {
  setSelectedCategory(undefined);
  setMinCalories(undefined);
  setMaxCalories(undefined);
  loadRecipes(1, false);
  setFiltersVisible(false);
};

  // Handle search button press
  const handleSearch = () => {
    loadRecipes(1, false);
  };

  // Render individual recipe item
  const renderItem = React.useCallback(
    ({ item }: { item: Recipe }) => <RecipeCard recipe={item} />,
    []
  );


  // Render recipe list with infinite scrolling
   return (
    <View style={{ flex: 1 }}>
      {/* Search bar */}
      <View style={styles.searchContainer}>
        <TextInput
          placeholder="Search recipes..."
          value={searchName}
          onChangeText={setSearchName}
          style={styles.searchInput}
          returnKeyType="search"
          onSubmitEditing={handleSearch}
        />
        <View style={{ flexDirection: "row", gap: 8 }}>
        <Button title="Search" onPress={handleSearch} />
        
        <Button title="Filters" onPress={() => setFiltersVisible(true)} />
        </View>
      </View>

      {/* Recipes list */}
    {loading && page === 1 ? ( 
      // Show loading indicator when loading first page
        <View style={styles.center}>
          <ActivityIndicator size="large" />
        </View>
      ) : (
    // Infinite scrolling list of recipes
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
      ListFooterComponent={
        loadingMore ? <ActivityIndicator style={{ margin: 16 }} /> : null
      } // Show loading indicator at bottom when loading more
    />
  )}

      {/* Filters modal */}
      <FilterModal
        visible={filtersVisible}
        onApply={handleApplyFilters}
        onReset={handleResetFilters}
        selectedCategory={selectedCategory}
        minCalories={minCalories}
        maxCalories={maxCalories}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  list: { padding: 16 },
  center: { flex: 1, justifyContent: "center", alignItems: "center" },
  searchContainer: {
    flexDirection: "row",
    padding: 8,
    alignItems: "center",
    justifyContent: "space-between",
  },
  searchInput: {
    flex: 1,
    borderWidth: 1,
    borderRadius: 6,
    padding: 8,
    marginRight: 8,
  },
});