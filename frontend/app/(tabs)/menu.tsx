import { View, Button, Alert } from "react-native";
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
            Alert.alert("Logout Error", "Failed to complete logout process.");
            setAuthenticated(false);
            router.replace("/screens/auth/loginScreen");
        }
    };

    return (
        <View
            style={{
                flex: 1,
                justifyContent: "center",
                alignItems: "center",
                backgroundColor: "darkblue",
                padding: 16
            }}
        >
            <Button
                title="My profile"
                onPress={() => router.push("/screens/menu/profileScreen")}
                color="orange"
            />
            <View style={{marginTop: 20}}>
            <Button
                title="My goals"
                onPress={() => router.push("/screens/menu/goalScreen")}
                color="green"
            />
            </View>
            <View style={{marginTop: 20}}>
            <Button
                title="My ratings"
                onPress={() => router.push("/screens/menu/my-raitings")}
                color="purple"
            />
            </View>
            <View style={{marginTop: 20}}>
            <Button 
                title="Logout" 
                onPress={handleLogout} 
                color="red"
            />
            </View>
        </View>
    );
}