import { Stack } from "expo-router";
import { AuthProvider } from "../contexts/AuthContext";



export default function RootLayout() {
    return (
        <AuthProvider>
            <Stack>
                <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
                <Stack.Screen name="menu/profileScreen" options={{
                    title: "My Profile",
                    headerShown: true,
                    headerBackTitle: "Go back",
                }} />
            </Stack>
        </AuthProvider>
    );
}