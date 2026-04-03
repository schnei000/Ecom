import { createContext } from "react";

const AuthContext = createContext({
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    isAdmin: false,
    login: () => {},
    logout: () => {},
    Logout: () => {},
});

export default AuthContext;