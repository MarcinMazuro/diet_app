import React, { useEffect, useState } from "react";
import {
  View,
  FlatList,
  ActivityIndicator,
  Text,
  Pressable,
} from "react-native";

import RecipeCard from "@/components/RecipeCard";
import FilterModal from "@/components/FilterModal";
import { getRecipes, Recipe } from "@/services/recipeService";
import SearchBar from "@/components/SearchBar";

export default function RecipesScreen() {
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
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
      setRecipes((prev) => (append ? [...prev, ...data.results] : data.results));
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
    loadRecipes(1, false);
    setFiltersVisible(false);
  };

  const renderFooter = React.useMemo(() => {
    return loadingMore ? <ActivityIndicator className="mt-4" size="small" color="#3b82f6" /> : null;
  }, [loadingMore]);

  const renderItem = React.useCallback(
    ({ item }: { item: Recipe }) => <RecipeCard recipe={item} />,
    []
  );

  return (
    <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 px-4 pt-5">
      <View className="rounded-[36px] bg-white border border-blue-200 shadow-lg p-6 mb-6">
        <View className="gap-4">
          <Text className="text-3xl font-bold text-blue-900">Recipes</Text>
          <Text className="text-base text-blue-600 leading-relaxed">
            Browse our collection of healthy recipes and filter by calories and categories.
          </Text>
        </View>

        <View className="mt-6 gap-4">
          <SearchBar
            onSearch={(query) => {
              setSearchName(query);
              loadRecipes(1, false);
            }}
            initialValue={searchName}
          />
          <Pressable
            onPress={() => setFiltersVisible(true)}
            className="rounded-[28px] bg-blue-600 py-5 items-center justify-center active:opacity-80 shadow-md"
          >
            <Text className="text-lg font-semibold text-white">Filters</Text>
          </Pressable>
        </View>
      </View>

      {loading && page === 1 ? (
        <View className="flex-1 justify-center items-center">
          <ActivityIndicator size="large" color="#3b82f6" />
        </View>
      ) : (
        <FlatList
          data={recipes}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          contentContainerStyle={{ paddingBottom: 24, paddingTop: 16 }}
          onEndReached={loadMore}
          onEndReachedThreshold={0.5}
          initialNumToRender={10}
          maxToRenderPerBatch={10}
          windowSize={5}
          ListFooterComponent={renderFooter}
          removeClippedSubviews
        />
      )}

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
