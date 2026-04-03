import {Navigate} from 'react-router-dom';
import useAuth from '../hooks/useAuth';

function AdminRoutes({children}) {
    const {isAuthenticated, isAdmin} = useAuth();
    // verifions si l utilisateur qui est authentifier est l administrateur
    if (!isAuthenticated || !isAdmin) {
        return <Navigate to="/" replace/>;
    }
    return children;
}

export default AdminRoutes;