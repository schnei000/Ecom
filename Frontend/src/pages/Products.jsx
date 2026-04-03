import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { FiArrowDown, FiGrid, FiSearch, FiSliders, FiX } from 'react-icons/fi';
import ProductCard from '../components/ProductCard.jsx';
import { fetchProducts } from '../api/ProductApi.js';
import useCategories from '../hooks/useCategories.js';

function Products() {
    const [searchParams, setSearchParams] = useSearchParams();
    const activeCategoryId = searchParams.get('category_id')
        ? Number.parseInt(searchParams.get('category_id'), 10)
        : null;

    const [allProducts, setAllProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [sort, setSort] = useState('');
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);

    const { categories } = useCategories();

    // Reset pagination when filters/sort change
    useEffect(() => {
        setPage(1);
        setAllProducts([]);
        setHasMore(true);
    }, [activeCategoryId, searchTerm, sort]);

    // Main fetch effect
    useEffect(() => {
        let active = true;

        const timer = setTimeout(() => {
            if (!active) return;
            setLoading(true);
            setError(null);

            fetchProducts({ categoryId: activeCategoryId, search: searchTerm, sort, page })
                .then((items) => {
                    if (!active) return;
                    setAllProducts((prev) => page === 1 ? items : [...prev, ...items]);
                    setHasMore(items.length === 12);
                })
                .catch((err) => {
                    if (!active) return;
                    setError(err.message);
                })
                .finally(() => {
                    if (!active) return;
                    setLoading(false);
                });
        }, page === 1 ? 260 : 0);

        return () => { active = false; clearTimeout(timer); };
    }, [activeCategoryId, searchTerm, sort, page]);

    const activeCategory = useMemo(
        () => categories.find((category) => category.id === activeCategoryId),
        [categories, activeCategoryId]
    );

    // Client-side sort as fallback (backend may not support sort param yet)
    const sortedProducts = useMemo(() => {
        if (!sort || allProducts.length === 0) return allProducts;
        const arr = [...allProducts];
        if (sort === 'price_asc') arr.sort((a, b) => Number(a.price) - Number(b.price));
        if (sort === 'price_desc') arr.sort((a, b) => Number(b.price) - Number(a.price));
        if (sort === 'name_asc') arr.sort((a, b) => a.name.localeCompare(b.name, 'fr'));
        return arr;
    }, [allProducts, sort]);

    const clearFilters = () => {
        setSearchParams({});
        setSearchTerm('');
        setSort('');
    };

    return (
        <div className="min-h-screen pb-20 pt-20">
            <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">

                {/* ── Header panel ── */}
                <section className="smoke-panel rounded-2xl p-6 sm:p-8 lg:p-10">
                    <div className="grid gap-8 lg:grid-cols-[1fr_auto] lg:items-end">
                        <div>
                            <span className="section-kicker">Catalogue</span>
                            <h1 className="mt-3 font-display text-[clamp(2.3rem,5vw,4.5rem)] font-bold leading-[0.96] tracking-[-0.04em] text-(--text)">
                                {activeCategory ? activeCategory.name : 'Tous nos produits.'}
                            </h1>
                            <p className="mt-4 max-w-2xl text-sm leading-7 text-zinc-400 sm:text-base">
                                Parcours l&apos;ensemble de notre catalogue. Filtre par catégorie ou recherche directement le produit qui t&apos;intéresse.
                            </p>
                            {activeCategory?.description && (
                                <p className="mt-3 max-w-2xl text-sm leading-6 text-zinc-500">
                                    {activeCategory.description}
                                </p>
                            )}
                        </div>

                        {/* Stats */}
                        <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
                            {[
                                { label: 'Produits', value: loading && allProducts.length === 0 ? '…' : allProducts.length },
                                { label: 'Catégories', value: categories.length || '…' },
                                { label: 'Filtre', value: 'Actif', small: true },
                            ].map((stat) => (
                                <div key={stat.label} className="rounded-xl border border-(--border) bg-(--bg-elevated) px-5 py-4">
                                    <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-zinc-500">{stat.label}</p>
                                    <p className={`mt-3 font-display font-bold tracking-[-0.04em] text-(--text) ${stat.small ? 'text-lg' : 'text-3xl'}`}>
                                        {stat.value}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* ── Search + sort + filter card ── */}
                    <div className="mt-8 grid gap-4 lg:grid-cols-[1fr_auto_auto] lg:items-center">
                        <div className="relative">
                            <FiSearch className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-500" />
                            <input
                                type="text"
                                value={searchTerm}
                                onChange={(event) => setSearchTerm(event.target.value)}
                                placeholder="Rechercher un produit, un univers, une idée..."
                                className="w-full rounded-xl border border-(--border) bg-(--surface) py-3.5 pl-12 pr-12 text-sm text-(--text) shadow-[0_4px_16px_rgba(0,0,0,0.20)] transition placeholder:text-zinc-600 focus:border-amber-400/40 focus:bg-(--surface-strong) focus:outline-none focus:ring-3 focus:ring-amber-400/08"
                            />
                            {searchTerm && (
                                <button
                                    type="button"
                                    onClick={() => setSearchTerm('')}
                                    aria-label="Effacer la recherche"
                                    className="absolute right-4 top-1/2 -translate-y-1/2 text-zinc-500 transition hover:text-(--text)"
                                >
                                    <FiX className="h-4 w-4" />
                                </button>
                            )}
                        </div>

                        <select
                            value={sort}
                            onChange={(e) => setSort(e.target.value)}
                            className="rounded-xl border border-(--border) bg-(--bg-elevated) px-4 py-3 text-sm text-zinc-300 focus:border-amber-400/40 focus:outline-none"
                        >
                            <option value="">Pertinence</option>
                            <option value="price_asc">Prix croissant</option>
                            <option value="price_desc">Prix décroissant</option>
                            <option value="name_asc">Nom A → Z</option>
                        </select>

                        <div className="rounded-xl border border-(--border) bg-(--bg-elevated) px-5 py-4">
                            <div className="flex items-center gap-3">
                                <span className="flex h-10 w-10 items-center justify-center rounded-xl border border-amber-400/20 bg-amber-400/08 text-amber-400">
                                    <FiSliders className="h-4 w-4" />
                                </span>
                                <div>
                                    <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-zinc-500">Filtres</p>
                                    <p className="mt-1 text-sm font-medium text-(--text)">Recherche active</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* ── Category filter strip ── */}
                {categories.length > 0 && (
                    <div className="sticky top-[5.3rem] z-30 mt-6">
                        <div className="scrollbar-hide flex items-center gap-2 overflow-x-auto rounded-2xl border border-(--border) bg-(--nav-gradient) px-2 py-2 shadow-(--shadow-md) backdrop-blur-xl">
                            <button
                                type="button"
                                onClick={clearFilters}
                                className={`pill-filter shrink-0 ${!activeCategoryId ? 'pill-filter-active' : 'pill-filter-inactive'}`}
                            >
                                <FiGrid className="h-3.5 w-3.5" />
                                Tous
                            </button>

                            {categories.map((category) => (
                                <button
                                    key={category.id}
                                    type="button"
                                    onClick={() => setSearchParams({ category_id: category.id })}
                                    className={`pill-filter shrink-0 ${activeCategoryId === category.id ? 'pill-filter-active' : 'pill-filter-inactive'}`}
                                >
                                    {category.name}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* ── Product grid ── */}
                <section className="mt-8">
                    {loading && allProducts.length === 0 && (
                        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                            {Array.from({ length: 8 }).map((_, index) => (
                                <div key={index} className="smoke-panel rounded-2xl p-3">
                                    <div className="aspect-[4/4.15] animate-pulse rounded-xl bg-(--surface)" />
                                    <div className="space-y-3 px-2 pb-2 pt-4">
                                        <div className="h-2.5 w-1/3 animate-pulse rounded-full bg-(--surface)" />
                                        <div className="h-4 animate-pulse rounded-full bg-(--surface)" />
                                        <div className="h-4 w-1/2 animate-pulse rounded-full bg-(--surface)" />
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {error && !loading && (
                        <div className="smoke-panel rounded-2xl border border-rose-400/20 px-6 py-14 text-center">
                            <p className="font-display text-3xl font-bold tracking-[-0.03em] text-(--text)">Impossible de charger le catalogue.</p>
                            <p className="mt-3 text-sm leading-6 text-zinc-400">{error}</p>
                            <button type="button" onClick={clearFilters} className="btn-outline mt-6 px-6 py-3 text-sm">
                                Réinitialiser les filtres
                            </button>
                        </div>
                    )}

                    {!loading && !error && allProducts.length === 0 && (
                        <div className="smoke-panel rounded-2xl px-6 py-20 text-center">
                            <p className="font-display text-3xl font-bold tracking-[-0.03em] text-(--text)">Aucun produit trouvé.</p>
                            <p className="mt-3 text-sm leading-6 text-zinc-400">
                                Essaie une autre recherche ou reviens à la grille complète pour retrouver la sélection.
                            </p>
                            <button type="button" onClick={clearFilters} className="btn-amber mt-6 px-6 py-3 text-sm">
                                Voir tout le catalogue
                            </button>
                        </div>
                    )}

                    {!error && sortedProducts.length > 0 && (
                        <>
                            <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
                                <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-zinc-500">
                                    {allProducts.length} produit{allProducts.length > 1 ? 's' : ''} affiché{allProducts.length > 1 ? 's' : ''}
                                </p>
                                {activeCategory && (
                                    <button type="button" onClick={clearFilters} className="button-secondary px-5 py-2.5 text-sm">
                                        Quitter {activeCategory.name}
                                    </button>
                                )}
                            </div>

                            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                                {sortedProducts.map((product) => (
                                    <ProductCard key={product.id} product={product} />
                                ))}
                            </div>
                        </>
                    )}

                    {/* ── Load more ── */}
                    {!loading && !error && hasMore && allProducts.length > 0 && (
                        <div className="mt-8 flex justify-center">
                            <button
                                type="button"
                                onClick={() => setPage((p) => p + 1)}
                                className="btn-ghost px-8 py-3 text-sm"
                            >
                                Charger plus
                                <FiArrowDown className="h-4 w-4" />
                            </button>
                        </div>
                    )}

                    {/* Subtle loading indicator when fetching additional pages */}
                    {loading && allProducts.length > 0 && (
                        <div className="mt-8 flex justify-center">
                            <div className="h-6 w-6 animate-spin rounded-full border-2 border-(--border) border-t-amber-400" />
                        </div>
                    )}
                </section>
            </div>
        </div>
    );
}

export default Products;
