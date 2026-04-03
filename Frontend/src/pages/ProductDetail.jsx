import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
    FiArrowLeft,
    FiCheckCircle,
    FiMinus,
    FiPlus,
    FiShield,
    FiShoppingBag,
    FiTag,
    FiTruck,
    FiZap,
} from 'react-icons/fi';
import { fetchProduct } from '../api/ProductApi';
import { addToCart } from '../api/cartApi';
import useAuth from '../hooks/useAuth';
import Loading from '../components/Loading';

const PRODUCT_ARTS = [
    {
        label: 'Tech edit',
        background: 'radial-gradient(circle at top left, rgba(240,166,58,0.30), transparent 34%), linear-gradient(135deg, #141922 0%, #1d2430 50%, #10141b 100%)',
        accent: 'rgba(240,166,58,0.22)',
    },
    {
        label: 'Culture edit',
        background: 'radial-gradient(circle at top left, rgba(255,209,125,0.20), transparent 36%), linear-gradient(135deg, #17191f 0%, #232732 50%, #12151b 100%)',
        accent: 'rgba(255,255,255,0.16)',
    },
    {
        label: 'Style edit',
        background: 'radial-gradient(circle at top left, rgba(240,166,58,0.18), transparent 36%), linear-gradient(135deg, #19171d 0%, #262029 50%, #12151b 100%)',
        accent: 'rgba(240,166,58,0.18)',
    },
];

const DETAIL_FEATURES = [
    { icon: FiTruck, title: 'Expédition premium', text: '48h en moyenne' },
    { icon: FiShield, title: 'Paiement sécurisé', text: 'Checkout protégé' },
    { icon: FiCheckCircle, title: 'Retours fluides', text: 'Sous 30 jours' },
];

