import {useReducer, useEffect} from "react";
import AuthContext from "./AuthContext";
import AuthReducer, {initialState} from "./AuthReducer";

function AuthProvider({children}) {
    const [state, dispatch] = useReducer(AuthReducer, initialState);
    // creons UseEffect pour charger l'utilisateur et le token depuis le localStorage au montage du composant

    useEffect(() => {
        const user = localStorage.getItem("user");
        const token = localStorage.getItem("token");
        // si nous avons un utilisateur le dispatch fera un login success
        if (user && token) {
            dispatch({
                type: "SUCCESS_LOGIN",
                payload: {
                    user:JSON.parse(user),
                    token:token
                },
            });
        }
    }, []);

    const login = (data) => {
        localStorage.setItem("user", JSON.stringify(data.user));
        localStorage.setItem("token", data.token);

        dispatch({
            type: "SUCCESS_LOGIN",
            payload: data,
        });
    };

    const Logout = () => {
        localStorage.clear();
        dispatch({type: "LOGOUT"});
    };

    return (
        <AuthContext.Provider
            value = {{
                ...state,
                login,
                Logout,
            }}
            >
            {children}
        </AuthContext.Provider>
    );
};

export default AuthProvider;