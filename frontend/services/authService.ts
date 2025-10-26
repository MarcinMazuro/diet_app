import * as SecureStore from 'expo-secure-store';
import { API_URL, ENDPOINTS } from '../config/api';
import 'expo-router';

/**
 * Obsługuje logowanie użytkownika, komunikację z API i zapis tokenów.
 */
export async function loginUser(username: string, password: string): Promise<void> {
  //Wysłanie żądania POST
  const res = await fetch(`${API_URL}${ENDPOINTS.LOGIN}`, {
    method: 'POST',
    headers: { Accept: 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });

  //Parsowanie odpowiedzi
  const ct = res.headers.get('content-type') ?? '';
  const text = await res.text();
  if (!ct.includes('application/json')) {
    throw new Error(`Nieoczekiwana odpowiedź z serwera: ${text}`);
  }
  const data = JSON.parse(text);

  //Obsługa błędów HTTP (statusy 4xx/5xx)
  if (!res.ok) {

    const msgs = Object.values(data).flat?.() ?? [];
    throw new Error(msgs.length ? msgs.join(' ') : 'Błąd logowania');
  }

  //Pobranie i walidacja tokena dostępu
  const accessToken = data.access ?? data.key ?? data.token ?? data.access_token ?? null;
  if (!accessToken) throw new Error('Brak tokena w odpowiedzi serwera');

  //Bezpieczny zapis tokenów
  await SecureStore.setItemAsync('accessToken', accessToken);
  const refreshToken = data.refresh ?? data.refresh_token ?? null;
  if (refreshToken) await SecureStore.setItemAsync('refreshToken', refreshToken);

}