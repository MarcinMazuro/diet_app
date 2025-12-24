import React, { useEffect, useState, useCallback } from "react";
import { View, FlatList, Text, Pressable, ActivityIndicator, StyleSheet, Button } from "react-native";
import { useRouter, useLocalSearchParams } from "expo-router";
import { getRecipes, Recipe } from "@/services/recipeService";
import FilterModal from "@/components/FilterModal";
import SearchBar from "@/components/SearchBar";
const PAGE_SIZE = 20;

export default function RecipePickerScreen() {
  const router = useRouter();
  const { date, mealType } = useLocalSearchParams<{ date: string; mealType: string }>();

  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [page, setPage] = useState(1);
  const [hasNext, setHasNext] = useState(true);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);

  const [search, setSearch] = useState("");
  const [filtersVisible, setFiltersVisible] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string>();
  const [minCalories, setMinCalories] = useState<number>();
  const [maxCalories, setMaxCalories] = useState<number>();

  const loadRecipes = async (pageToLoad = 1, append = false) => {
    try {
      pageToLoad === 1 ? setLoading(true) : setLoadingMore(true);

      const data = await getRecipes({
        page: pageToLoad,
        pageSize: PAGE_SIZE,
        name: search || undefined,
        ordering: "name",
        category: selectedCategory,
        minCalories,
        maxCalories,
      });

      setHasNext(Boolean(data.next));
      setPage(pageToLoad);
      setRecipes((prev) => (append ? [...prev, ...data.results] : data.results));
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };



  useEffect(() => {
    loadRecipes(1, false);
  }, [search, selectedCategory, minCalories, maxCalories]);

  const loadMore = () => {
    if (!loadingMore && hasNext) {
      loadRecipes(page + 1, true);
    }
  };

  const handleApplyFilters = (category?: string, min?: number, max?: number) => {
    setSelectedCategory(category);
    setMinCalories(min);
    setMaxCalories(max);
    setFiltersVisible(false);
  };

  const handleResetFilters = () => {
    setSelectedCategory(undefined);
    setMinCalories(undefined);
    setMaxCalories(undefined);
    setFiltersVisible(false);
  };

  const renderItem = useCallback(
    ({ item }: { item: Recipe }) => (
      <Pressable
        style={styles.row}
        onPress={() => router.push(`/screens/recipe/${item.id}`)}
      >
        <View style={{ flex: 1 }}>
          <Text style={styles.name}>{item.name}</Text>
          <Text style={styles.meta}>{item.calories} kcal • {item.preparation_time} min</Text>
        </View>

        <Pressable
          onPress={() =>
            router.push({
              pathname: "/screens/planner/confirm-add",
              params: { recipeId: item.id.toString(),recipeName:item.name, date, mealType },
            })
          }
        >
          <Text style={styles.add}>＋</Text>
        </Pressable>
      </Pressable>
    ),
    [date, mealType]
  );

  if (loading && page === 1) return <ActivityIndicator style={{ marginTop: 40 }} />;

  return (
    <View style={styles.container}>
      <SearchBar onSearch={setSearch} initialValue={search} />
      <Button title="Filters" onPress={() => setFiltersVisible(true)} />

      <FlatList
        data={recipes}
        keyExtractor={(item) => item.id.toString()}
        renderItem={renderItem}
        onEndReached={loadMore}
        onEndReachedThreshold={0.5}
        initialNumToRender={10}
        maxToRenderPerBatch={10}
        windowSize={5}
        removeClippedSubviews
        ListFooterComponent={loadingMore ? <ActivityIndicator style={{ margin: 16 }} /> : null}
      />

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
  container: { flex: 1, padding: 12 },
  row: { flexDirection: "row", alignItems: "center", paddingVertical: 12, borderBottomWidth: 1, borderColor: "#eee" },
  name: { fontSize: 16, fontWeight: "500" },
  meta: { fontSize: 12, color: "#666" },
  add: { fontSize: 26, color: "green", paddingHorizontal: 12 },
});
