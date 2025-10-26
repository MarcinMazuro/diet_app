import { Stack } from "expo-router";

export default function RootLayout() {
  return (
    <Stack initialRouteName="loginScreen">
      <Stack.Screen name="loginScreen" options={{ headerShown: false }} />
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
    </Stack>
  );
}
