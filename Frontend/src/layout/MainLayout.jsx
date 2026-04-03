import Navbar from "../components/Navbar";
import Footer from "../components/Footer";
import FloatingCart from "../components/FloatingCart";

function MainLayout({children}) {
    return (
        <div className="flex min-h-screen flex-col overflow-x-hidden bg-transparent">
            <Navbar/>
            <main className="flex-1">
                {children}
            </main>
            <Footer/>
            <FloatingCart />
        </div>
    );
};

export default MainLayout;
