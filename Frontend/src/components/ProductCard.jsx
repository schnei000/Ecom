import { useState } from 'react';
import { Link } from 'react-router-dom';
import { FiArrowRight } from 'react-icons/fi';

const FALLBACK_THEMES = [
    {
        badge: 'Tech edit',
    },
    {
        badge: 'Culture edit',
    },
    {
        badge: 'Style edit',
    },
];

function normalizeText(value = '') {
    return value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
}

function getFallbackTheme(product) {
    const search = normalizeText(`${product.name} ${product.category_name ?? ''}`);

    if (search.includes('tech') || search.includes('lectronique') || search.includes('phone') || search.includes('ordi')) {
        return FALLBACK_THEMES[0];
    }
    if (search.includes('livre') || search.includes('roman') || search.includes('culture')) {
        return FALLBACK_THEMES[1];
    }
    if (search.includes('mode') || search.includes('vetement') || search.includes('style')) {
        return FALLBACK_THEMES[2];
    }

    return FALLBACK_THEMES[product.id % FALLBACK_THEMES.length];
}

function ProductCard({ product }) {
    const inStock = product.stock > 0;
    const [imageError, setImageError] = useState(false);

    const theme = getFallbackTheme(product);
    const imageUrl = product.image_url || null;
    const showImage = imageUrl && !imageError;

    return (
        <Link to={`/products/${product.id}`} className="product-card-dark group flex h-full flex-col">
            {/* ── Image / Fallback ── */}
            <div
                className="relative m-3 overflow-hidden rounded-xl border border-(--border) bg-(--bg-elevated)"
                style={{ aspectRatio: '4 / 4.15' }}
            >
                {showImage ? (
                    <img
                        src={imageUrl}
                        alt={product.name}
                        onError={() => setImageError(true)}
                        loading="lazy"
                        className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-103"
                    />
                ) : (
                    <div className="relative flex h-full flex-col justify-between p-5 bg-(--bg-elevated)">
                        <span className="inline-flex w-fit rounded-full border border-(--border) bg-(--surface) px-3 py-1.5 text-[9px] font-semibold uppercase tracking-[0.12em] text-zinc-500">
                            {theme.badge}
                        </span>

                        <span className="pointer-events-none absolute -right-4 bottom-0 font-display text-[6.25rem] font-bold tracking-[-0.06em] text-white/[0.05]">
                            {product.name.charAt(0).toUpperCase()}
                        </span>

                        <div className="relative">
                            <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-zinc-500">
                                {product.category_name ?? 'Produit'}
                            </p>
                            <p className="mt-2 max-w-[72%] font-display text-[1.9rem] font-bold leading-none tracking-[-0.04em] text-(--text)">
                                {product.name}
                            </p>
                        </div>
                    </div>
                )}

                {/* Gradient overlay */}
                <div className="absolute inset-0 bg-linear-to-t from-(--bg-base)/70 via-transparent to-transparent" />

                {/* Top badges */}
                <div className="absolute left-3 top-3 flex flex-wrap items-center gap-1.5">
                    <span className="rounded-full border border-(--border) bg-(--bg-elevated)/80 px-2.5 py-1 text-[9px] font-semibold uppercase tracking-widest text-(--text-soft) backdrop-blur-sm">
                        {product.category_name ?? theme.badge}
                    </span>
                    <span className={`rounded-full px-2.5 py-1 text-[9px] font-semibold uppercase tracking-widest ${
                        inStock
                            ? 'border border-emerald-400/20 bg-emerald-400/10 text-emerald-400'
                            : 'border border-rose-400/20 bg-rose-400/10 text-rose-400'
                    }`}>
                        {inStock ? 'En stock' : 'Indisponible'}
                    </span>
                </div>
            </div>

            {/* ── Info ── */}
            <div className="flex flex-1 flex-col gap-3 px-4 pb-4 pt-1">
                <h3 className="line-clamp-2 min-h-[2.8rem] font-display text-[1.05rem] font-semibold leading-6 tracking-[-0.02em] text-(--text)">
                    {product.name}
                </h3>

                <div className="mt-auto flex items-end justify-between gap-3 pt-1">
                    <div>
                        <p className="font-display text-xl font-bold tracking-[-0.04em] text-(--text)">
                            {Number(product.price ?? 0).toFixed(2)}
                            <span className="ml-1 text-sm font-medium text-(--text-soft)">USD</span>
                        </p>
                        <p className={`mt-1 text-xs font-medium ${inStock ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {inStock ? `${product.stock} en stock` : 'Rupture de stock'}
                        </p>
                    </div>

                    <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-(--border) bg-transparent text-zinc-500 transition-all duration-200 group-hover:border-amber-400/50 group-hover:bg-amber-400 group-hover:text-slate-950">
                        <FiArrowRight className="h-4 w-4" />
                    </span>
                </div>
            </div>
        </Link>
    );
}

export default ProductCard;
