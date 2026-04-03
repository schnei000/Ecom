import { Link } from 'react-router-dom';
import { FiArrowRight, FiHome } from 'react-icons/fi';

function NotFound() {
    return (
        <div className="flex min-h-screen items-center justify-center px-4 pt-20 pb-20">
            <div className="smoke-panel w-full max-w-xl rounded-2xl p-10 text-center">
                <p className="section-kicker justify-center">Erreur 404</p>
                <p className="mt-4 font-display text-[8rem] font-bold leading-none tracking-[-0.06em] text-white opacity-10">404</p>
                <h1 className="mt-2 font-display text-4xl font-bold tracking-[-0.05em] text-white">Page introuvable.</h1>
                <p className="mx-auto mt-4 max-w-sm text-sm leading-7 text-zinc-400">
                    Cette page n&apos;existe pas ou a été déplacée. Retourne à l&apos;accueil ou explore le catalogue.
                </p>
                <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
                    <Link to="/" className="btn-amber px-6 py-3 text-sm">
                        <FiHome className="h-4 w-4" />
                        Retour à l&apos;accueil
                    </Link>
                    <Link to="/products" className="btn-ghost px-6 py-3 text-sm">
                        Explorer le catalogue
                        <FiArrowRight className="h-4 w-4" />
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default NotFound;
