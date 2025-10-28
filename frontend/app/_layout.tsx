import { Stack } from "expo-router";

export default function RootLayout() {
  return (
    <Stack initialRouteName="(tabs)">
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="loginScreen" options={{ headerShown: false }} />
      <Stack.Screen name="register" options={{ 
        headerShown: true,
        headerTitle: "Register",
        headerBackTitle: "Back"
      }} />
    </Stack>
  );
}
