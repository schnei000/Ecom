import { initialState } from './cartInitialState.js';

export default function CartReducer(state, action) {
    switch (action.type) {
        case 'SET_CART': {
            const items = action.payload.items ?? [];
            const total = action.payload.total ?? 0;
            const cartCount = items.reduce((sum, item) => sum + (item.quantity ?? 0), 0);
            return { items, total, cartCount };
        }
        case 'CLEAR_CART':
            return initialState;
        default:
            return state;
    }
}
