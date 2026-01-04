import React, { useState } from 'react';
import { View, TextInput, Button, Text, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { registerUser } from '@/services/authService';
import { useAuth } from '@/contexts/AuthContext';

export default function RegisterScreen() {
  const router = useRouter();
  const { setAuthenticated } = useAuth(); // using the auth context
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password1: '',
    password2: '',
  });

  const handleRegister = async () => {
    // Validate all fields are filled
    if (Object.values(formData).some(v => !v)) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    // Validate passwords match
    if (formData.password1 !== formData.password2) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }

    setLoading(true);
    try {
      await registerUser(
        formData.username,
        formData.email,
        formData.password1,
        formData.password2
      );
      // Navigate to main app on success
      setAuthenticated(true);
      router.replace('/(tabs)/meal-plan');
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Registration failed';
      Alert.alert('Registration Error', msg);
      setLoading(false);
    }
  };

  return (
    <View style={{ flex: 1, justifyContent: 'center', padding: 16 }}>
      <Text style={{ fontSize: 20, marginBottom: 20, textAlign: 'center' }}>
        Register
      </Text>

      <TextInput
        placeholder="Username"
        value={formData.username}
        onChangeText={(text) => setFormData(prev => ({ ...prev, username: text }))}
        style={{ borderWidth: 1, padding: 8, marginVertical: 8 }}
        autoCapitalize="none"
        editable={!loading}
      />

      <TextInput
        placeholder="Email"
        value={formData.email}
        onChangeText={(text) => setFormData(prev => ({ ...prev, email: text }))}
        style={{ borderWidth: 1, padding: 8, marginVertical: 8 }}
        autoCapitalize="none"
        keyboardType="email-address"
        editable={!loading}
      />

      <TextInput
        placeholder="Password"
        value={formData.password1}
        onChangeText={(text) => setFormData(prev => ({ ...prev, password1: text }))}
        secureTextEntry
        style={{ borderWidth: 1, padding: 8, marginVertical: 8 }}
        editable={!loading}
      />

      <TextInput
        placeholder="Confirm Password"
        value={formData.password2}
        onChangeText={(text) => setFormData(prev => ({ ...prev, password2: text }))}
        secureTextEntry
        style={{ borderWidth: 1, padding: 8, marginVertical: 8 }}
        editable={!loading}
      />

      {loading ? (
        <ActivityIndicator size="large" style={{ marginTop: 12 }} />
      ) : (
        <>
          <Button title="Register" onPress={handleRegister} />
          <View style={{ marginTop: 22, alignItems: 'center' }}>
            <Button 
              title="Back to Login" 
              onPress={() => router.back()} 
            />
          </View>
        </>
      )}
    </View>
  );
}
