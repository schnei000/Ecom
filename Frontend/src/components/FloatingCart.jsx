import { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiShoppingBag } from 'react-icons/fi';
import useAuth from '../hooks/useAuth';
import CartContext from '../context/cart/CartContext';

function FloatingCart() {
    const { isAuthenticated } = useAuth();
    const { cartCount } = useContext(CartContext);
    const navigate = useNavigate();
    const itemLabel = `${cartCount} article${cartCount > 1 ? 's' : ''}`;

    if (!isAuthenticated) return null;

    return (
        <button
            type="button"
            onClick={() => navigate('/dashboard')}
            className="fixed bottom-[calc(1.25rem+env(safe-area-inset-bottom))] right-[calc(1.25rem+env(safe-area-inset-right))] z-40 transition duration-300 hover:-translate-y-1 sm:bottom-[calc(2rem+env(safe-area-inset-bottom))] sm:right-[calc(2rem+env(safe-area-inset-right))]"
            aria-label={cartCount > 0 ? `Ouvrir mon panier, ${itemLabel}` : 'Ouvrir mon panier'}
        >
            <span className="absolute inset-0 rounded-full bg-amber-400/16 blur-2xl" />
            <span className="smoke-panel relative flex items-center gap-3 rounded-full px-4 py-3 text-white transition hover:border-white/16">
                <span className="flex h-11 w-11 items-center justify-center rounded-full border border-amber-400/26 bg-amber-400/12 text-amber-300 shadow-[0_12px_30px_rgba(0,0,0,0.28)]">
                    <FiShoppingBag className="h-[18px] w-[18px]" />
                </span>
                <span className="hidden text-left sm:block">
                    <span className="block text-[10px] uppercase tracking-[0.18em] text-white/40">Panier</span>
                    <span className="block text-sm font-semibold text-white">Mon panier</span>
                </span>
                {cartCount > 0 && (
                    <span className="flex min-h-7 min-w-7 items-center justify-center rounded-full bg-amber-400 px-2 text-xs font-bold text-slate-950" aria-live="polite">
                        {cartCount > 99 ? '99+' : cartCount}
                    </span>
                )}
            </span>
        </button>
    );
}

export default FloatingCart;
