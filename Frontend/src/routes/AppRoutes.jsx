import {routes, Route} from 'react-router-dom';
import MainLayout from '../layouts/MainLayout';
import DashboardLayout from '../layouts/DashboardLayout';
import AdminLayout from '../layouts/AdminLayout';
import PrivateRoute from './PrivateRoutes';
import AdminRoutes from './AdminRoutes';
import Home from '../pages/Home';
import Login from '../pages/Login';
import Register from '../pages/Register';
import Products from '../pages/Products';
import UserDashboad from '../pages/dashboard/UserDashboard';
import AdminDashboard from '../pages/dashboard/AdminDashboard';

function AppRoutes() {
    return (
        <Routes>
            {/*public routes */}
            <Route
                path="/"
                element ={
                    <MainLayout>
                        <Home/>
                    </MainLayout>
                
                }
            />
            <Route
                path = "/products"
                element = {
                    <MainLayout>
                        <Products/>
                    </MainLayout>
                }
            />

            <Route
                path = "/login"
                element = {
                    <MainLayout>
                        <Login/>
                    </MainLayout>
                }
            />

            <Route
            path = "/register"
            element = {
                <MainLayout>
                    <Register/>
                </MainLayout>
            }
            />

            {/*private routes */}
            <Route
                path = "/dashboard"
                elememnt = {
                    <PrivateRoute>
                        <DashoardLayout/>
                        <UserDashboard/>
                    </PrivateRoute>
                }
            />

            {/*admin routes */}
            <Route
                path = "/admin"
                element = {
                    <PrivateRoute>
                        <AdminLayout/>
                        <AdminDashboard/>
                    </PrivateRoute>
                }
            />

        </Routes>
    )
}

export default AppRoutes;