import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import MainLayout from '../layout/MainLayout';
import AuthLayout from '../layout/AuthLayout';
import DashboardLayout from '../layout/DashboardLayout';
import AdminLayout from '../layout/AdminLayout';
import PrivateRoute from './PrivateRoutes';
import AdminRoutes from './AdminRoutes';
import Loading from '../components/Loading';

const Home = lazy(() => import('../pages/Home'));
const Products = lazy(() => import('../pages/Products'));
const ProductDetail = lazy(() => import('../pages/ProductDetail'));
const Login = lazy(() => import('../pages/Login'));
const Register = lazy(() => import('../pages/Register'));
const UserDashboard = lazy(() => import('../pages/dashboard/UserDashboard'));
const AdminDashboard = lazy(() => import('../pages/dashboard/AdminDashboard'));
const NotFound = lazy(() => import('../pages/NotFound'));

const PageFallback = () => (
    <div className="flex min-h-[60vh] items-center justify-center">
        <Loading />
    </div>
);

function AppRoutes() {
    return (
        <Suspense fallback={<PageFallback />}>
            <Routes>
                {/* routes publiques */}
                <Route path="/" element={<MainLayout><Home /></MainLayout>} />
                <Route path="/products" element={<MainLayout><Products /></MainLayout>} />
                <Route path="/products/:id" element={<MainLayout><ProductDetail /></MainLayout>} />
                <Route path="/login" element={<AuthLayout><Login /></AuthLayout>} />
                <Route path="/register" element={<AuthLayout><Register /></AuthLayout>} />

                {/* routes privées */}
                <Route path="/dashboard" element={<PrivateRoute><DashboardLayout><UserDashboard /></DashboardLayout></PrivateRoute>} />

                {/* routes admin */}
                <Route path="/admin" element={<AdminRoutes><AdminLayout><AdminDashboard /></AdminLayout></AdminRoutes>} />

                {/* 404 */}
                <Route path="*" element={<MainLayout><NotFound /></MainLayout>} />
            </Routes>
        </Suspense>
    );
}

export default AppRoutes;
