import React from "react";
import {useContext} from React;
import {AuthContext} from "../context/AuthContext";

function UseAuth() {
    const context = useContext(AuthContext);

    // condition pour verifier l existence du context
    if (!context) {
        throw new Error("dans useAuth, le context doit etre utilise dans un AuthProvider");
    }

    return context;
}
export default UseAuth;