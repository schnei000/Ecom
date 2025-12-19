import {Navigate} from 'react-router-dom';
import useAuth from '../hooks/useAuth';

function privateRoutes({children}) {
    const {isAuthentificated} = useAuth();
    // verigions si l utilisateur est authentifier
    if (!isAuthentificated) {
        return <Navigate to="/login" replace/>;
    }
    return children;
    }

    export default PrivateRoute;