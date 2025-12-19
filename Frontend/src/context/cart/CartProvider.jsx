import {useReducer} from 'react';
import CartContext from './CartContext.jsx';
import CartReducer, {initialState} from './CartReducer.jsx';

function CartProvider({children}) {
    const [state,dispatch] = useReducer(CartReducer,initialState);

    const addToCart= (Product) => {
        dispatch({type: 'ADD_TO_CART', payload: Product});

    };
    const removeFromCart = (Product) => {
        dispatch({type: 'REMOVE_FROM_CART', payload: Product});
    };
    const clearCart = () => {
        dispatch({type: 'CLEAR_CART'});
    };
    return (
        <CartContext.Provider
        value={{
            items: state.items,
            total: state.total,
            addToCart,
            removeFromCart,
            clearCart,
        }}
        >
            {children}
        </CartContext.Provider>
    );
}

export default CartProvider;
