import React, { createContext, useState, useEffect } from 'react';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    // Initialize state directly from localStorage so refresh doesn't flash the login screen
    const [token, setToken] = useState(() => localStorage.getItem('token'));
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // If a token exists, parse it to hydrate the user state immediately
        const hydrateAuthState = async () => {
            if (token) {
                try {
                    // Since JWTs are base64 encoded strings (header.payload.signature),
                    // we can safely parse the middle section in the browser without an API call.
                    const base64Url = token.split('.')[1];
                    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
                    const jsonPayload = decodeURIComponent(window.atob(base64).split('').map(function(c) {
                        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
                    }).join(''));

                    const decoded = JSON.parse(jsonPayload);
                    
                    // Check expiration natively
                    if (decoded.exp * 1000 < Date.now()) {
                        logout();
                        return;
                    }
                    
                    // We only have the generic string identifier in the subject "sub", 
                    // which is good enough to verify they are logged in.
                    setUser({ identifier: decoded.sub });
                } catch (error) {
                    console.error("Failed to decode token", error);
                    logout(); // Malformed token; clear everything
                }
            } else {
                setUser(null);
            }
            setLoading(false);
        };

        hydrateAuthState();
    }, [token]);

    const login = (newToken) => {
        localStorage.setItem('token', newToken);
        setToken(newToken);
        // The useEffect will catch the token change and parse the user payload
    };

    const logout = () => {
        localStorage.removeItem('token');
        setToken(null);
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ token, user, login, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};
