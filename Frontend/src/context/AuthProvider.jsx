import { useReducer, useEffect, useCallback, useRef } from 'react';
import AuthContext from './AuthContext';
import AuthReducer, { initialState } from './AuthReducer';

function getTokenExpiry(token) {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.exp ? payload.exp * 1000 : null;
    } catch {
        return null;
    }
}

function AuthProvider({ children }) {
    const [state, dispatch] = useReducer(AuthReducer, initialState);
    const refreshTimerRef = useRef(null);

    // Charger user/token/refresh_token depuis localStorage au montage
    useEffect(() => {
        const raw = localStorage.getItem('user');
        const token = localStorage.getItem('token');
        const refresh_token = localStorage.getItem('refresh_token');
        if (!raw || raw === 'undefined' || !token) {
            localStorage.removeItem('user');
            localStorage.removeItem('token');
            localStorage.removeItem('refresh_token');
            return;
        }
        try {
            const user = JSON.parse(raw);
            dispatch({ type: 'SUCCESS_LOGIN', payload: { user, token, refresh_token } });
        } catch {
            localStorage.removeItem('user');
            localStorage.removeItem('token');
            localStorage.removeItem('refresh_token');
        }
    }, []);

    const logout = useCallback(() => {
        clearTimeout(refreshTimerRef.current);
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        localStorage.removeItem('refresh_token');
        dispatch({ type: 'LOGOUT' });
    }, []);

    const doRefresh = useCallback(async (currentRefreshToken) => {
        if (!currentRefreshToken) { logout(); return; }
        try {
            const res = await fetch('/auth/v1/refresh', {
                method: 'POST',
                headers: { Authorization: `Bearer ${currentRefreshToken}` },
            });
            const json = await res.json();
            if (!res.ok) throw new Error(json.message);
            const newToken = json.data.access_token;
            const newRefresh = json.data.refresh_token;
            localStorage.setItem('token', newToken);
            if (newRefresh) localStorage.setItem('refresh_token', newRefresh);
            dispatch({ type: 'REFRESH_TOKEN', payload: { token: newToken, refresh_token: newRefresh } });
        } catch {
            logout();
        }
    }, [logout]);

    // Planifier le refresh automatique 5 minutes avant expiry
    useEffect(() => {
        clearTimeout(refreshTimerRef.current);
        if (!state.token) return;

        const expiry = getTokenExpiry(state.token);
        if (!expiry) return;

        const delay = expiry - Date.now() - 5 * 60 * 1000;
        if (delay <= 0) {
            doRefresh(state.refreshToken);
            return;
        }
        refreshTimerRef.current = setTimeout(() => doRefresh(state.refreshToken), delay);
        return () => clearTimeout(refreshTimerRef.current);
    }, [state.token, state.refreshToken, doRefresh]);

    const login = useCallback((data) => {
        localStorage.setItem('user', JSON.stringify(data.user));
        localStorage.setItem('token', data.token);
        if (data.refresh_token) {
            localStorage.setItem('refresh_token', data.refresh_token);
        }
        dispatch({ type: 'SUCCESS_LOGIN', payload: data });
    }, []);

    const updateUser = useCallback((data) => {
        dispatch({ type: 'UPDATE_USER', payload: data });
    }, []);

    // Conserver l'ancienne casse pour ne pas casser les imports existants
    const Logout = logout;

    return (
        <AuthContext.Provider value={{ ...state, login, Logout, logout, updateUser }}>
            {children}
        </AuthContext.Provider>
    );
}

export default AuthProvider;
