import { apiFetch } from './apiClient';

const BASE_URL = '/auth/v1';

async function register(data) {
    return apiFetch(`${BASE_URL}/register`, {
        method: 'POST',
        body: data,
        fallbackMessage: "Erreur lors de l'inscription.",
    });
}

async function login(data) {
    return apiFetch(`${BASE_URL}/login`, {
        method: 'POST',
        body: data,
        fallbackMessage: 'Identifiants invalides.',
    });
}

async function logout(token) {
    return apiFetch(`${BASE_URL}/logout`, {
        method: 'POST',
        token,
        fallbackMessage: 'Erreur lors de la déconnexion.',
    });
}

async function getMe(token) {
    return apiFetch(`${BASE_URL}/me`, {
        token,
        fallbackMessage: 'Erreur lors de la récupération du profil.',
    });
}

async function getUsers(token, page = 1, perPage = 20) {
    return apiFetch(`${BASE_URL}/users?page=${page}&per_page=${perPage}`, {
        token,
        fallbackMessage: 'Erreur lors de la récupération des utilisateurs.',
    });
}

async function refreshToken(refreshTokenValue) {
    return apiFetch(`${BASE_URL}/refresh`, {
        method: 'POST',
        token: refreshTokenValue,
        fallbackMessage: 'Erreur lors du rafraîchissement du token.',
    });
}

async function updateProfile(data, token) {
    return apiFetch(`${BASE_URL}/me`, {
        method: 'PUT',
        token,
        body: data,
        fallbackMessage: 'Erreur lors de la mise à jour du profil.',
    });
}

async function changePassword(data, token) {
    return apiFetch(`${BASE_URL}/me/password`, {
        method: 'PATCH',
        token,
        body: data,
        fallbackMessage: 'Erreur lors du changement de mot de passe.',
    });
}

export { register, login, logout, getMe, getUsers, refreshToken, updateProfile, changePassword };
