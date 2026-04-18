
import { View, Text, Pressable, Alert } from "react-native";
import { useRouter } from "expo-router";
import { logoutUser } from "@/services/authService";
import { useAuth } from "@/contexts/AuthContext";

export default function Menu() {
  const router = useRouter();
  const { setAuthenticated } = useAuth();

  const handleLogout = async () => {
    try {
      await logoutUser();
      setAuthenticated(false);
      router.replace("/screens/auth/loginScreen");
    } catch (err) {
      Alert.alert("Logout Error", "Failed to end session.");
      setAuthenticated(false);
      router.replace("/screens/auth/loginScreen");
    }
  };

  return (
    <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100 px-6 py-8">
      <View className="rounded-[36px] bg-white border border-blue-200 shadow-lg p-8 gap-6">
        <View className="gap-3">
          <Text className="text-3xl font-bold text-blue-900 tracking-tight">Menu</Text>
          <Text className="text-base text-blue-600 leading-relaxed">
            Quick access to your profile, goals, and ratings.
          </Text>
        </View>

        <View className="gap-4">
          <Pressable
            onPress={() => router.push("/screens/menu/profileScreen")}
            className="rounded-[28px] bg-blue-50 px-6 py-5 active:opacity-80"
          >
            <Text className="text-lg font-semibold text-blue-900">My Profile</Text>
          </Pressable>

          <Pressable
            onPress={() => router.push("/screens/menu/goalScreen")}
            className="rounded-[28px] bg-blue-50 px-6 py-5 active:opacity-80"
          >
            <Text className="text-lg font-semibold text-blue-900">My Goals</Text>
          </Pressable>

          <Pressable
            onPress={() => router.push("/screens/menu/my-raitings")}
            className="rounded-[28px] bg-blue-50 px-6 py-5 active:opacity-80"
          >
            <Text className="text-lg font-semibold text-blue-900">Ratings</Text>
          </Pressable>
        </View>

        <Pressable
          onPress={handleLogout}
          className="rounded-[28px] bg-red-500 py-5 items-center justify-center active:opacity-80 shadow-md"
        >
          <Text className="text-lg font-semibold text-white">Sign Out</Text>
        </Pressable>
      </View>
    </View>
  );
}