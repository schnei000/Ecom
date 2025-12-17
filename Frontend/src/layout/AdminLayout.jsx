import NavBar from "../components/NavBar";
import Footer from "../components/Footer";
import UseAuth from "../hooks/useAuth";

function AdminLayout({children}) {
    const {user} = UseAuth();

    return (
        <div className = "min-h-screen bg-neutral-900 text-white">
            <NavBar/>
            <div className = "container mx-auto px-4 py-8">
                <h1 className= "text-2xl font-semibold mb-6">
                    Administrator Panel - {user?.userName}
                </h1>
                {children}
            </div>
            <Footer/>
        </div>
    )
};

export default AdminLayout;