import * as SecureStore from 'expo-secure-store';
import { API_URL, ENDPOINTS } from '../config/api';
import 'expo-router';

/**
 * Log in a user with given credentials.
 */
export async function loginUser(username: string, password: string): Promise<void> {
  //Send login request
  const res = await fetch(`${API_URL}${ENDPOINTS.LOGIN}`, {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  //Response handling
  const ct = res.headers.get('content-type') ?? '';
  const text = await res.text();
  if (!ct.includes('application/json')) {
    throw new Error(`Unexpected respond from server: ${text}`);
  }
  const data = JSON.parse(text);

  //Http error handling
  if (!res.ok) {

    const msgs = Object.values(data).flat?.() ?? [];
    throw new Error(msgs.length ? msgs.join(' ') : 'Log in failed');
  }

  //Extract tokens from response
  const accessToken = data.access ?? data.key ?? data.token ?? data.access_token ?? null;
  if (!accessToken) throw new Error('No access token in response');

  //Store tokens securely
  await SecureStore.setItemAsync('accessToken', accessToken);
  const refreshToken = data.refresh ?? data.refresh_token ?? null;
  if (refreshToken) await SecureStore.setItemAsync('refreshToken', refreshToken);

}