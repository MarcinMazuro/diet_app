import { Text, View, Button, Alert } from "react-native";
import { useRouter } from 'expo-router'; 
import { logoutUser } from '../../services/authService'; 

export default function Menu() {
    const router = useRouter(); 

    const handleLogout = async () => {
        try {
            await logoutUser();

            router.replace('/loginScreen'); 
        } catch (err) {

            Alert.alert('Logout Error', 'Failed to complete logout process.');
            router.replace('/');
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
           
            
            {/* Przycisk Wyloguj */}
            <Button 
                title="Wyloguj" 
                onPress={handleLogout} 
                color="red"
            />
        </View>
    );
}