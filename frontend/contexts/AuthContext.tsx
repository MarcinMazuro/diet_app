import React, { createContext, useContext, useEffect, useState } from "react";
import * as SecureStore from "expo-secure-store";

type AuthContextType = {
    isAuthenticated: boolean;
    loading: boolean;
    setAuthenticated: (value: boolean) => void;
    checkAuth: () => Promise<void>;
};
// Create the AuthContext with default values
const AuthContext = createContext<AuthContextType>({
    isAuthenticated: false,
    loading: true,
    setAuthenticated: () => {},
    checkAuth: async () => {},
});
// AuthProvider component to wrap the app and provide auth state
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [isAuthenticated, setAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);
    // Function to check authentication status
    const checkAuth = async () => {
        try {
            const token = await SecureStore.getItemAsync("accessToken");
            setAuthenticated(!!token);
        } catch (err) {
            console.error("Auth check failed:", err);
            setAuthenticated(false);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        checkAuth();
    }, []);
// Provide the auth state and functions to children components
    return (
        <AuthContext.Provider value={{ isAuthenticated, loading, setAuthenticated, checkAuth }}>
            {children}
        </AuthContext.Provider>
    );
};
// Custom hook to use the AuthContext
export const useAuth = () => useContext(AuthContext);
