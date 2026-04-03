import { startTransition, useEffect, useEffectEvent, useState } from 'react';
import { Link, NavLink, useLocation, useNavigate } from 'react-router-dom';
import {
    FiArrowRight,
    FiMenu,
    FiMoon,
    FiShoppingBag,
    FiSun,
    FiUser,
    FiX,
    FiZap,
} from 'react-icons/fi';
import useAuth from '../hooks/useAuth';
import useTheme from '../hooks/useTheme';
import useCategories from '../hooks/useCategories';
import { getCart } from '../api/cartApi';

const PRIMARY_LINKS = [
    { to: '/', label: 'Accueil', end: true },
    { to: '/products', label: 'Catalogue', end: false },
    { to: '/products', label: 'Nouveautés', end: false, static: true },
];

function Navbar() {
    const { isAuthenticated, isAdmin, Logout, token } = useAuth();
    const { theme, toggleTheme } = useTheme();
    const navigate = useNavigate();
    const location = useLocation();

    const [scrolled, setScrolled] = useState(false);
    const { categories } = useCategories();
    const [cartCount, setCartCount] = useState(0);
    const [mobileOpen, setMobileOpen] = useState(false);

    const refreshCartCount = useEffectEvent(async () => {
        if (!isAuthenticated || !token) {
            startTransition(() => setCartCount(0));
            return;
        }

        try {
            const data = await getCart(token);
            const items = data.items ?? data.panier ?? data ?? [];
            const total = items.reduce((sum, item) => sum + (item.quantity ?? 1), 0);
            startTransition(() => setCartCount(total));
        } catch {
            // silence volontaire
        }
    });

    useEffect(() => {
        refreshCartCount();
    }, [isAuthenticated, token]);

    useEffect(() => {
        const handler = () => refreshCartCount();
        window.addEventListener('cart-updated', handler);
        return () => window.removeEventListener('cart-updated', handler);
    }, [token]);

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 18);
        window.addEventListener('scroll', onScroll, { passive: true });
        return () => window.removeEventListener('scroll', onScroll);
    }, []);

    useEffect(() => {
        if (!mobileOpen) return undefined;
        const handleKey = (event) => {
            if (event.key === 'Escape') setMobileOpen(false);
        };
        window.addEventListener('keydown', handleKey);
        return () => window.removeEventListener('keydown', handleKey);
    }, [mobileOpen]);

    useEffect(() => {
        if (!mobileOpen) return undefined;

        const previousOverflow = document.body.style.overflow;
        document.body.style.overflow = 'hidden';

        return () => {
            document.body.style.overflow = previousOverflow;
        };
    }, [mobileOpen]);

    const isHome = location.pathname === '/';
    const isTransparent = isHome && !scrolled && theme === 'dark';
    const isDashboardRoute = location.pathname.startsWith('/dashboard');
    const isAdminRoute = location.pathname.startsWith('/admin');
    const topCategories = categories.slice(0, 8);
    const closeMobileMenu = () => setMobileOpen(false);

    const handleLogout = () => {
        Logout();
        closeMobileMenu();
        navigate('/');
    };

    /* ── Classes adaptatives selon mode transparent / solid ── */
    const linkBase = 'rounded-full px-4 py-2.5 text-sm font-medium transition';
    const navLinkTone = isTransparent
        ? `text-white/60 hover:bg-white/[0.07] hover:text-white ${linkBase}`
        : `nav-link-tone ${linkBase}`;
    const navLinkActive = isTransparent
        ? `bg-white/10 border border-white/14 text-white ${linkBase}`
        : `nav-link-active-solid ${linkBase}`;
    const actionBase = 'rounded-full px-5 py-2.5 text-sm font-medium transition';
    const actionBtn = isTransparent
        ? `smoke-chip text-white/70 hover:border-white/18 hover:text-white ${actionBase}`
        : `smoke-chip ${actionBase}`;
    const actionBtnActive = `bg-amber-500/15 border border-amber-400/30 text-amber-300 ${actionBase}`;
    const iconBtn = isTransparent
        ? 'smoke-chip relative flex h-10 w-10 items-center justify-center rounded-full text-white/70 hover:border-white/18 hover:text-white transition'
        : 'smoke-chip relative flex h-10 w-10 items-center justify-center rounded-full hover:border-(--border-hover) transition';

    return (
        <header className="fixed inset-x-0 top-0 z-50">
            <div className={isTransparent ? 'navbar-transparent' : 'navbar-solid'}>
                <div className="mx-auto flex h-18 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">

                    {/* ── Logo ── */}
                    <Link to="/" aria-label="Boutik Lakay, retour à l'accueil" className="group flex shrink-0 items-center gap-3">
                        <span className={`flex h-10 w-10 items-center justify-center rounded-xl text-amber-400 transition group-hover:bg-amber-400/12 group-hover:border-amber-400/28 ${
                            isTransparent
                                ? 'border border-white/12 bg-white/[0.07]'
                                : 'border border-(--border) bg-(--surface)'
                        }`}>
                            <FiZap className="h-4.5 w-4.5" />
                        </span>
                        <div className="hidden sm:block">
                            <p className={`font-display text-[1.25rem] font-bold tracking-[-0.04em] ${isTransparent ? 'text-white' : 'text-(--text)'}`}>
                                Boutik<span className="text-amber-400">Lakay</span>
                            </p>
                            <p className={`text-[10px] font-medium uppercase tracking-[0.18em] ${isTransparent ? 'text-white/44' : 'text-(--text-faint)'}`}>
                                Mode · Tech · Culture
                            </p>
                        </div>
                    </Link>

                    {/* ── Primary nav ── */}
                    <nav className="hidden items-center gap-1 lg:flex" aria-label="Navigation principale">
                        {PRIMARY_LINKS.map((item) =>
                            item.static ? (
                                <Link key={item.label} to={item.to} className={navLinkTone}>
                                    {item.label}
                                </Link>
                            ) : (
                                <NavLink
                                    key={item.label}
                                    to={item.to}
                                    end={item.end}
                                    className={({ isActive }) => (isActive ? navLinkActive : navLinkTone)}
                                >
                                    {item.label}
                                </NavLink>
                            )
                        )}
                    </nav>

                    {/* ── Actions ── */}
                    <div className="flex items-center gap-2">
                        {/* ── Toggle thème ── */}
                        <button
                            type="button"
                            onClick={toggleTheme}
                            aria-label={theme === 'dark' ? 'Passer en mode clair' : 'Passer en mode sombre'}
                            className={isTransparent ? iconBtn : 'theme-toggle relative flex h-10 w-10 items-center justify-center rounded-full'}
                        >
                            {theme === 'dark'
                                ? <FiSun className="h-4 w-4" />
                                : <FiMoon className="h-4 w-4" />
                            }
                        </button>

                        {isAuthenticated ? (
                            <>
                                <button
                                    type="button"
                                    onClick={() => navigate('/dashboard')}
                                    aria-label={cartCount > 0 ? `Panier, ${cartCount} article${cartCount > 1 ? 's' : ''}` : 'Mon compte'}
                                    className={`hidden sm:inline-flex ${iconBtn}`}
                                >
                                    <FiShoppingBag className="h-4 w-4" />
                                    {cartCount > 0 && (
                                        <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-amber-400 px-1.5 text-[10px] font-bold text-slate-950">
                                            {cartCount > 9 ? '9+' : cartCount}
                                        </span>
                                    )}
                                </button>

                                <NavLink
                                    to="/dashboard"
                                    className={({ isActive }) =>
                                        `hidden sm:inline-flex ${isActive || isDashboardRoute ? actionBtnActive : actionBtn}`
                                    }
                                >
                                    Mon compte
                                </NavLink>

                                {isAdmin && (
                                    <NavLink
                                        to="/admin"
                                        className={({ isActive }) =>
                                            `hidden md:inline-flex ${isActive || isAdminRoute ? actionBtnActive : actionBtn}`
                                        }
                                    >
                                        Admin
                                    </NavLink>
                                )}

                                <button
                                    type="button"
                                    onClick={handleLogout}
                                    className={`hidden sm:inline-flex ${actionBtn}`}
                                >
                                    Déconnexion
                                </button>
                            </>
                        ) : (
                            <>
                                <Link to="/login" className={`hidden sm:inline-flex ${actionBtn}`}>
                                    Connexion
                                </Link>
                                <Link to="/register" className="hidden btn-amber px-5 py-2.5 text-sm sm:inline-flex">
                                    Créer un compte
                                </Link>
                            </>
                        )}

                        <button
                            type="button"
                            onClick={() => setMobileOpen((v) => !v)}
                            aria-label={mobileOpen ? 'Fermer le menu' : 'Ouvrir le menu'}
                            aria-expanded={mobileOpen}
                            aria-controls="mobile-site-menu"
                            className={`inline-flex h-10 w-10 items-center justify-center ${iconBtn} lg:hidden`}
                        >
                            {mobileOpen ? <FiX className="h-5 w-5" /> : <FiMenu className="h-5 w-5" />}
                        </button>
                    </div>
                </div>

                {/* ── Category strip ── */}
                {topCategories.length > 0 && (
                    <div className={`hidden border-t lg:block ${isTransparent ? 'border-white/[0.07]' : 'border-(--border)'}`}>
                        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                            <div className="scrollbar-hide flex items-center gap-2 overflow-x-auto py-2.5">
                                {topCategories.map((category) => (
                                    <Link
                                        key={category.id}
                                        to={`/products?category_id=${category.id}`}
                                        className={`smoke-chip rounded-full px-3.5 py-1.5 text-[10px] font-medium uppercase tracking-widest transition ${
                                            isTransparent
                                                ? 'text-white/52 hover:border-white/16 hover:text-white'
                                                : 'hover:border-(--border-hover)'
                                        }`}
                                    >
                                        {category.name}
                                    </Link>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* ── Mobile drawer ── */}
            {mobileOpen && (
                <>
                    <button
                        type="button"
                        aria-label="Fermer le menu mobile"
                        onClick={closeMobileMenu}
                        className="mobile-menu-backdrop fixed inset-x-0 bottom-0 top-18 z-40 backdrop-blur-sm lg:hidden"
                    />
                    <div
                        id="mobile-site-menu"
                        className="smoke-panel relative z-50 mx-4 mt-2 rounded-2xl p-4 shadow-[0_20px_60px_rgba(0,0,0,0.50)] lg:hidden"
                    >
                        <div className="flex flex-col gap-1">
                            {PRIMARY_LINKS.map((item) =>
                                item.static ? (
                                    <Link
                                        key={item.label}
                                        to={item.to}
                                        onClick={closeMobileMenu}
                                        className="nav-mobile-link flex items-center justify-between rounded-xl px-4 py-3 text-sm font-medium"
                                    >
                                        <span>{item.label}</span>
                                        <FiArrowRight className="h-4 w-4" />
                                    </Link>
                                ) : (
                                    <NavLink
                                        key={item.label}
                                        to={item.to}
                                        end={item.end}
                                        onClick={closeMobileMenu}
                                        className={({ isActive }) =>
                                            `flex items-center justify-between rounded-xl px-4 py-3 text-sm font-medium ${
                                                isActive ? 'nav-mobile-link-active' : 'nav-mobile-link'
                                            }`
                                        }
                                    >
                                        <span>{item.label}</span>
                                        <FiArrowRight className="h-4 w-4" />
                                    </NavLink>
                                )
                            )}
                        </div>

                        <div className="mt-4 border-t border-(--border) pt-4">
                            {isAuthenticated ? (
                                <div className="flex flex-col gap-2">
                                    <NavLink
                                        to="/dashboard"
                                        onClick={closeMobileMenu}
                                        className={({ isActive }) =>
                                            `flex items-center gap-2 rounded-xl px-4 py-3 text-sm font-medium ${
                                                isActive || isDashboardRoute ? 'nav-mobile-link-active' : 'nav-mobile-link'
                                            }`
                                        }
                                    >
                                        <FiUser className="h-4 w-4" />
                                        Mon compte
                                        {cartCount > 0 && (
                                            <span className="ml-auto rounded-full bg-amber-400 px-2 py-0.5 text-[10px] font-bold text-slate-950">
                                                {cartCount}
                                            </span>
                                        )}
                                    </NavLink>

                                    {isAdmin && (
                                        <NavLink
                                            to="/admin"
                                            onClick={closeMobileMenu}
                                            className={({ isActive }) =>
                                                `rounded-xl px-4 py-3 text-sm font-medium ${
                                                    isActive || isAdminRoute ? 'nav-mobile-link-active' : 'nav-mobile-link'
                                                }`
                                            }
                                        >
                                            Espace admin
                                        </NavLink>
                                    )}

                                    <button
                                        type="button"
                                        onClick={handleLogout}
                                        className="nav-mobile-link rounded-xl px-4 py-3 text-left text-sm font-medium"
                                    >
                                        Déconnexion
                                    </button>
                                </div>
                            ) : (
                                <div className="flex flex-col gap-2">
                                    <Link
                                        to="/login"
                                        onClick={closeMobileMenu}
                                        className="nav-mobile-link rounded-xl px-4 py-3 text-sm font-medium"
                                    >
                                        Connexion
                                    </Link>
                                    <Link to="/register" onClick={closeMobileMenu} className="btn-amber w-full px-5 py-3 text-sm">
                                        Créer un compte
                                    </Link>
                                </div>
                            )}
                        </div>

                        {topCategories.length > 0 && (
                            <div className="mt-4 border-t border-(--border) pt-4">
                                <p className="mobile-section-label mb-3 text-[10px] font-semibold uppercase tracking-[0.18em]">
                                    Catégories
                                </p>
                                <div className="flex flex-wrap gap-2">
                                    {topCategories.map((category) => (
                                        <Link
                                            key={category.id}
                                            to={`/products?category_id=${category.id}`}
                                            onClick={closeMobileMenu}
                                            className="smoke-chip rounded-full px-3 py-1.5 text-[10px] font-medium uppercase tracking-widest transition"
                                        >
                                            {category.name}
                                        </Link>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* ── Toggle thème mobile ── */}
                        <div className="mt-4 border-t border-(--border) pt-4">
                            <button
                                type="button"
                                onClick={toggleTheme}
                                className="nav-mobile-link flex w-full items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium"
                            >
                                {theme === 'dark'
                                    ? <><FiSun className="h-4 w-4 text-amber-400" /><span>Mode clair</span></>
                                    : <><FiMoon className="h-4 w-4 text-zinc-400" /><span>Mode sombre</span></>
                                }
                            </button>
                        </div>
                    </div>
                </>
            )}
        </header>
    );
}

export default Navbar;
