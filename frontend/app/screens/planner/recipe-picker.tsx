import { useEffect, useState, useCallback } from "react";
import { View, FlatList, Text, Pressable, ActivityIndicator } from "react-native";
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
        onPress={() =>
          router.push({
            pathname: `/screens/recipe/${item.id}` as any,
            params: {
              fromPlanner: "true",
              date,
              mealType,
            },
          } as any)
        }
        className="mb-4 rounded-[32px] bg-white border border-blue-200 shadow-lg overflow-hidden active:opacity-80"
      >
        <View className="p-5">
          <View className="flex-row justify-between items-start gap-4">
            <View className="flex-1">
              <Text className="text-xl font-bold text-blue-900 leading-tight">{item.name}</Text>
              {item.calories && (
                <Text className="text-base text-blue-600 mt-2">{Math.round(item.calories)} kcal</Text>
              )}
            </View>
          </View>

          {item.description && (
            <Text className="text-sm text-blue-700 leading-relaxed mt-3" numberOfLines={2}>
              {item.description}
            </Text>
          )}
          
          <Text className="text-xs text-blue-500 mt-3">Tap for details</Text>
        </View>
      </Pressable>
    ),
    [date, mealType, router]
  );

  if (loading && page === 1) {
    return (
      <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 justify-center items-center">
        <ActivityIndicator size="large" color="#3b82f6" />
      </View>
    );
  }

  return (
    <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <SearchBar onSearch={setSearch} initialValue={search} />

      <Pressable
        className="mb-4 rounded-[28px] bg-white border border-blue-200 py-5 items-center shadow-sm"
        onPress={() => setFiltersVisible(true)}
      >
        <Text className="text-lg font-semibold text-blue-700">Filters</Text>
      </Pressable>

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
        contentContainerStyle={{ paddingBottom: 24 }}
        ListFooterComponent={
          loadingMore ? (
            <ActivityIndicator className="my-4" size="small" color="#3b82f6" />
          ) : null
        }
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
