import * as SecureStore from 'expo-secure-store';
import { API_URL, ENDPOINTS } from '../config/api';

// Helper function to handle tokens
async function handleAuthTokens(data: any): Promise<void> {
  const access = data.access ?? data.key ?? data.token ?? data.access_token ?? null;
  const refresh = data.refresh ?? data.refresh_token ?? null;

  if (!access) throw new Error('No access token in response');

  await SecureStore.setItemAsync('accessToken', access);
  if (refresh) {
    await SecureStore.setItemAsync('refreshToken', refresh);
  }
}

// Helper function to get access token (used in other services)
export async function getAccessToken(): Promise<string | null> {
    return await SecureStore.getItemAsync('accessToken');
}


// Function to refresh access token
export async function refreshAccessToken(): Promise<string | null> {
    const refresh = await SecureStore.getItemAsync("refreshToken");
    if (!refresh) return null;

    const res = await fetch(`${API_URL}/api/v1/auth/token/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh }),
    });

    if (!res.ok) {
        await SecureStore.deleteItemAsync("accessToken");
        await SecureStore.deleteItemAsync("refreshToken");
        return null;
    }

    const data = await res.json();
    const access = data.access ?? data.access_token;
    if (access) {
        await SecureStore.setItemAsync("accessToken", access);
        return access;
    }
    return null;
}


// Function to log in a user
export async function loginUser(username: string, password: string): Promise<void> {
  const res = await fetch(`${API_URL}${ENDPOINTS.LOGIN}`, {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  const ct = res.headers.get('content-type') ?? '';
  const text = await res.text();
  if (!ct.includes('application/json')) {
    throw new Error(`Unexpected respond from server: ${text}`);
  }
  const data = JSON.parse(text);

  if (!res.ok) {
    const msgs = Object.values(data).flat?.() ?? [];
    throw new Error(msgs.length ? msgs.join(' ') : 'Log in failed');
  }

  await handleAuthTokens(data);
}

// Function to register a new user
export async function registerUser(
  username: string, 
  email: string, 
  password1: string, 
  password2: string
): Promise<void> {
  const res = await fetch(`${API_URL}${ENDPOINTS.REGISTER}`, {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password1, password2 }),
  });
// Handle response
  const ct = res.headers.get('content-type') ?? '';
  const text = await res.text();
  if (!ct.includes('application/json')) {
    throw new Error(`Unexpected response from server: ${text}`);
  }
  const data = JSON.parse(text);

  if (!res.ok) {
    const msgs = Object.values(data).flat?.() ?? [];
    throw new Error(msgs.length ? msgs.join(' ') : 'Registration failed');
  }

  // Handle tokens after successful registration
  await handleAuthTokens(data);
}



// Logout function
export async function logoutUser(): Promise<void> {
    const refreshToken = await SecureStore.getItemAsync('refreshToken');
    
    // Remove tokens from secure storage
    await SecureStore.deleteItemAsync('accessToken');
    if (refreshToken) {
        await SecureStore.deleteItemAsync('refreshToken');
    }

    if (refreshToken) {
        try {
            // Inform the server about logout to invalidate the refresh token
            await fetch(`${API_URL}${ENDPOINTS.LOGOUT}`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ refresh: refreshToken }),
            });

        } catch (error) {
            console.error('Logout request failed (tokens already removed on client):', error);
        }
    }
}