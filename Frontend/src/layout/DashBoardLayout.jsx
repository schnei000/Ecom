import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import UseAuth from "../hooks/useAuth";

function DashboardLayout({children}) {
    const {user} = UseAuth();

    return (
        <div className = "min-h-screen flex flex col bg-gray-100">
            <NavBar/>
            <div className = "container mx-auto px-4 py-8">
                <h1 className= "text-2xl font-semibold mb-6">
                    Bienvenue {user?.userName}
                </h1>
                {children}
                <Footer/>
            </div>
        </div>
    )
};

export default DashboardLayout;
    