// A simple API client that handles token-based authentication with automatic token refresh.
import { API_URL } from "@/config/api";
import { getAccessToken, refreshAccessToken } from "@/services/authService";

export async function apiFetch(
    endpoint: string,
    options: RequestInit = {},
    retry = true
): Promise<Response> {
    let token = await getAccessToken();

    const headers = {
        ...(options.headers || {}),
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };

    // first request
    let response = await fetch(`${API_URL}${endpoint}`, {
        ...options,
        headers,
    });

    // If token expired — try to refresh and retry the request
    if (response.status === 401 && retry) {
        const newToken = await refreshAccessToken();

        if (newToken) {
            const retryHeaders = {
                ...(options.headers || {}),
                "Content-Type": "application/json",
                Authorization: `Bearer ${newToken}`,
            };

            response = await fetch(`${API_URL}${endpoint}`, {
                ...options,
                headers: retryHeaders,
            });
        } else {
            throw new Error("Session expired. Please log in again.");
        }
    }

    return response;
}
