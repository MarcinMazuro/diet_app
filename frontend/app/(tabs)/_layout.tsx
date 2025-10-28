import React, { useEffect, useState } from 'react';
import MaterialCommunityIcons from '@expo/vector-icons/MaterialCommunityIcons';
import { Tabs } from "expo-router";
import { useRouter } from "expo-router";
import * as SecureStore from "expo-secure-store";
import { ActivityIndicator, View } from 'react-native';

export default function TabsLayout() {
  const router = useRouter();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const token = await SecureStore.getItemAsync("accessToken");
        if (!token) {
          router.replace("/loginScreen"); 
        }
      } catch {
        router.replace("/loginScreen"); 
      } finally {
        setChecking(false);
      }
    })();
  }, []);

  if (checking) {
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
            <MaterialCommunityIcons name="food-apple" size={24} color={color} />
          ),
        }}
      />
      <Tabs.Screen 
        name="test" 
        options={{ title: "Test Screen" }}
      />
    </Tabs>
  );
}
