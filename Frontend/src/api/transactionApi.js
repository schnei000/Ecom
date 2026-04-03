import { apiFetch } from './apiClient';

const BASE_URL = '/api/v1';

async function pay(order_id, amount, payment_method, token) {
    return apiFetch(`${BASE_URL}/pay`, {
        method: 'POST',
        token,
        body: { order_id, amount, payment_method },
        fallbackMessage: 'Erreur lors du paiement.',
    });
}

async function getTransactions(token) {
    const data = await apiFetch(`${BASE_URL}/transactions`, {
        token,
        fallbackMessage: 'Erreur lors de la récupération des transactions.',
    });
    return data.data ?? [];
}

async function getTransaction(id, token) {
    return apiFetch(`${BASE_URL}/transaction/${id}`, {
        token,
        fallbackMessage: 'Transaction introuvable.',
    });
}

async function cancelTransaction(id, token) {
    return apiFetch(`${BASE_URL}/transaction/${id}/cancel`, {
        method: 'POST',
        token,
        fallbackMessage: "Erreur lors de l'annulation.",
    });
}

async function getDailyTransactions(token) {
    return apiFetch(`${BASE_URL}/transactions/daily`, {
        token,
        fallbackMessage: 'Erreur lors de la récupération.',
    });
}

async function getAllTransactionsAdmin(token, page = 1, perPage = 20) {
    return apiFetch(`${BASE_URL}/admin/transactions?page=${page}&per_page=${perPage}`, {
        token,
        fallbackMessage: 'Erreur lors de la récupération.',
    });
}

export { pay, getTransactions, getTransaction, cancelTransaction, getDailyTransactions, getAllTransactionsAdmin };
