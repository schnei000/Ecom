/**
 * AuthLayout — No Navbar, no Footer.
 * Used for Login and Register split-screen pages.
 */
function AuthLayout({ children }) {
    return (
        <div className="relative min-h-screen overflow-hidden bg-[#05050d]">
            <div className="pointer-events-none absolute left-0 top-0 h-80 w-80 rounded-full bg-violet-600/14 blur-[160px]" />
            <div className="pointer-events-none absolute bottom-0 right-0 h-96 w-96 rounded-full bg-amber-500/10 blur-[170px]" />
            {children}
        </div>
    );
}

export default AuthLayout;