function normalizeText(value = '') {
    return value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

function getProductArt(product) {
    const search = normalizeText(`${product.name} ${product.category_name ?? ''}`);

    if (search.includes('tech') || search.includes('lectronique') || search.includes('phone') || search.includes('ordi')) {
        return PRODUCT_ARTS[0];
    }
    if (search.includes('livre') || search.includes('roman') || search.includes('book') || search.includes('culture')) {
        return PRODUCT_ARTS[1];
    }
    if (search.includes('mode') || search.includes('vetement') || search.includes('style') || search.includes('habit')) {
        return PRODUCT_ARTS[2];
    }

    return PRODUCT_ARTS[product.id % PRODUCT_ARTS.length];
}

function ProductMedia({ product, inStock }) {
    const art = getProductArt(product);
    const [imageError, setImageError] = useState(false);

    if (product.image_url && !imageError) {
        return (
            <div className="relative h-full overflow-hidden rounded-[2.3rem]">
                <img
                    src={product.image_url}
                    alt={product.name}
                    onError={() => setImageError(true)}
                    className="h-[24rem] w-full object-cover md:h-[34rem]"
                    loading="eager"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#10141b]/78 via-transparent to-transparent" />
                <span className="smoke-chip-soft absolute left-5 top-5 inline-flex items-center gap-2 rounded-full px-3 py-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/74">
                    <FiZap className="h-3.5 w-3.5 text-amber-300" />
                    {art.label}
                </span>
                {!inStock && (
                    <div className="absolute inset-0 flex items-center justify-center bg-[#10141b]/60 backdrop-blur-[2px]">
                        <span className="rounded-full border border-white/14 bg-black/70 px-6 py-3 text-sm font-bold uppercase tracking-[0.22em] text-white/74">
                            Rupture de stock
                        </span>
                    </div>
                )}
            </div>
        );
    }

    return (
        <div className="relative flex min-h-[24rem] w-full flex-col justify-between overflow-hidden rounded-[2.3rem] p-6 md:min-h-[34rem] md:p-8" style={{ background: art.background }}>
            <span className="smoke-chip-soft inline-flex w-fit items-center gap-2 rounded-full px-3 py-2 text-[10px] font-bold uppercase tracking-[0.18em] text-white/72">
                <FiZap className="h-3.5 w-3.5 text-amber-300" />
                {art.label}
            </span>

            <div className="pointer-events-none absolute -right-5 bottom-0 font-display text-[8rem] font-bold tracking-[-0.08em] text-white/[0.08] md:text-[10rem]">
                {product.name.charAt(0).toUpperCase()}
            </div>

            <div className="pointer-events-none absolute right-8 top-10 h-28 w-28 rounded-full blur-3xl" style={{ background: art.accent }} />

            <div className="relative max-w-md">
                <p className="text-[10px] font-bold uppercase tracking-[0.24em] text-white/44">
                    {product.category_name ?? `Categorie #${product.category_id}`}
                </p>
                <h2 className="mt-4 font-display text-[clamp(2.6rem,6vw,5rem)] font-bold leading-[0.92] tracking-[-0.06em] text-white">
                    {product.name}
                </h2>
            </div>

            {!inStock && (
                <div className="absolute inset-0 flex items-center justify-center bg-[#10141b]/50 backdrop-blur-[2px]">
                    <span className="rounded-full border border-white/14 bg-black/70 px-6 py-3 text-sm font-bold uppercase tracking-[0.22em] text-white/74">
                        Rupture de stock
                    </span>
                </div>
            )}
        </div>
    );
}

function ProductDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const { isAuthenticated, token } = useAuth();

    const [product, setProduct] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [quantity, setQuantity] = useState(1);
    const [adding, setAdding] = useState(false);

    useEffect(() => {
        fetchProduct(id)
            .then(setProduct)
            .catch((err) => setError(err.message))
            .finally(() => setLoading(false));
    }, [id]);

    const handleAddToCart = async () => {
        setAdding(true);
        const loadingToast = toast.loading('Ajout au panier...');

        try {
            await addToCart(product.id, quantity, token);
            toast.success(`${quantity} x "${product.name}" ajouté au panier.`, { id: loadingToast });
            window.dispatchEvent(new Event('cart-updated'));
            setQuantity(1);
        } catch (err) {
            toast.error(err.message || "Erreur lors de l'ajout au panier", { id: loadingToast });
        } finally {
            setAdding(false);
        }
    };

    if (loading) return <Loading fullScreen />;

    if (error || !product) {
        return (
            <div className="flex min-h-[70vh] items-center justify-center px-4 pt-20">
                <div className="smoke-panel max-w-xl rounded-[2.2rem] px-6 py-12 text-center">
                    <p className="font-display text-3xl font-bold tracking-[-0.05em] text-white">Produit introuvable.</p>
                    <p className="mt-3 text-sm leading-6 text-white/48">{error ?? "Ce produit n’est plus disponible dans le catalogue."}</p>
                    <button
                        type="button"
                        onClick={() => navigate('/products')}
                        className="btn-outline mt-6 px-6 py-3 text-sm"
                    >
                        <FiArrowLeft className="h-4 w-4" />
                        Retour au catalogue
                    </button>
                </div>
            </div>
        );
    }

    const inStock = product.stock > 0;
    const maxQty = Math.max(1, Math.min(product.stock, 99));

    return (
        <div className="min-h-screen pt-20 pb-20">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                <nav className="mb-6 flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.16em] text-white/36">
                    <Link to="/" className="transition hover:text-white">Accueil</Link>
                    <span>/</span>
                    <Link to="/products" className="transition hover:text-white">Catalogue</Link>
                    <span>/</span>
                    <span className="truncate text-white/52">{product.name}</span>
                </nav>

                <div className="grid gap-6 lg:grid-cols-[0.92fr_1.08fr]">
                    <div className="space-y-4 lg:sticky lg:top-24 lg:self-start">
                        <div className="smoke-panel rounded-[2.5rem] p-3">
                            <ProductMedia product={product} inStock={inStock} />
                        </div>

                        <div className="grid gap-3 sm:grid-cols-3">
                            {DETAIL_FEATURES.map((item) => (
                                <div key={item.title} className="smoke-panel rounded-[1.6rem] p-4">
                                    <span className="flex h-11 w-11 items-center justify-center rounded-[1rem] border border-amber-400/22 bg-amber-400/10 text-amber-300">
                                        <item.icon className="h-[1.1rem] w-[1.1rem]" />
                                    </span>
                                    <p className="mt-4 text-sm font-semibold text-white">{item.title}</p>
                                    <p className="mt-1 text-sm text-white/44">{item.text}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-6">
                        <section className="surface-panel rounded-[2.5rem] p-6 sm:p-8">
                            <div className="flex flex-wrap items-center gap-3">
                                <span className="tag tag-amber">
                                    <FiTag className="h-3 w-3" />
                                    {product.category_name ?? `Categorie #${product.category_id}`}
                                </span>
                                {inStock ? (
                                    <span className="tag tag-green">En stock ({product.stock})</span>
                                ) : (
                                    <span className="tag tag-red">Rupture de stock</span>
                                )}
                            </div>

                            <h1 className="mt-5 font-display text-[clamp(2.2rem,5vw,4.1rem)] font-bold leading-[0.96] tracking-[-0.06em] text-white">
                                {product.name}
                            </h1>

                            <p className="mt-5 max-w-3xl text-base leading-8 text-white/52">
                                {product.description ? product.description.slice(0, 160) : 'Découvrez ce produit en détail : prix, disponibilité et ajout au panier en quelques secondes.'}
                            </p>

                            <div className="mt-8 flex flex-wrap items-end gap-6 border-t border-white/10 pt-8">
                                <div>
                                    <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-white/38">Prix</p>
                                    <p className="mt-3 font-display text-5xl font-bold tracking-[-0.06em] text-white">
                                        {Number(product.price ?? 0).toFixed(2)}
                                        <span className="ml-2 text-xl font-semibold text-white/38">USD</span>
                                    </p>
                                </div>

                                <div className="rounded-[1.5rem] border border-white/10 bg-white/[0.05] px-5 py-4">
                                    <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-white/38">Disponibilité</p>
                                    <p className={`mt-2 text-sm font-semibold ${inStock ? 'text-emerald-400' : 'text-rose-400'}`}>
                                        {inStock ? `${product.stock} unités prêtes à partir` : 'Actuellement indisponible'}
                                    </p>
                                </div>
                            </div>
                        </section>

                        <section className="surface-panel rounded-[2.2rem] p-6 sm:p-8">
                            <div className="grid gap-6 lg:grid-cols-[1fr_auto]">
                                <div>
                                    <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-white/38">Description</p>
                                    <p className="mt-4 text-sm leading-7 text-white/52 sm:text-base">
                                        {product.description || 'Ce produit a été sélectionné pour sa qualité, sa fiabilité et son bon équilibre entre usage quotidien et rapport qualité-prix.'}
                                    </p>
                                </div>

                                <div className="rounded-[1.6rem] border border-white/10 bg-white/[0.05] px-5 py-5 lg:min-w-[15rem]">
                                    <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-white/38">Référence</p>
                                    <p className="mt-2 font-semibold text-white">Produit #{product.id}</p>
                                    <p className="mt-4 text-[10px] font-bold uppercase tracking-[0.22em] text-white/38">Univers</p>
                                    <p className="mt-2 text-sm font-semibold text-white">
                                        {product.category_name ?? 'Catalogue général'}
                                    </p>
                                </div>
                            </div>
                        </section>

                        {!isAuthenticated ? (
                            <section className="smoke-panel rounded-[2.2rem] p-6 text-white sm:p-8">
                                <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-white/40">Action</p>
                                <h2 className="mt-4 font-display text-3xl font-bold tracking-[-0.05em]">
                                    Connecte-toi pour ajouter ce produit à ton panier.
                                </h2>
                                <p className="mt-4 max-w-2xl text-sm leading-7 text-white/58">
                                    En te connectant, tu pourras suivre ta sélection, gérer tes commandes et finaliser ton achat plus rapidement.
                                </p>
                                <div className="mt-6">
                                    <Link to="/login" className="btn-amber px-7 py-3.5 text-sm">
                                        Se connecter
                                    </Link>
                                </div>
                            </section>
                        ) : !inStock ? (
                            <section className="smoke-panel rounded-[2rem] px-6 py-10">
                                <p className="font-display text-3xl font-bold tracking-[-0.04em] text-white">Produit momentanément indisponible.</p>
                                <p className="mt-3 text-sm leading-6 text-white/48">
                                    Tu peux revenir au catalogue pour découvrir les autres sélections actuellement en stock.
                                </p>
                            </section>
                        ) : (
                            <section className="smoke-panel rounded-[2.3rem] p-6 text-white sm:p-8">
                                <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
                                    <div>
                                        <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-white/40">Ajouter au panier</p>
                                        <h2 className="mt-4 font-display text-3xl font-bold tracking-[-0.05em]">
                                            Finalise ton choix en quelques secondes.
                                        </h2>
                                        <p className="mt-4 max-w-2xl text-sm leading-7 text-white/58">
                                            Ajuste la quantité, vérifie le sous-total et ajoute le produit à ton panier sans friction.
                                        </p>
                                    </div>

                                    <div className="rounded-[1.6rem] border border-white/10 bg-white/[0.05] px-5 py-4">
                                        <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-white/40">Sous-total</p>
                                        <p className="mt-2 font-display text-4xl font-bold tracking-[-0.05em] text-white">
                                            {(Number(product.price ?? 0) * quantity).toFixed(2)}
                                            <span className="ml-2 text-lg font-semibold text-white/42">USD</span>
                                        </p>
                                    </div>
                                </div>

                                <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-stretch">
                                    <div className="smoke-chip-soft flex items-center overflow-hidden rounded-full">
                                        <button
                                            type="button"
                                            onClick={() => setQuantity((current) => Math.max(1, current - 1))}
                                            aria-label="Diminuer la quantité"
                                            className="flex h-12 w-12 items-center justify-center text-white/60 transition hover:bg-white/[0.05] hover:text-white"
                                        >
                                            <FiMinus className="h-4 w-4" />
                                        </button>

                                        <span className="min-w-12 text-center text-sm font-bold text-white">{quantity}</span>

                                        <button
                                            type="button"
                                            onClick={() => setQuantity((current) => Math.min(maxQty, current + 1))}
                                            aria-label="Augmenter la quantité"
                                            className="flex h-12 w-12 items-center justify-center text-white/60 transition hover:bg-white/[0.05] hover:text-white"
                                        >
                                            <FiPlus className="h-4 w-4" />
                                        </button>
                                    </div>

                                    <button
                                        type="button"
                                        onClick={handleAddToCart}
                                        disabled={adding}
                                        className="btn-amber flex flex-1 items-center justify-center gap-2 px-7 py-3.5 text-sm disabled:cursor-not-allowed disabled:opacity-55"
                                    >
                                        {adding ? (
                                            <>
                                                <Loading size="sm" />
                                                Ajout en cours...
                                            </>
                                        ) : (
                                            <>
                                                <FiShoppingBag className="h-4 w-4" />
                                                Ajouter au panier
                                            </>
                                        )}
                                    </button>
                                </div>
                            </section>
                        )}

                        <button
                            type="button"
                            onClick={() => navigate('/products')}
                            className="button-secondary inline-flex items-center gap-2 self-start px-6 py-3 text-sm"
                        >
                            <FiArrowLeft className="h-4 w-4" />
                            Retour au catalogue
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default ProductDetail;
