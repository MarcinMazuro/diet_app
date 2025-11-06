import React, { createContext, useContext, useEffect, useState } from "react";
import { getAccessToken } from "@/services/authService"; // ⬅️ ważne!

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

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
    const [isAuthenticated, setAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);

    // Checks whether the user has a valid token
    const checkAuth = async () => {
        try {
            const token = await getAccessToken();
            setAuthenticated(!!token);
        } catch {
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
        <AuthContext.Provider
            value={{ isAuthenticated, loading, setAuthenticated, checkAuth }}
        >
            {children}
        </AuthContext.Provider>
    );
};
// Custom hook to use the AuthContext
export const useAuth = () => useContext(AuthContext);
