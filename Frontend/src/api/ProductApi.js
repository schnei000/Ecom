import { apiFetch } from './apiClient';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

async function fetchProducts({ categoryId, search, sort, page = 1, per_page = 12 } = {}) {
    const params = new URLSearchParams({ per_page, page });
    if (categoryId) params.set('category_id', categoryId);
    if (search) params.set('search', search);
    if (sort) params.set('sort', sort);
    const data = await apiFetch(`${BASE_URL}/products?${params}`, {
        fallbackMessage: 'Erreur lors de la récupération des produits.',
    });
    return data.data ?? [];
}

async function fetchProduct(id) {
    const data = await apiFetch(`${BASE_URL}/products/${id}`, {
        fallbackMessage: 'Produit introuvable.',
    });
    return data.data ?? data;
}

async function fetchCategories() {
    const data = await apiFetch(`${BASE_URL}/categories`, {
        fallbackMessage: 'Erreur lors de la récupération des catégories.',
    });
    return data.data ?? [];
}

async function createProduct(productData, token) {
    return apiFetch(`${BASE_URL}/products`, {
        method: 'POST',
        token,
        body: productData,
        fallbackMessage: 'Erreur lors de la création.',
    });
}

async function updateProduct(id, productData, token) {
    return apiFetch(`${BASE_URL}/products/${id}`, {
        method: 'PUT',
        token,
        body: productData,
        fallbackMessage: 'Erreur lors de la mise à jour.',
    });
}

async function deleteProduct(id, token) {
    return apiFetch(`${BASE_URL}/products/${id}`, {
        method: 'DELETE',
        token,
        fallbackMessage: 'Erreur lors de la suppression.',
    });
}

async function createCategory(data, token) {
    return apiFetch(`${BASE_URL}/categories`, {
        method: 'POST',
        token,
        body: data,
        fallbackMessage: 'Erreur lors de la création de la catégorie.',
    });
}

async function updateCategory(id, data, token) {
    return apiFetch(`${BASE_URL}/categories/${id}`, {
        method: 'PUT',
        token,
        body: data,
        fallbackMessage: 'Erreur lors de la mise à jour de la catégorie.',
    });
}

async function deleteCategory(id, token) {
    return apiFetch(`${BASE_URL}/categories/${id}`, {
        method: 'DELETE',
        token,
        fallbackMessage: 'Erreur lors de la suppression de la catégorie.',
    });
}

export { fetchProducts, fetchProduct, fetchCategories, createProduct, updateProduct, deleteProduct, createCategory, updateCategory, deleteCategory };
