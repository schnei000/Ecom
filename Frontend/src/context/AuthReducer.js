export const initialState = {
    user: null,
    token: null,
    isAuthentification:false,
    isAdmin:false,
};

export default function AuthReducer(state,action) {
    switch (action.type){
        case "SUCCESS_LOGIN":
            return {
                ...state,
                user:action.payload.user,
                token:action.payload.token,
                isAuthentification:true,
                isAdmin:action.payload.user.isAdmin
            }
            case "LOGOUT":
                return initialState;
                default:
                    return state;
    }
}