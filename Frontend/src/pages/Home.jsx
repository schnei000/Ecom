import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
    FiArrowRight,
    FiClock,
    FiCopy,
    FiHeadphones,
    FiLock,
    FiShoppingBag,
    FiStar,
    FiTruck,
    FiZap,
} from 'react-icons/fi';
import imgElectronique from '../assets/images/electronique.png';
import imgLivres from '../assets/images/livres.png';
import imgVetement from '../assets/images/vetement.png';
import { fetchProducts } from '../api/ProductApi';
import useCategories from '../hooks/useCategories';
import useScrollReveal from '../hooks/useScrollReveal';
import ProductCard from '../components/ProductCard';

const CATEGORY_VISUALS = [
    {
        img: imgElectronique,
        mono: 'TECH',
        overline: 'Technologie',
        eyebrow: 'Performance essentielle',
        description: 'Smartphones, accessoires et matériel informatique sélectionnés pour leur fiabilité et leur rapport qualité-prix.',
        background: 'linear-gradient(180deg, rgba(9,11,16,0.12), rgba(9,11,16,0.58)), radial-gradient(circle at 18% 18%, rgba(240,166,58,0.32), transparent 34%)',
        orb: 'rgba(240,166,58,0.26)',
    },
    {
        img: imgLivres,
        mono: 'LIRE',
        overline: 'Culture',
        eyebrow: 'Culture choisie',
        description: 'Romans, essais, bandes dessinées et guides pratiques pour tous les goûts et tous les âges.',
        background: 'linear-gradient(180deg, rgba(9,11,16,0.12), rgba(9,11,16,0.6)), radial-gradient(circle at 18% 18%, rgba(255,209,125,0.22), transparent 34%)',
        orb: 'rgba(255,255,255,0.18)',
    },
    {
        img: imgVetement,
        mono: 'MODE',
        overline: 'Mode',
        eyebrow: 'Vestiaire contemporain',
        description: 'Vêtements, chaussures et accessoires pour exprimer ton style au quotidien, à prix maîtrisé.',
        background: 'linear-gradient(180deg, rgba(9,11,16,0.12), rgba(9,11,16,0.62)), radial-gradient(circle at 18% 18%, rgba(240,166,58,0.24), transparent 34%)',
        orb: 'rgba(240,166,58,0.18)',
    },
];

const FALLBACK_CATEGORIES = [
    { id: null, name: 'Mode & Vestiaire' },
    { id: null, name: 'Essentiels Tech' },
    { id: null, name: 'Culture & Livres' },
];

const TRUST_ITEMS = [
    { num: '01', icon: FiTruck, title: 'Livraison suivie', text: 'Expédition sous 48h avec suivi en temps réel. Livraison offerte dès 50 USD d\'achat.' },
    { num: '02', icon: FiClock, title: 'Retours simplifiés', text: 'Retourne tes articles sous 30 jours, sans frais et sans justificatif.' },
    { num: '03', icon: FiLock, title: 'Paiement protégé', text: 'Transactions sécurisées par chiffrement SSL. Tes données bancaires ne sont jamais stockées.' },
    { num: '04', icon: FiHeadphones, title: 'Support réactif', text: 'Une équipe disponible 7j/7 pour répondre à tes questions et résoudre tes problèmes.' },
];

const TICKER_ITEMS = [
    'Nouveautés chaque semaine',
    'Livraison offerte dès 50 USD',
    'Paiement sécurisé',
    'Retours sous 30 jours',
    'Sélection éditoriale',
    'Code SUMMER26 -20%',
    'Nouveautés chaque semaine',
    'Livraison offerte dès 50 USD',
    'Paiement sécurisé',
    'Retours sous 30 jours',
    'Sélection éditoriale',
    'Code SUMMER26 -20%',
];

const HERO_METRICS = [
    { value: '10k+', label: 'Produits référencés' },
    { value: '48h', label: 'Expédition premium' },
    { value: '4.9/5', label: 'Satisfaction client' },
];

