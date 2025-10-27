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
      Alert.alert('Error', 'Fill in every box');
      return;
    }

    setLoading(true);
    
    try {
      await loginUser(username, password);
      // Routing after successful log in 
      router.replace('/(tabs)');
      
    } catch (err) {
      // Errors and messages
      const msg = err instanceof Error ? err.message : 'Could not log in';
      Alert.alert('Log in error', msg);
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
        <Button title="Log in" onPress={handleLogin} />
      )}
    </View>
  );
}