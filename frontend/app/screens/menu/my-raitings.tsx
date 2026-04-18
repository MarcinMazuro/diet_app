
import { View, Text, FlatList, Pressable, ActivityIndicator } from "react-native";
import { useEffect, useState } from "react";
import { useRouter } from "expo-router";
import { getMyRatings, MyRating } from "@/services/myRatingsService";

export default function MyRatingsScreen() {
  const [ratings, setRatings] = useState<MyRating[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const load = async () => {
      try {
        const data = await getMyRatings();
        setRatings(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  if (loading) {
    return (
      <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 justify-center items-center">
        <ActivityIndicator size="large" color="#3b82f6" />
      </View>
    );
  }

  if (ratings.length === 0) {
    return (
      <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 justify-center items-center p-6">
        <Text className="text-base text-blue-500">You have no ratings yet.</Text>
      </View>
    );
  }

  return (
    <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100">
      <FlatList
        data={ratings}
        keyExtractor={(item) => item.recipe_id.toString()}
        contentContainerStyle={{ padding: 20, paddingBottom: 24 }}
        renderItem={({ item }) => (
          <Pressable
            onPress={() => router.push(`/screens/recipe/${item.recipe_id}`)}
            className="rounded-[36px] bg-white border border-blue-200 shadow-lg p-6 mb-5 active:opacity-80"
          >
            <Text className="text-lg font-semibold text-blue-900">{item.recipe_name}</Text>
            <Text className="mt-3 text-base text-blue-600">Rating: {item.rating} ⭐</Text>
          </Pressable>
        )}
      />
    </View>
  );
}
