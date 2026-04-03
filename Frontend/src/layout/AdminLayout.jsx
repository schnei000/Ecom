import Navbar from "../components/Navbar";
import Footer from "../components/Footer";

function AdminLayout({children}) {
    return (
        <div className="min-h-screen overflow-x-hidden bg-transparent text-white">
            <Navbar/>
            <main className="mx-auto w-full max-w-7xl px-4 pt-18 sm:px-6 lg:px-8">
                {children}
            </main>
            <Footer/>
        </div>
    )
};

export default AdminLayout;
