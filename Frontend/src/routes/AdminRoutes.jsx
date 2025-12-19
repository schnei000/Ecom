import {Navigate} from 'react-router-dom';
import useAuth from '../hooks/useAuth';

function AdminRoutes({children}) {
    const {isAuthentificated, isAdmin} = useAuth();
    // verifions si l utilisateur qui est authentifier est l administrateur
    if (!isAuthentificated || !isAdmin) {
        return <Navigate to="/" replace/>;
    }
    return children;
}

export default AdminRoutes;