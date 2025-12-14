import React, { useEffect } from "react";
import MaterialCommunityIcons from "@expo/vector-icons/MaterialCommunityIcons";
import Feather from '@expo/vector-icons/Feather';
import { Tabs, useRouter } from "expo-router";
import { ActivityIndicator, View } from "react-native";
import { useAuth } from "@/contexts/AuthContext";

export default function TabsLayout() {
    const router = useRouter();
    const { isAuthenticated, loading } = useAuth();

    useEffect(() => {
        if (!loading && !isAuthenticated) {
            // Navigate to log in screen if not authenticated
            router.replace("/loginScreen");
        }
    }, [loading, isAuthenticated]);

    if (loading) {
        // Wait while checking authentication
        return (
            <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
                <ActivityIndicator size="large" />
            </View>
        );
    }

  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: "coral" }} >
      <Tabs.Screen 
        name="index" 
        options={{
          title: "Home Screen",
          tabBarIcon: ({ color, size }) => (
            <MaterialCommunityIcons name="food-apple" size={size} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="recipes" 
        options={{
            title: "Recipes",
            tabBarIcon: ({ color, size }) => (
                <MaterialCommunityIcons name="food-takeout-box" size={size} color={color} />
            ),


        }}
      />
      <Tabs.Screen 
        name="menu" 
        options={{
            title: "Menu Screen",
            tabBarIcon: ({ color, size }) => (
                <Feather name="menu" size={size} color={color} />
            ),
      }}
      />
    </Tabs>
  );
}