function normalizeText(value = '') {
    return value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

function getCategoryVisual(categoryName, index) {
    const normalized = normalizeText(categoryName);

    if (normalized.includes('lectronique') || normalized.includes('tech') || normalized.includes('inform')) {
        return CATEGORY_VISUALS[0];
    }
    if (normalized.includes('livre') || normalized.includes('roman') || normalized.includes('book')) {
        return CATEGORY_VISUALS[1];
    }
    if (normalized.includes('vetement') || normalized.includes('mode') || normalized.includes('habit')) {
        return CATEGORY_VISUALS[2];
    }

    return CATEGORY_VISUALS[index % CATEGORY_VISUALS.length];
}

function getMonogram(product, fallback = 'B') {
    const source = product?.name?.trim();
    return source ? source.charAt(0).toUpperCase() : fallback;
}

function HeroSpotlightCard({ product, label, caption, accent = '#f0a63a', compact = false }) {
    const title = product?.name ?? label;
    const subtitle = product?.category_name ?? caption;
    const detail = product?.price != null ? `${product.price.toFixed(2)} USD` : caption;
    const target = product ? `/products/${product.id}` : '/products';

    return (
        <Link
            to={target}
            className={`group rounded-2xl border border-(--border) bg-(--bg-card) p-4 transition hover:border-(--border-hover) ${compact ? '' : 'smoke-panel-soft'}`}
        >
            <div className="flex items-start gap-4">
                <div
                    className="relative flex h-14 w-14 shrink-0 items-center justify-center overflow-hidden rounded-xl"
                    style={{
                        background: `rgba(245,158,11,0.10)`,
                        border: `1px solid rgba(245,158,11,0.16)`,
                    }}
                >
                    <span className="font-display text-2xl font-bold text-amber-400">{getMonogram(product)}</span>
                </div>

                <div className="min-w-0 flex-1">
                    <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-zinc-500">{subtitle}</p>
                    <h3 className="mt-1 line-clamp-2 font-display text-base font-semibold tracking-[-0.02em] text-(--text)">
                        {title}
                    </h3>
                    <p className="mt-1.5 text-sm font-semibold text-amber-400">{detail}</p>
                </div>

                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-(--border) bg-transparent text-zinc-500 transition group-hover:border-amber-400 group-hover:bg-amber-400 group-hover:text-slate-950">
                    <FiArrowRight className="h-4 w-4" />
                </span>
            </div>
        </Link>
    );
}

function Home() {
    const [featuredProducts, setFeaturedProducts] = useState([]);
    const [loadingProducts, setLoadingProducts] = useState(true);
    const { categories } = useCategories();
    const [copiedPromo, setCopiedPromo] = useState(false);

    const trustRef = useScrollReveal();
    const categoryRef = useScrollReveal();
    const productRef = useScrollReveal();
    const promoRef = useScrollReveal();

    useEffect(() => {
        fetchProducts()
            .then((products) => setFeaturedProducts(products.slice(0, 6)))
            .catch(() => setFeaturedProducts([]))
            .finally(() => setLoadingProducts(false));
    }, []);

    const displayCategories = categories.length > 0 ? categories.slice(0, 3) : FALLBACK_CATEGORIES;
    const heroProduct = featuredProducts[0];
    const secondaryProduct = featuredProducts[1];
    const tertiaryProduct = featuredProducts[2];

    const handleCopyPromo = async () => {
        try {
            await navigator.clipboard?.writeText('SUMMER26');
            setCopiedPromo(true);
            setTimeout(() => setCopiedPromo(false), 1800);
        } catch {
            setCopiedPromo(false);
        }
    };

    return (
        <div className="overflow-x-hidden">
            <section className="relative overflow-hidden bg-(--bg-base) pt-24 text-white">
                <div className="relative mx-auto max-w-7xl px-4 pb-20 sm:px-6 lg:px-8">
                    <div className="grid gap-8 lg:grid-cols-[1fr_0.95fr]">
                        <div className="animate-fade-up pt-8 pb-10 lg:pt-16 lg:pb-20">
                            <span className="surface-chip-dark inline-flex items-center gap-2 rounded-full px-4 py-2 text-[10px] font-bold uppercase tracking-[0.16em]">
                                <FiStar className="h-3.5 w-3.5 text-amber-400" />
                                Nouveau — Printemps 2026
                            </span>

                            <h1 className="mt-6 font-display text-[clamp(3.1rem,7vw,6rem)] font-bold leading-[0.92] tracking-[-0.05em] text-(--text)">
                                Le meilleur
                                <br />
                                <span className="text-gradient-brand">du shopping</span>
                                <br />
                                en un endroit.
                            </h1>

                            <p className="mt-6 max-w-2xl text-base leading-7 text-zinc-400 sm:text-lg">
                                Boutik Lakay réunit mode, tech et culture dans une boutique soignée, avec une livraison suivie, des retours simplifiés et des prix qui respectent ton budget.
                            </p>

                            <div className="mt-10 flex flex-wrap gap-3">
                                <Link to="/products" className="btn-amber px-7 py-3.5">
                                    Explorer le catalogue
                                    <FiArrowRight className="h-4 w-4" />
                                </Link>
                                <Link to="/register" className="btn-ghost px-7 py-3.5">
                                    Créer un compte
                                    <FiShoppingBag className="h-4 w-4" />
                                </Link>
                            </div>

                            <div className="mt-12 grid gap-3 sm:grid-cols-3">
                                {HERO_METRICS.map((metric) => (
                                    <div key={metric.label} className="rounded-2xl border border-(--border) bg-(--bg-card) px-5 py-4">
                                        <p className="font-display text-3xl font-bold tracking-[-0.04em] text-(--text)">{metric.value}</p>
                                        <p className="mt-2 text-[11px] uppercase tracking-[0.12em] text-zinc-500">{metric.label}</p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="animate-fade-up delay-200 lg:pt-12 lg:pb-20">
                            <div className="smoke-panel relative overflow-hidden rounded-2xl p-5 sm:p-6 lg:p-7">
                                <div className="relative">
                                    <div className="flex flex-wrap items-center justify-between gap-3">
                                        <span className="smoke-chip inline-flex items-center gap-2 rounded-full px-3 py-2 text-[10px] font-bold uppercase tracking-[0.14em]">
                                            <FiZap className="h-3.5 w-3.5 text-amber-400" />
                                            Sélection du moment
                                        </span>
                                        <span className="smoke-chip-soft rounded-full px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.14em]">
                                            Nouveautés 2026
                                        </span>
                                    </div>

                                    <div className="mt-5 grid gap-4 xl:grid-cols-[1.05fr_0.95fr]">
                                        <div className="smoke-panel-soft rounded-2xl p-5">
                                            <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-amber-400">
                                                Nos engagements
                                            </p>
                                            <h2 className="mt-4 font-display text-[clamp(2.1rem,4vw,3.25rem)] font-bold leading-[0.96] tracking-[-0.04em] text-(--text)">
                                                Qualité.
                                                <br />
                                                Rapidité.
                                                <br />
                                                Confiance.
                                            </h2>
                                            <p className="mt-4 max-w-md text-sm leading-6 text-zinc-400">
                                                Des produits vérifiés, expédiés rapidement et retournables facilement. Boutik Lakay, c&apos;est le shopping sans compromis.
                                            </p>

                                            <div className="mt-6 grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                                                {['Livraison 48h', 'Retours 30j', 'Paiement sécurisé'].map((item) => (
                                                    <span key={item} className="smoke-chip rounded-full px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.12em]">
                                                        {item}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="grid gap-3">
                                            <HeroSpotlightCard
                                                product={heroProduct}
                                                label="Capsule Signature"
                                                caption="Produit vedette"
                                                accent="#f0a63a"
                                            />
                                            <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
                                                <HeroSpotlightCard
                                                    product={secondaryProduct}
                                                    label="Collection Quotidien"
                                                    caption="Nouveau drop"
                                                    accent="#ffd17d"
                                                    compact
                                                />

                                                <button
                                                    type="button"
                                                    onClick={handleCopyPromo}
                                                    className="rounded-2xl border border-amber-400/20 bg-[rgba(245,158,11,0.06)] p-4 text-left transition hover:border-amber-400/30 hover:bg-[rgba(245,158,11,0.09)]"
                                                >
                                                    <div className="flex items-start justify-between gap-4">
                                                        <div>
                                                            <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-amber-400">Code promo</p>
                                                            <p className="mt-3 font-display text-3xl font-bold tracking-[0.08em] text-(--text)">SUMMER26</p>
                                                            <p className="mt-2 text-sm text-zinc-400">
                                                                {copiedPromo ? 'Code copié' : 'Clique pour copier et activer -20%'}
                                                            </p>
                                                        </div>
                                                        <span className="smoke-chip flex h-9 w-9 items-center justify-center rounded-full">
                                                            <FiCopy className="h-4 w-4" />
                                                        </span>
                                                    </div>
                                                </button>
                                            </div>

                                            <HeroSpotlightCard
                                                product={tertiaryProduct}
                                                label="Edition Maison"
                                                caption="Sélection raffinée"
                                                accent="#f3b357"
                                                compact
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <section ref={trustRef} className="relative -mt-8 pb-4">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                        {TRUST_ITEMS.map((item, index) => (
                            <article
                                key={item.title}
                                className="trust-card reveal p-5"
                                style={{ animationDelay: `${index * 0.08}s` }}
                            >
                                <div className="flex items-start justify-between gap-4">
                                    <div>
                                        <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-zinc-600">{item.num}</p>
                                        <h3 className="mt-3 font-display text-xl font-semibold tracking-[-0.03em] text-(--text)">
                                            {item.title}
                                        </h3>
                                        <p className="mt-3 text-sm leading-6 text-zinc-400">{item.text}</p>
                                    </div>
                                    <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl border border-amber-400/20 bg-amber-400/08 text-amber-400">
                                        <item.icon className="h-5 w-5" />
                                    </span>
                                </div>
                            </article>
                        ))}
                    </div>
                </div>
            </section>

            <div className="smoke-band mt-8 overflow-hidden border-y border-(--border) py-3">
                <div className="ticker-track">
                    {TICKER_ITEMS.map((item, index) => (
                        <span key={`${item}-${index}`} className="mx-8 whitespace-nowrap text-[11px] font-semibold uppercase tracking-[0.16em] text-zinc-500">
                            {item}
                        </span>
                    ))}
                </div>
            </div>

            <section ref={categoryRef} className="section-shell py-24">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="mb-12 grid gap-6 lg:grid-cols-[1fr_auto] lg:items-end">
                        <div className="reveal">
                            <span className="section-kicker">Univers</span>
                            <h2 className="section-title">Explorez nos univers.</h2>
                            <p className="mt-4 max-w-2xl text-sm leading-7 text-zinc-400 sm:text-base">
                                Mode, tech et culture : tout ce dont tu as besoin, réuni en un seul endroit avec une sélection renouvelée chaque semaine.
                            </p>
                        </div>

                        <div className="reveal smoke-panel rounded-2xl px-5 py-4">
                            <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-amber-400">Sélection</p>
                            <p className="mt-2 max-w-xs text-sm leading-6 text-zinc-400">
                                Chaque catégorie est mise à jour régulièrement avec les meilleures références du moment.
                            </p>
                        </div>
                    </div>

                    <div className="grid gap-4 lg:grid-cols-3 lg:grid-rows-2">
                        {displayCategories.map((category, index) => {
                            const visual = getCategoryVisual(category.name, index);
                            const isLead = index === 0;

                            return (
                                <Link
                                    key={category.id ?? category.name}
                                    to={category.id ? `/products?category_id=${category.id}` : '/products'}
                                    className={`category-card reveal group flex min-h-72 flex-col justify-between p-5 sm:p-6 ${
                                        isLead ? 'lg:row-span-2 lg:min-h-[31rem]' : 'lg:min-h-60'
                                    }`}
                                    style={{ animationDelay: `${index * 0.08}s` }}
                                >
                                    <div className="absolute inset-0 overflow-hidden">
                                        <img
                                            src={visual.img}
                                            alt={category.name}
                                            loading="lazy"
                                            className="h-full w-full object-cover transition-transform duration-700 group-hover:scale-105"
                                        />
                                    </div>
                                    <div className="absolute inset-0 opacity-95" style={{ background: visual.background }} />
                                    <div className="absolute inset-0 bg-linear-to-t from-[#11161d]/88 via-[#11161d]/28 to-transparent" />
                                    <span className="pointer-events-none absolute -right-3 bottom-1 font-display text-[4.8rem] font-bold tracking-[-0.06em] text-white/[0.07] sm:text-[6.5rem]">
                                        {visual.mono}
                                    </span>

                                    <div className="relative flex items-start justify-between gap-4">
                                        <div>
                                            <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-amber-300">{visual.overline}</p>
                                            <p className="mt-2 text-sm text-white/58">{visual.eyebrow}</p>
                                        </div>
                                        <span className="smoke-chip-soft rounded-full px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.12em]">
                                            Catégorie
                                        </span>
                                    </div>

                                    <div className="relative">
                                        <h3 className={`font-display font-bold tracking-[-0.04em] text-white ${isLead ? 'text-4xl' : 'text-[1.9rem]'}`}>
                                            {category.name}
                                        </h3>
                                        <p className="mt-3 max-w-sm text-sm leading-6 text-white/62">{visual.description}</p>
                                        <span className="mt-5 inline-flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.12em] text-amber-300">
                                            Découvrir la sélection
                                            <FiArrowRight className="h-3.5 w-3.5" />
                                        </span>
                                    </div>
                                </Link>
                            );
                        })}
                    </div>
                </div>
            </section>

            <section ref={productRef} className="section-shell py-24">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="mb-12 flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
                        <div className="reveal">
                            <span className="section-kicker">Sélection</span>
                            <h2 className="section-title">Notre sélection du moment.</h2>
                            <p className="mt-4 max-w-2xl text-sm leading-7 text-zinc-400 sm:text-base">
                                Des produits choisis pour leur qualité, leur utilité et leur rapport qualité-prix. Retrouvez l&apos;ensemble du catalogue sur la page dédiée.
                            </p>
                        </div>

                        <Link to="/products" className="btn-outline reveal px-6 py-3 text-sm">
                            Voir tout le catalogue
                            <FiArrowRight className="h-4 w-4" />
                        </Link>
                    </div>

                    {loadingProducts ? (
                        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                            {Array.from({ length: 4 }).map((_, index) => (
                                <div key={index} className="smoke-panel rounded-2xl p-3">
                                    <div className="aspect-[4/4.2] animate-pulse rounded-xl bg-(--surface)" />
                                    <div className="space-y-3 px-2 pb-2 pt-4">
                                        <div className="h-2.5 w-1/3 animate-pulse rounded-full bg-(--surface)" />
                                        <div className="h-4 animate-pulse rounded-full bg-(--surface)" />
                                        <div className="h-4 w-1/2 animate-pulse rounded-full bg-(--surface)" />
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : featuredProducts.length === 0 ? (
                        <div className="smoke-panel rounded-2xl px-6 py-20 text-center">
                            <p className="font-display text-3xl font-bold tracking-[-0.03em] text-(--text)">Aucun produit disponible.</p>
                            <p className="mt-3 text-sm leading-6 text-zinc-400">
                                La vitrine est prête, mais aucun article n&apos;est encore remonté par l&apos;API.
                            </p>
                        </div>
                    ) : (
                        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                            {featuredProducts.slice(0, 4).map((product, index) => (
                                <div key={product.id} className="reveal" style={{ animationDelay: `${index * 0.08}s` }}>
                                    <ProductCard product={product} />
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </section>

            <section ref={promoRef} className="section-shell pb-24">
                <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
                    <div className="smoke-panel reveal relative overflow-hidden rounded-2xl px-6 py-16 sm:px-8 lg:px-12">
                        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center opacity-[0.04]">
                            <span className="font-display text-[18vw] font-bold uppercase tracking-[-0.06em] text-white">
                                SALE
                            </span>
                        </div>

                        <div className="relative grid gap-8 lg:grid-cols-[1fr_auto] lg:items-end">
                            <div>
                                <span className="section-kicker">Offre du moment</span>
                                <h2 className="mt-4 font-display text-[clamp(2.3rem,5vw,4.6rem)] font-bold leading-[0.96] tracking-[-0.04em] text-(--text)">
                                    −20% sur toute la sélection estivale.
                                </h2>
                                <p className="mt-5 max-w-2xl text-base leading-7 text-zinc-400">
                                    Copie le code, applique-le au panier. Valable jusqu&apos;au 31 août 2026 sur mode, tech et culture. Non cumulable.
                                </p>
                            </div>

                            <div className="rounded-2xl border border-(--border) bg-(--bg-elevated) p-5">
                                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-zinc-500">Code promo actif</p>
                                <p className="mt-3 font-display text-4xl font-bold tracking-[0.08em] text-amber-400">SUMMER26</p>
                                <p className="mt-2 text-sm text-zinc-400">−20% · Collection estivale 2026</p>
                                <div className="mt-5 flex flex-col gap-3">
                                    <button type="button" onClick={handleCopyPromo} className="btn-amber w-full px-6 py-3.5 text-sm">
                                        {copiedPromo ? '✓ Code copié !' : 'Copier le code'}
                                    </button>
                                    <Link to="/products" className="btn-ghost w-full px-6 py-3.5 text-sm">
                                        Parcourir la sélection
                                    </Link>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}

export default Home;
