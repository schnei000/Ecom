export const initialState = {
    user: null,
    token: null,
    refreshToken: null,
    isAuthenticated: false,
    isAdmin: false,
};

export default function AuthReducer(state, action) {
    switch (action.type) {
        case 'SUCCESS_LOGIN':
            return {
                ...state,
                user: action.payload.user,
                token: action.payload.token,
                refreshToken: action.payload.refresh_token ?? null,
                isAuthenticated: true,
                isAdmin: action.payload.user?.is_admin ?? false,
            };
        case 'REFRESH_TOKEN':
            return {
                ...state,
                token: action.payload.token,
                refreshToken: action.payload.refresh_token ?? state.refreshToken,
            };
        case 'UPDATE_USER':
            localStorage.setItem('user', JSON.stringify({ ...state.user, ...action.payload }));
            return { ...state, user: { ...state.user, ...action.payload } };
        case 'LOGOUT':
            return initialState;
        default:
            return state;
    }
}
