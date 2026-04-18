import React, { useState } from 'react';
import { View, TextInput, Pressable, Text, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { registerUser } from '@/services/authService';
import { useAuth } from '@/contexts/AuthContext';


export default function RegisterScreen() {
  const router = useRouter();
  const { setAuthenticated } = useAuth();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password1: '',
    password2: '',
  });

  const handleRegister = async () => {
    if (Object.values(formData).some(v => !v)) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

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
      setAuthenticated(true);
      router.replace('/meal-plan' as any);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Registration failed';
      Alert.alert('Registration Error', msg);
      setLoading(false);
    }
  };

  return (
    <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100">
      <View className="flex-1 justify-center px-8 py-12">
        <View className="rounded-[36px] bg-white border border-blue-200 shadow-lg p-8 gap-8">
          <View className="gap-3">
            <Text className="text-3xl font-bold text-blue-900 tracking-tight">Create Account</Text>
            <Text className="text-base text-blue-600 leading-relaxed">
              Start building healthier habits and manage your diet in one place.
            </Text>
          </View>

          <View className="gap-8">
            <TextInput
              placeholder="Username"
              value={formData.username}
              onChangeText={(text) => setFormData(prev => ({ ...prev, username: text }))}
              autoCapitalize="none"
              editable={!loading}
              placeholderTextColor="#64748b"
              className="rounded-[28px] border border-blue-300 bg-blue-50 px-5 py-4 text-blue-900 text-base"
            />
            <TextInput
              placeholder="Email"
              value={formData.email}
              onChangeText={(text) => setFormData(prev => ({ ...prev, email: text }))}
              autoCapitalize="none"
              keyboardType="email-address"
              editable={!loading}
              placeholderTextColor="#64748b"
              className="rounded-[28px] border border-blue-300 bg-blue-50 px-5 py-4 text-blue-900 text-base"
            />
            <TextInput
              placeholder="Password"
              value={formData.password1}
              onChangeText={(text) => setFormData(prev => ({ ...prev, password1: text }))}
              secureTextEntry
              editable={!loading}
              placeholderTextColor="#64748b"
              className="rounded-[28px] border border-blue-300 bg-blue-50 px-5 py-4 text-blue-900 text-base"
            />
            <TextInput
              placeholder="Confirm Password"
              value={formData.password2}
              onChangeText={(text) => setFormData(prev => ({ ...prev, password2: text }))}
              secureTextEntry
              editable={!loading}
              placeholderTextColor="#64748b"
              className="rounded-[28px] border border-blue-300 bg-blue-50 px-5 py-4 text-blue-900 text-base"
            />
          </View>

          {loading ? (
            <ActivityIndicator size="large" color="#3b82f6" className="mt-4" />
          ) : (
            <View className="gap-5">
              <Pressable
                onPress={handleRegister}
                className="rounded-[28px] bg-blue-600 py-5 items-center justify-center active:opacity-80 shadow-md"
              >
                <Text className="text-lg font-semibold text-white">Sign Up</Text>
              </Pressable>

              <View className="items-center gap-4">
                <Text className="text-blue-600 text-base">Already have an account?</Text>
                <Pressable
                  onPress={() => router.back()}
                  className="rounded-[28px] bg-blue-100 px-6 py-4 active:opacity-80"
                >
                  <Text className="text-blue-700 font-semibold text-base">Back to Sign In</Text>
                </Pressable>
              </View>
            </View>
          )}
        </View>
      </View>
    </View>
  );
}
