import "../global.css";
import { Stack } from "expo-router";
import { AuthProvider } from "../contexts/AuthContext";

export default function RootLayout() {
    return (
        <AuthProvider>
            <Stack>
                <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
                <Stack.Screen name="screens/menu/profileScreen" options={{
                    title: "Profile",
                    headerShown: true,
                    headerBackTitle: "Go back",
                }} />
                <Stack.Screen name="screens/menu/goalScreen" options={{
                    title: "Goals",
                    headerShown: true,
                    headerBackTitle: "Go back",
                }} />
            </Stack>
        </AuthProvider>
    );
}