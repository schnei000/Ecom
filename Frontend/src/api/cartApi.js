import { apiFetch } from './apiClient';

const BASE_URL = `${import.meta.env.VITE_API_BASE_URL ?? ''}/api/v1/panier`;

async function getCart(token) {
    const data = await apiFetch(`${BASE_URL}/view`, {
        token,
        fallbackMessage: 'Erreur lors de la récupération du panier.',
    });
    return data.data ?? [];
}

async function addToCart(product_id, quantity, token) {
    return apiFetch(`${BASE_URL}/add`, {
        method: 'POST',
        token,
        body: { product_id, quantity },
        fallbackMessage: "Erreur lors de l'ajout au panier.",
    });
}

async function updateCartItem(product_id, quantity, token) {
    return apiFetch(`${BASE_URL}/update/${product_id}`, {
        method: 'PUT',
        token,
        body: { quantity },
        fallbackMessage: 'Erreur lors de la mise à jour.',
    });
}

async function removeFromCart(product_id, token) {
    return apiFetch(`${BASE_URL}/delete/${product_id}`, {
        method: 'DELETE',
        token,
        fallbackMessage: 'Erreur lors de la suppression.',
    });
}

async function clearCart(token) {
    return apiFetch(`${BASE_URL}/clear`, {
        method: 'DELETE',
        token,
        fallbackMessage: 'Erreur lors du vidage du panier.',
    });
}

export { getCart, addToCart, updateCartItem, removeFromCart, clearCart };
