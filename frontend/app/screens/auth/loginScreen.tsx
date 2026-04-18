import React, { useState } from 'react';
import { View, TextInput, Pressable, Text, Alert, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';
import { loginUser } from '@/services/authService';
import { useAuth } from '@/contexts/AuthContext';


export default function LoginScreen() {
  const router = useRouter();
  const { setAuthenticated } = useAuth();

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
      setAuthenticated(true);
      router.replace('/meal-plan' as any);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Could not log in';
      Alert.alert('Log in error', msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View className="flex-1 bg-gradient-to-br from-blue-50 to-indigo-100">
      <View className="flex-1 justify-center px-8 py-12">
        <View className="rounded-[36px] bg-white border border-blue-200 shadow-lg p-8 gap-8">
          <View className="gap-3">
            <Text className="text-3xl font-bold text-blue-900 tracking-tight">Welcome Back</Text>
            <Text className="text-base text-blue-600 leading-relaxed">
              Return to your nutrition plan and track your daily progress.
            </Text>
          </View>

          <View className="gap-8">
            <TextInput
              placeholder="Username"
              value={username}
              onChangeText={setUsername}
              autoCapitalize="none"
              editable={!loading}
              placeholderTextColor="#64748b"
              className="rounded-[28px] border border-blue-300 bg-blue-50 px-5 py-4 text-blue-900 text-base"
            />
            <TextInput
              placeholder="Password"
              value={password}
              onChangeText={setPassword}
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
                onPress={handleLogin}
                className="rounded-[28px] bg-blue-600 py-5 items-center justify-center active:opacity-80 shadow-md"
              >
                <Text className="text-lg font-semibold text-white">Sign In</Text>
              </Pressable>

              <View className="items-center gap-4">
                <Text className="text-blue-600 text-base">Don't have an account yet?</Text>
                <Pressable
                  onPress={() => router.push('./register')}
                  className="rounded-[28px] bg-blue-100 px-6 py-4 active:opacity-80"
                >
                  <Text className="text-blue-700 font-semibold text-base">Sign Up</Text>
                </Pressable>
              </View>
            </View>
          )}
        </View>
      </View>
    </View>
  );
}
