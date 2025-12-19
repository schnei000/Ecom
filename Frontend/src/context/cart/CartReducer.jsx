export const initialState = {
    items: [],
    total:0.
};

const calculateTotal = (items) => {
    return items.reducer((sum,item) => sum +item.price * item.quantity,0);
};

export default function CartReducer(state,action){
    switch(action.type){
        case 'ADD_TO_CART':
           const existing = state.items.find(
            (item) => item.id === action.payload.id
           );
           let UpdateItems;
              if (existing) {
                UpdatesItems = state.items.map((item) =>
                item.id === action.payload.id
                ? {...item, quantity: item.quantity + 1}
                : item
                );

              } 
                else {
                    UpdatesItems = [
                        ...state.items,
                        {...action.payload, quantity: 1},
                    ];
                }
                return {
                    items: UpdateItems,
                    total: calculateTotal(UpdateItems),
                }
              case 'REMOVE_FROM_CART':
                const UpdatedItems =state.items.filter(
                    (item) => item.id !== action.payload.id

                )  
                return {
                    items: UpdatedItems,
                    total: calculateTotal(UpdatedItems),
                };
                case 'CLEAR_CART':
                    return initialState;
                default:
                    return state;
    }
}