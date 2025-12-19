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
    return <ActivityIndicator style={{ marginTop: 40 }} />;
  }

  if (ratings.length === 0) {
    return <Text style={{ padding: 16 }}>You have no ratings yet.</Text>;
  }

  return (
    <FlatList
      data={ratings}
      keyExtractor={(item) => item.recipe_id.toString()}
      renderItem={({ item }) => (
        <Pressable
          onPress={() => router.push(`/screens/recipe/${item.recipe_id}`)}
          style={{ padding: 16, borderBottomWidth: 1 }}
        >
          <Text style={{ fontWeight: "bold" }}>{item.recipe_name}</Text>
          <Text>Rating: {item.rating} ⭐</Text>
        </Pressable>
      )}
    />
  );
}
