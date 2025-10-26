import React, { useState } from 'react';
import { View, TextInput, Button, Text, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
// Importujemy funkcję logowania z serwisu
import { loginUser } from '../services/authService';


export default function LoginScreen() {
  const router = useRouter();

  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('Błąd', 'Wypełnij wszystkie pola');
      return;
    }

    setLoading(true);
    
    try {
      await loginUser(username, password);
      // Przekierowanie po udanym logowaniu
      router.replace('/(tabs)');
      
    } catch (err) {
      //Obsługa błędów i wyświetlenie komunikatu
      const msg = err instanceof Error ? err.message : 'Nie udało się zalogować';
      Alert.alert('Błąd logowania', msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={{ flex: 1, justifyContent: 'center', padding: 16 }}>
      <Text style={{ fontSize: 20, marginBottom: 12, textAlign: 'center' }}>Logowanie</Text>

      <TextInput
        placeholder="Username"
        value={username}
        onChangeText={setUsername}
        style={{ borderWidth: 1, padding: 8, marginVertical: 8 }}
        autoCapitalize="none"
        editable={!loading}
      />

      <TextInput
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={{ borderWidth: 1, padding: 8, marginVertical: 8 }}
        editable={!loading}
      />

      {loading ? (
        <ActivityIndicator size="large" style={{ marginTop: 12 }} />
      ) : (
        <Button title="Zaloguj się" onPress={handleLogin} />
      )}
    </View>
  );
}