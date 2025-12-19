const API_URL = "http://localhost:5000/api";

async function fetchProducts() {
    const res = await fetch(`${API_URL}/products`);
    const data = await res.json();
    if (!res.ok) {
        throw new Error("Erreur lors de la récupération des produits");
    }
    return data;
}

export { fetchProducts };