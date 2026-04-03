import { useContext } from "react";
import AuthContext from "../context/AuthContext";

function useAuth() {
    const context = useContext(AuthContext);

    // condition pour verifier l existence du context
    if (!context) {
        throw new Error("dans useAuth, le context doit etre utilise dans un AuthProvider");
    }

    return context;
}
export default useAuth;