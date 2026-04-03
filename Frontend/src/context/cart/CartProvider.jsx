import { useReducer, useEffect, useCallback } from 'react';
import CartContext from './CartContext.jsx';
import CartReducer from './CartReducer.jsx';
import { initialState } from './cartInitialState.js';
import useAuth from '../../hooks/useAuth';
import { addToCart as apiAdd, updateCartItem as apiUpdate, removeFromCart as apiRemove, clearCart as apiClear } from '../../api/cartApi';

const CART_URL = '/api/v1/panier/view';

function CartProvider({ children }) {
    const [state, dispatch] = useReducer(CartReducer, initialState);
    const { isAuthenticated, token } = useAuth();

    const refreshCart = useCallback(async () => {
        if (!isAuthenticated || !token) {
            dispatch({ type: 'CLEAR_CART' });
            return;
        }
        try {
            const res = await fetch(CART_URL, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) return;
            const data = await res.json();
            dispatch({
                type: 'SET_CART',
                payload: { items: data.data ?? [], total: data.total_price ?? 0 },
            });
        } catch {
            // silencieux — ne pas bloquer le rendu
        }
    }, [isAuthenticated, token]);

    // Recharger le panier à chaque changement d'auth
    useEffect(() => {
        refreshCart();
    }, [refreshCart]);

    const addToCart = useCallback(async (productId, quantity = 1) => {
        if (!token) return;
        await apiAdd(productId, quantity, token);
        await refreshCart();
        window.dispatchEvent(new Event('cart-updated'));
    }, [token, refreshCart]);

    const updateCartItem = useCallback(async (productId, quantity) => {
        if (!token) return;
        await apiUpdate(productId, quantity, token);
        await refreshCart();
        window.dispatchEvent(new Event('cart-updated'));
    }, [token, refreshCart]);

    const removeFromCart = useCallback(async (productId) => {
        if (!token) return;
        await apiRemove(productId, token);
        await refreshCart();
        window.dispatchEvent(new Event('cart-updated'));
    }, [token, refreshCart]);

    const clearCart = useCallback(async () => {
        if (!token) return;
        await apiClear(token);
        dispatch({ type: 'CLEAR_CART' });
        window.dispatchEvent(new Event('cart-updated'));
    }, [token]);

    return (
        <CartContext.Provider
            value={{
                items: state.items,
                total: state.total,
                cartCount: state.cartCount,
                addToCart,
                updateCartItem,
                removeFromCart,
                clearCart,
                refreshCart,
            }}
        >
            {children}
        </CartContext.Provider>
    );
}

export default CartProvider;
