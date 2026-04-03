import { createContext } from 'react';

const CartContext = createContext({
    items: [],
    total: 0,
    cartCount: 0,
    addToCart: async () => {},
    updateCartItem: async () => {},
    removeFromCart: async () => {},
    clearCart: async () => {},
    refreshCart: async () => {},
});

export default CartContext;