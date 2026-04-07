import { apiFetch } from './apiClient';

const BASE_URL = `${import.meta.env.VITE_API_BASE_URL ?? ''}/api/v1`;

async function createOrder(token) {
    return apiFetch(`${BASE_URL}/order`, {
        method: 'POST',
        token,
        fallbackMessage: 'Erreur lors de la création de la commande.',
    });
}

async function getOrders(token) {
    const data = await apiFetch(`${BASE_URL}/orders`, {
        token,
        fallbackMessage: 'Erreur lors de la récupération des commandes.',
    });
    return data.data ?? [];
}

async function getOrder(id, token) {
    return apiFetch(`${BASE_URL}/orders/${id}`, {
        token,
        fallbackMessage: 'Commande introuvable.',
    });
}

async function cancelOrder(id, token) {
    return apiFetch(`${BASE_URL}/orders/${id}/cancel`, {
        method: 'POST',
        token,
        fallbackMessage: "Erreur lors de l'annulation.",
    });
}

export { createOrder, getOrders, getOrder, cancelOrder };
