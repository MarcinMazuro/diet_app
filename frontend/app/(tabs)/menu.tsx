import { View, Button, Alert } from "react-native";
import { useRouter } from "expo-router";
import { logoutUser } from "../../services/authService";
import { useAuth } from "../../contexts/AuthContext";

export default function Menu() {
    const router = useRouter();
    const { setAuthenticated } = useAuth();

    const handleLogout = async () => {
        try {
            await logoutUser();
            setAuthenticated(false);
            router.replace("/loginScreen");
        } catch (err) {
            Alert.alert("Logout Error", "Failed to complete logout process.");
            setAuthenticated(false);
            router.replace("/loginScreen");
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
                title="Mój profil"
                onPress={() => router.push("/menu/profileScreen")}
                color="orange"
            />
            <View style={{marginTop: 20}}>
            <Button
                title="Moje cele"
                onPress={() => router.push("/menu/goalScreen")}
                color="green"
            />
            </View>
            <View style={{marginTop: 20}}>
            <Button 
                title="Wyloguj" 
                onPress={handleLogout} 
                color="red"
            />
            </View>
        </View>
    );
}