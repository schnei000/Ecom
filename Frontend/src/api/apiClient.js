/**
 * Wrapper centralisé pour tous les appels API.
 *
 * Gère automatiquement :
 * - L'en-tête Authorization avec le token JWT
 * - Le Content-Type (JSON ou FormData selon le body)
 * - La lecture de la réponse JSON
 * - Le throw sur les réponses non-ok
 */

export async function apiFetch(url, { method = 'GET', token, body, fallbackMessage = 'Erreur serveur.' } = {}) {
    const headers = {};

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    let requestBody;
    if (body instanceof FormData) {
        // FormData positionne son propre Content-Type (boundary inclus)
        requestBody = body;
    } else if (body !== undefined) {
        headers['Content-Type'] = 'application/json';
        requestBody = JSON.stringify(body);
    }

    const res = await fetch(url, { method, headers, body: requestBody });
    const data = await res.json();

    if (!res.ok) {
        throw new Error(data.message || fallbackMessage);
    }

    return data;
}
