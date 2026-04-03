import { startTransition, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    BarChart,
    Bar,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
} from 'recharts';
import {
    FiAlertCircle,
    FiArrowRight,
    FiBarChart2,
    FiBox,
    FiDownload,
    FiEdit2,
    FiGrid,
    FiImage,
    FiLayers,
    FiPackage,
    FiPlus,
    FiRefreshCcw,
    FiShield,
    FiTag,
    FiTrash2,
    FiTrendingUp,
    FiUserCheck,
    FiUsers,
    FiX,
} from 'react-icons/fi';
import useAuth from '../../hooks/useAuth';
import useTheme from '../../hooks/useTheme';
import { fetchProducts, fetchCategories, deleteProduct, createProduct, updateProduct, createCategory, updateCategory, deleteCategory } from '../../api/ProductApi';
import { getAllTransactionsAdmin } from '../../api/transactionApi';
import { getUsers } from '../../api/authApi';
import Loading from '../../components/Loading';
import { formatCurrency, formatDateTime } from '../../utils/format';

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

const ADMIN_TABS = [
    { id: 'overview', label: "Vue d'ensemble", icon: FiGrid },
    { id: 'products', label: 'Produits', icon: FiBox },
    { id: 'categories', label: 'Catégories', icon: FiTag },
    { id: 'users', label: 'Utilisateurs', icon: FiUsers },
    { id: 'transactions', label: 'Transactions', icon: FiBarChart2 },
];

const EMPTY_PRODUCT_FORM = {
    name: '',
    description: '',
    price: '',
    stock: '',
    category_id: '',
    image: null,
    remove_image: false,
};

function getProductFormState(product = null) {
    if (!product) return { ...EMPTY_PRODUCT_FORM };

    return {
        name: product.name ?? '',
        description: product.description ?? '',
        price: product.price != null ? String(product.price) : '',
        stock: product.stock != null ? String(product.stock) : '',
        category_id: product.category_id != null ? String(product.category_id) : '',
        image: null,
        remove_image: false,
    };
}

function buildProductFormData(form) {
    const payload = new FormData();
    payload.append('name', form.name.trim());
    payload.append('description', form.description.trim());
    payload.append('price', form.price);
    payload.append('stock', form.stock);
    payload.append('category_id', form.category_id);

    if (form.image instanceof File) {
        payload.append('image', form.image);
    }

    if (form.remove_image) {
        payload.append('remove_image', 'true');
    }

    return payload;
}

async function fetchUsersList(token) {
    const data = await getUsers(token, 1, 100);
    return data.data ?? [];
}

function LoadingPanel({ label = 'Chargement...' }) {
    return (
        <div className="surface-panel rounded-[2rem] px-6 py-16">
            <div className="flex flex-col items-center justify-center gap-4">
                <Loading size="lg" />
                <p className="text-sm font-medium text-white/54">{label}</p>
            </div>
        </div>
    );
}

function ErrorPanel({ message }) {
    return (
        <div className="surface-panel rounded-[2rem] border border-rose-500/14 px-6 py-8">
            <div className="flex items-start gap-4">
                <span className="flex h-12 w-12 items-center justify-center rounded-[1.2rem] bg-rose-500/12 text-rose-300">
                    <FiAlertCircle className="h-5 w-5" />
                </span>
                <div>
                    <p className="font-display text-2xl font-bold tracking-[-0.04em] text-white">Impossible de charger cette section</p>
                    <p className="mt-2 text-sm leading-6 text-white/56">{message}</p>
                </div>
            </div>
        </div>
    );
}

function EmptyPanel({ icon, title, text }) {
    const Icon = icon;

    return (
        <div className="surface-panel rounded-[2rem] px-6 py-14">
            <div className="mx-auto flex max-w-md flex-col items-center text-center">
                <span className="flex h-16 w-16 items-center justify-center rounded-[1.4rem] border border-white/10 bg-white/[0.08] text-amber-300">
                    <Icon className="h-6 w-6" />
                </span>
                <p className="mt-5 font-display text-3xl font-bold tracking-[-0.04em] text-white">{title}</p>
                <p className="mt-3 text-sm leading-6 text-white/56">{text}</p>
            </div>
        </div>
    );
}

function DashboardMetric({ icon, label, value, hint, accent = 'text-amber-300' }) {
    const Icon = icon;

    return (
        <div className="surface-panel card-lift rounded-[1.8rem] p-5">
            <div className="flex items-start justify-between gap-4">
                <div>
                    <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-white/42">{label}</p>
                    <p className={`mt-3 font-display text-4xl font-bold tracking-[-0.05em] ${accent}`}>{value}</p>
                    <p className="mt-2 text-sm text-white/56">{hint}</p>
                </div>
                <span className="flex h-12 w-12 items-center justify-center rounded-[1.3rem] border border-white/10 bg-white/[0.08] text-amber-300">
                    <Icon className="h-5 w-5" />
                </span>
            </div>
        </div>
    );
}

function TonePill({ tone = 'neutral', children }) {
    const map = {
        neutral: 'border border-white/10 bg-white/[0.06] text-white/70',
        success: 'border border-emerald-500/20 bg-emerald-500/12 text-emerald-300',
        warn: 'border border-amber-400/22 bg-amber-400/15 text-amber-300',
        danger: 'border border-rose-500/20 bg-rose-500/12 text-rose-300',
        info: 'border border-cyan-500/20 bg-cyan-500/12 text-cyan-300',
    };

    return (
        <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${map[tone] ?? map.neutral}`}>
            {children}
        </span>
    );
}

function ProductForm({ token, categories, product = null, onSaved, onCancel }) {
    const isEditing = Boolean(product);
    const [form, setForm] = useState(() => getProductFormState(product));
    const [error, setError] = useState(null);
    const [saving, setSaving] = useState(false);
    const [previewUrl, setPreviewUrl] = useState(product?.image_url ?? '');

    useEffect(() => {
        setForm(getProductFormState(product));
    }, [product]);

    useEffect(() => {
        if (form.image instanceof File) {
            const objectUrl = URL.createObjectURL(form.image);
            setPreviewUrl(objectUrl);
            return () => URL.revokeObjectURL(objectUrl);
        }

        setPreviewUrl(form.remove_image ? '' : (product?.image_url ?? ''));
        return undefined;
    }, [form.image, form.remove_image, product]);

    const handleChange = (event) => {
        const { name, value } = event.target;
        setForm((current) => ({ ...current, [name]: value }));
    };

    const handleImageChange = (event) => {
        const file = event.target.files?.[0] ?? null;
        setForm((current) => ({
            ...current,
            image: file,
            remove_image: file ? false : current.remove_image,
        }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setSaving(true);
        setError(null);

        const loadingToast = toast.loading(isEditing ? 'Mise à jour du produit...' : 'Création du produit...');

        try {
            const payload = buildProductFormData(form);
            const response = isEditing
                ? await updateProduct(product.id, payload, token)
                : await createProduct(payload, token);

            toast.success(isEditing ? 'Produit mis à jour' : 'Produit créé avec succès', { id: loadingToast });

            const savedProduct = response.data;
            if (isEditing) {
                onSaved?.(savedProduct);
            } else {
                setForm({ ...EMPTY_PRODUCT_FORM });
                onSaved?.(savedProduct);
            }
        } catch (err) {
            setError(err.message);
            toast.error(err.message, { id: loadingToast });
        } finally {
            setSaving(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="surface-panel rounded-[2rem] p-6">
            <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                <div>
                    <p className="section-kicker">Catalogue</p>
                    <h3 className="mt-3 font-display text-3xl font-bold tracking-[-0.05em] text-white">
                        {isEditing ? 'Modifier un produit.' : 'Ajouter un nouveau produit.'}
                    </h3>
                </div>
                <button type="button" onClick={onCancel} className="button-secondary rounded-full px-5 py-3 text-sm font-semibold">
                    Fermer
                </button>
            </div>

            {error && (
                <div className="mt-5 rounded-[1.4rem] border border-rose-500/14 bg-rose-500/[0.08] px-4 py-3 text-sm text-rose-300">
                    {error}
                </div>
            )}

            <div className="mt-6 grid gap-4 sm:grid-cols-2">
                <input
                    name="name"
                    value={form.name}
                    onChange={handleChange}
                    className="dashboard-input"
                    placeholder="Nom du produit"
                    required
                />

                <select
                    name="category_id"
                    value={form.category_id}
                    onChange={handleChange}
                    className="dashboard-select"
                    required
                >
                    <option value="" disabled>Choisir une catégorie</option>
                    {categories.map((category) => (
                        <option key={category.id} value={category.id}>
                            {category.name}
                        </option>
                    ))}
                </select>

                <input
                    name="price"
                    value={form.price}
                    onChange={handleChange}
                    className="dashboard-input"
                    placeholder="Prix en USD"
                    type="number"
                    min="0"
                    step="0.01"
                    required
                />

                <input
                    name="stock"
                    value={form.stock}
                    onChange={handleChange}
                    className="dashboard-input"
                    placeholder="Stock disponible"
                    type="number"
                    min="0"
                    required
                />

                <textarea
                    name="description"
                    value={form.description}
                    onChange={handleChange}
                    className="dashboard-textarea sm:col-span-2"
                    placeholder="Description produit"
                    rows={4}
                    required
                />

                <div className="sm:col-span-2">
                    <div className="rounded-[1.6rem] border border-white/10 bg-white/[0.05] p-4">
                        <div className="flex flex-col gap-4 lg:flex-row">
                            <div className="flex h-36 w-full items-center justify-center overflow-hidden rounded-[1.3rem] border border-white/10 bg-white/[0.04] lg:w-40">
                                {previewUrl ? (
                                    <img src={previewUrl} alt="Aperçu du produit" className="h-full w-full object-cover" />
                                ) : (
                                    <div className="flex flex-col items-center gap-2 text-white/42">
                                        <FiImage className="h-7 w-7" />
                                        <span className="text-xs font-semibold uppercase tracking-[0.18em]">Aperçu</span>
                                    </div>
                                )}
                            </div>

                            <div className="flex-1">
                                <p className="text-[10px] font-bold uppercase tracking-[0.22em] text-white/42">Image produit</p>
                                <p className="mt-2 text-sm leading-6 text-white/56">
                                    Formats acceptés: JPG, PNG ou WebP. Une nouvelle image remplace automatiquement l'ancienne.
                                </p>

                                <label className="button-secondary mt-4 inline-flex cursor-pointer rounded-full px-5 py-3 text-sm font-semibold">
                                    <FiImage className="h-4 w-4" />
                                    {form.image ? "Changer l'image" : 'Choisir une image'}
                                    <input
                                        type="file"
                                        accept="image/png,image/jpeg,image/webp"
                                        className="sr-only"
                                        onChange={handleImageChange}
                                    />
                                </label>

                                {(form.image || product?.image_url) && (
                                    <div className="mt-4 flex flex-wrap gap-3">
                                        {product?.image_url && !form.image && !form.remove_image && (
                                            <button
                                                type="button"
                                                onClick={() => setForm((current) => ({ ...current, remove_image: true, image: null }))}
                                                className="danger-button inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold"
                                            >
                                                <FiX className="h-4 w-4" />
                                                Supprimer l'image actuelle
                                            </button>
                                        )}

                                        {form.remove_image && (
                                            <button
                                                type="button"
                                                onClick={() => setForm((current) => ({ ...current, remove_image: false }))}
                                                className="inline-flex items-center gap-2 rounded-full border border-white/10 px-4 py-2 text-sm font-semibold text-white/56 transition hover:bg-white/10 hover:text-white"
                                            >
                                                Annuler la suppression
                                            </button>
                                        )}

                                        {form.image && (
                                            <button
                                                type="button"
                                                onClick={() => setForm((current) => ({ ...current, image: null }))}
                                                className="inline-flex items-center gap-2 rounded-full border border-white/10 px-4 py-2 text-sm font-semibold text-white/56 transition hover:bg-white/10 hover:text-white"
                                            >
                                                Retirer le nouveau fichier
                                            </button>
                                        )}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="mt-6 flex flex-col gap-3 sm:flex-row">
                <button type="submit" disabled={saving} className="button-primary rounded-full px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-55">
                    {saving ? 'Enregistrement...' : isEditing ? 'Enregistrer les modifications' : 'Créer le produit'}
                </button>
                <button type="button" onClick={onCancel} className="button-secondary rounded-full px-6 py-3.5 text-sm font-semibold">
                    Annuler
                </button>
            </div>
        </form>
    );
}

function StockAdjust({ product, token, onUpdated }) {
    const [delta, setDelta] = useState('');
    const [saving, setSaving] = useState(false);

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (delta === '') return;

        setSaving(true);
        const loadingToast = toast.loading('Ajustement du stock...');

        try {
            const response = await fetch(`${BASE_URL}/products/${product.id}/stock`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({ delta: Number.parseInt(delta, 10) }),
            });

            const data = await response.json();
            if (!response.ok) throw new Error(data.message || "Erreur lors de l'ajustement.");

            onUpdated(product.id, data.data.new_stock);
            setDelta('');
            toast.success('Stock mis à jour', { id: loadingToast });
        } catch (err) {
            toast.error(err.message, { id: loadingToast });
        } finally {
            setSaving(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="flex min-w-[9rem] items-center gap-2" onClick={(event) => event.stopPropagation()}>
            <input
                type="number"
                value={delta}
                onChange={(event) => setDelta(event.target.value)}
                className="dashboard-input min-h-11 px-4 py-2 text-sm"
                placeholder="ex: +3 / -2"
            />
            <button type="submit" disabled={saving || delta === ''} className="button-secondary min-w-16 rounded-full px-4 py-2.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-55">
                OK
            </button>
        </form>
    );
}

/* ─────────────── Chart palette & helpers ─────────────── */
const PIE_COLORS = ['#f59e0b', '#10b981', '#22d3ee', '#8b5cf6', '#f97316', '#f43f5e', '#0ea5e9', '#a78bfa'];

function useChartColors() {
    const { theme } = useTheme();
    const dark = theme === 'dark';
    return {
        tick:   dark ? 'rgba(255,255,255,0.4)'  : 'rgba(9,9,11,0.5)',
        grid:   dark ? 'rgba(255,255,255,0.06)' : 'rgba(9,9,11,0.08)',
        legend: dark ? 'rgba(255,255,255,0.65)' : 'rgba(9,9,11,0.65)',
        tooltip: dark ? '#1c1c1c' : '#ffffff',
        tooltipBorder: dark ? 'rgba(255,255,255,0.10)' : 'rgba(9,9,11,0.10)',
        tooltipText: dark ? undefined : '#09090b',
    };
}

function ChartTooltipContent({ active, payload, label, formatVal }) {
    const c = useChartColors();
    if (!active || !payload?.length) return null;
    return (
        <div style={{ background: c.tooltip, border: `1px solid ${c.tooltipBorder}`, color: c.tooltipText }} className="rounded-[1rem] px-4 py-3 shadow-xl">
            {label && (
                <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.18em]" style={{ opacity: 0.5 }}>{label}</p>
            )}
            {payload.map((entry, i) => (
                <p key={i} className="text-sm font-semibold" style={{ color: entry.color ?? entry.fill }}>
                    {entry.name}: {formatVal ? formatVal(entry.value) : entry.value}
                </p>
            ))}
        </div>
    );
}

function RevenueAreaChart({ transactions }) {
    const data = useMemo(() => {
        const map = {};
        transactions.forEach((tx) => {
            if (!tx.created_at) return;
            const d = new Date(tx.created_at);
            const key = d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
            if (!map[key]) map[key] = { date: key, revenu: 0, nb: 0, ts: d.getTime() };
            map[key].revenu += Number(tx.amount ?? 0);
            map[key].nb += 1;
        });
        return Object.values(map).sort((a, b) => a.ts - b.ts);
    }, [transactions]);

    if (data.length === 0) {
        return (
            <div className="flex h-52 items-center justify-center text-sm text-white/35">
                Pas encore de données de transactions.
            </div>
        );
    }

    const c = useChartColors();
    return (
        <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={data} margin={{ top: 8, right: 8, left: -10, bottom: 0 }}>
                <defs>
                    <linearGradient id="gradRevenu" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.28} />
                        <stop offset="95%" stopColor="#f59e0b" stopOpacity={0} />
                    </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={c.grid} vertical={false} />
                <XAxis dataKey="date" tick={{ fill: c.tick, fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: c.tick, fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v}`} />
                <Tooltip content={<ChartTooltipContent formatVal={(v) => formatCurrency(v)} />} />
                <Area type="monotone" dataKey="revenu" name="Revenus" stroke="#f59e0b" strokeWidth={2.5} fill="url(#gradRevenu)" dot={false} activeDot={{ r: 5, fill: '#f59e0b', stroke: c.tooltip, strokeWidth: 2 }} />
            </AreaChart>
        </ResponsiveContainer>
    );
}

function CategoryDonutChart({ products }) {
    const data = useMemo(() => {
        const map = {};
        products.forEach((p) => {
            const cat = p.category_name ?? 'Autre';
            map[cat] = (map[cat] ?? 0) + 1;
        });
        return Object.entries(map).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value);
    }, [products]);

    if (data.length === 0) {
        return <div className="flex h-52 items-center justify-center text-sm text-white/35">Pas encore de produits.</div>;
    }

    const c = useChartColors();
    return (
        <ResponsiveContainer width="100%" height={220}>
            <PieChart>
                <Pie data={data} cx="50%" cy="45%" innerRadius={52} outerRadius={82} paddingAngle={3} dataKey="value" stroke="none">
                    {data.map((_, i) => (
                        <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                </Pie>
                <Tooltip content={<ChartTooltipContent />} />
                <Legend formatter={(value) => <span style={{ color: c.legend, fontSize: 12 }}>{value}</span>} iconType="circle" iconSize={8} />
            </PieChart>
        </ResponsiveContainer>
    );
}

function TxStatusBarChart({ transactions }) {
    const data = useMemo(() => [
        { status: 'Complétées', count: transactions.filter((tx) => tx.status === 'completed').length, fill: '#10b981' },
        { status: 'En attente', count: transactions.filter((tx) => tx.status === 'pending').length, fill: '#f59e0b' },
        { status: 'Annulées', count: transactions.filter((tx) => tx.status === 'cancelled').length, fill: '#f43f5e' },
    ], [transactions]);

    const total = data.reduce((s, d) => s + d.count, 0);

    if (total === 0) {
        return <div className="flex h-52 items-center justify-center text-sm text-white/35">Pas encore de transactions.</div>;
    }

    const c = useChartColors();
    return (
        <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data} margin={{ top: 8, right: 8, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={c.grid} vertical={false} />
                <XAxis dataKey="status" tick={{ fill: c.tick, fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: c.tick, fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
                <Tooltip content={<ChartTooltipContent />} />
                <Bar dataKey="count" name="Transactions" radius={[6, 6, 0, 0]}>
                    {data.map((entry, i) => (
                        <Cell key={i} fill={entry.fill} fillOpacity={0.85} />
                    ))}
                </Bar>
            </BarChart>
        </ResponsiveContainer>
    );
}

function StockBarChart({ products }) {
    const data = useMemo(() =>
        [...products]
            .sort((a, b) => Number(a.stock ?? 0) - Number(b.stock ?? 0))
            .slice(0, 8)
            .map((p) => ({
                name: p.name.length > 14 ? p.name.slice(0, 13) + '…' : p.name,
                stock: Number(p.stock ?? 0),
                fill: Number(p.stock ?? 0) === 0 ? '#f43f5e' : Number(p.stock ?? 0) <= 5 ? '#f59e0b' : '#10b981',
            })),
    [products]);

    if (data.length === 0) {
        return <div className="flex h-52 items-center justify-center text-sm text-white/35">Pas encore de produits.</div>;
    }

    const c = useChartColors();
    return (
        <ResponsiveContainer width="100%" height={220}>
            <BarChart data={data} layout="vertical" margin={{ top: 4, right: 12, left: 4, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={c.grid} horizontal={false} />
                <XAxis type="number" tick={{ fill: c.tick, fontSize: 11 }} axisLine={false} tickLine={false} allowDecimals={false} />
                <YAxis type="category" dataKey="name" tick={{ fill: c.legend, fontSize: 11 }} axisLine={false} tickLine={false} width={90} />
                <Tooltip content={<ChartTooltipContent />} />
                <Bar dataKey="stock" name="Stock" radius={[0, 6, 6, 0]}>
                    {data.map((entry, i) => (
                        <Cell key={i} fill={entry.fill} fillOpacity={0.85} />
                    ))}
                </Bar>
            </BarChart>
        </ResponsiveContainer>
    );
}

/* ─────────────── OverviewTab ─────────────── */
function OverviewTab({ products, transactions, users }) {
    const totalRevenue = useMemo(
        () => transactions.filter((tx) => tx.status === 'completed').reduce((sum, tx) => sum + Number(tx.amount ?? 0), 0),
        [transactions],
    );
    const lowStockProducts = useMemo(() => products.filter((p) => Number(p.stock ?? 0) <= 5), [products]);
    const activeUsers = useMemo(() => users.filter((u) => !u.is_deleted).length, [users]);
    const confirmedUsers = useMemo(() => users.filter((u) => u.email_confirmed).length, [users]);

    return (
        <div className="space-y-6">
            {/* ── KPI cards ── */}
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                <DashboardMetric icon={FiBox} label="Produits actifs" value={products.length} hint="Catalogue visible dans la boutique." accent="text-white" />
                <DashboardMetric icon={FiTrendingUp} label="Revenus (complétés)" value={formatCurrency(totalRevenue)} hint="Transactions avec statut complété." accent="text-emerald-300" />
                <DashboardMetric icon={FiBarChart2} label="Transactions" value={transactions.length} hint="Total chargé depuis l'API." accent="text-amber-300" />
                <DashboardMetric icon={FiUsers} label="Utilisateurs actifs" value={activeUsers} hint="Comptes non supprimés." accent="text-cyan-300" />
            </div>

            {/* ── Graphes ligne 1 : Revenus + Répartition catégories ── */}
            <div className="grid gap-6 lg:grid-cols-2">
                <section className="surface-panel rounded-[2rem] p-6">
                    <p className="section-kicker">Analyse financière</p>
                    <h3 className="mt-2 font-display text-2xl font-bold tracking-[-0.04em] text-white">Revenus par jour.</h3>
                    <p className="mt-1 text-xs text-white/45">Cumul des paiements par date de transaction.</p>
                    <div className="mt-5">
                        <RevenueAreaChart transactions={transactions} />
                    </div>
                </section>

                <section className="surface-panel rounded-[2rem] p-6">
                    <p className="section-kicker">Catalogue</p>
                    <h3 className="mt-2 font-display text-2xl font-bold tracking-[-0.04em] text-white">Produits par catégorie.</h3>
                    <p className="mt-1 text-xs text-white/45">Répartition du catalogue par univers.</p>
                    <div className="mt-5">
                        <CategoryDonutChart products={products} />
                    </div>
                </section>
            </div>

            {/* ── Graphes ligne 2 : Statuts transactions + Stock critique ── */}
            <div className="grid gap-6 lg:grid-cols-2">
                <section className="surface-panel rounded-[2rem] p-6">
                    <p className="section-kicker">Transactions</p>
                    <h3 className="mt-2 font-display text-2xl font-bold tracking-[-0.04em] text-white">Répartition par statut.</h3>
                    <p className="mt-1 text-xs text-white/45">Complétées, en attente et annulées.</p>
                    <div className="mt-5">
                        <TxStatusBarChart transactions={transactions} />
                    </div>
                </section>

                <section className="surface-panel rounded-[2rem] p-6">
                    <p className="section-kicker">Gestion stock</p>
                    <h3 className="mt-2 font-display text-2xl font-bold tracking-[-0.04em] text-white">Stock par produit.</h3>
                    <p className="mt-1 text-xs text-white/45">Les 8 produits avec le stock le plus bas.</p>
                    <div className="mt-5">
                        <StockBarChart products={products} />
                    </div>
                </section>
            </div>

            {/* ── Alertes stock + santé back-office ── */}
            <div className="grid gap-6 lg:grid-cols-[1.08fr_0.92fr]">
                <section className="surface-panel rounded-[2rem] p-6">
                    <div className="flex items-center justify-between gap-4">
                        <div>
                            <p className="section-kicker">Surveillance stock</p>
                            <h3 className="mt-3 font-display text-2xl font-bold tracking-[-0.04em] text-white">Produits à surveiller.</h3>
                        </div>
                        <TonePill tone={lowStockProducts.length > 0 ? 'warn' : 'success'}>
                            {lowStockProducts.length > 0 ? `${lowStockProducts.length} à réappro` : 'Tout va bien'}
                        </TonePill>
                    </div>

                    {lowStockProducts.length === 0 ? (
                        <div className="mt-6 rounded-[1.7rem] border border-emerald-500/[0.12] bg-emerald-500/[0.08] px-5 py-5 text-sm text-emerald-300">
                            Aucun produit en zone de stock bas.
                        </div>
                    ) : (
                        <div className="mt-6 grid gap-3">
                            {lowStockProducts.slice(0, 5).map((product) => (
                                <div key={product.id} className="rounded-[1.6rem] border border-white/10 bg-white/[0.06] px-5 py-4">
                                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                                        <div>
                                            <p className="text-xs uppercase tracking-[0.2em] text-white/40">Produit #{product.id}</p>
                                            <p className="mt-1.5 text-sm font-semibold text-white">{product.name}</p>
                                        </div>
                                        <TonePill tone={Number(product.stock ?? 0) === 0 ? 'danger' : 'warn'}>
                                            {product.stock} en stock
                                        </TonePill>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </section>

                <section className="surface-panel-dark rounded-[2rem] p-6 text-white">
                    <p className="section-kicker text-white/60">Santé du back-office</p>
                    <h3 className="mt-3 font-display text-2xl font-bold tracking-[-0.04em]">Indicateurs rapides.</h3>

                    <div className="mt-6 grid gap-4">
                        <div className="rounded-[1.6rem] border border-white/10 bg-white/[0.08] p-5">
                            <p className="text-[11px] uppercase tracking-[0.2em] text-white/45">Catégories</p>
                            <p className="mt-3 font-display text-4xl font-bold tracking-[-0.05em]">{new Set(products.map((p) => p.category_name)).size}</p>
                            <p className="mt-2 text-sm text-white/60">Univers dans le catalogue.</p>
                        </div>
                        <div className="rounded-[1.6rem] border border-white/10 bg-white/[0.08] p-5">
                            <p className="text-[11px] uppercase tracking-[0.2em] text-white/45">Emails confirmés</p>
                            <p className="mt-3 font-display text-4xl font-bold tracking-[-0.05em]">{confirmedUsers}</p>
                            <p className="mt-2 text-sm text-white/60">Comptes validés et prêts à convertir.</p>
                        </div>
                        <div className="rounded-[1.6rem] border border-white/10 bg-white/[0.08] p-5">
                            <p className="text-[11px] uppercase tracking-[0.2em] text-white/45">Transactions chargées</p>
                            <p className="mt-3 font-display text-4xl font-bold tracking-[-0.05em]">{transactions.length}</p>
                            <p className="mt-2 text-sm text-white/60">Remontées par l&apos;API transactions.</p>
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
}

function ProductsTab({ products, categories, token, loading, onRefresh, setProducts }) {
    const [showForm, setShowForm] = useState(false);
    const [editingProduct, setEditingProduct] = useState(null);
    const [deletingId, setDeletingId] = useState(null);

    const handleDelete = async (id) => {
        if (!window.confirm('Supprimer ce produit ?')) return;

        setDeletingId(id);
        const loadingToast = toast.loading('Suppression du produit...');

        try {
            await deleteProduct(id, token);
            setProducts((current) => current.filter((product) => product.id !== id));
            toast.success('Produit supprimé', { id: loadingToast });
        } catch (err) {
            toast.error(err.message, { id: loadingToast });
        } finally {
            setDeletingId(null);
        }
    };

    const handleStockUpdate = (productId, newStock) => {
        setProducts((current) => current.map((product) => (
            product.id === productId ? { ...product, stock: newStock } : product
        )));
    };

    const handleProductSaved = (savedProduct) => {
        setProducts((current) => {
            const exists = current.some((product) => product.id === savedProduct.id);
            if (exists) {
                return current.map((product) => (product.id === savedProduct.id ? savedProduct : product));
            }
            return [savedProduct, ...current];
        });
        setEditingProduct(null);
        setShowForm(false);
    };

    const closeForms = () => {
        setShowForm(false);
        setEditingProduct(null);
    };

    if (loading) return <LoadingPanel label="Chargement du catalogue..." />;

    return (
        <div className="space-y-6">
            <div className="surface-panel rounded-[2rem] p-6">
                <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
                    <div>
                        <p className="section-kicker">Gestion produits</p>
                        <h2 className="mt-3 font-display text-3xl font-bold tracking-[-0.05em] text-white">Un back-office plus propre pour piloter le catalogue.</h2>
                        <p className="mt-3 max-w-2xl text-sm leading-6 text-white/56">
                            Gérez les fiches produit, les images et le stock depuis une interface compacte, claire et plus agréable à utiliser au quotidien.
                        </p>
                    </div>

                    <div className="flex flex-col gap-3 sm:flex-row">
                        <button type="button" onClick={onRefresh} className="button-secondary inline-flex items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-semibold">
                            <FiRefreshCcw className="h-4 w-4" />
                            Actualiser
                        </button>
                        <button
                            type="button"
                            onClick={() => {
                                setEditingProduct(null);
                                setShowForm((value) => !value);
                            }}
                            className="button-primary inline-flex items-center justify-center gap-2 rounded-full px-5 py-3 text-sm font-semibold"
                        >
                            <FiPlus className="h-4 w-4" />
                            {showForm ? 'Fermer le formulaire' : 'Nouveau produit'}
                        </button>
                    </div>
                </div>
            </div>

            {showForm && (
                <ProductForm
                    token={token}
                    categories={categories}
                    onSaved={handleProductSaved}
                    onCancel={closeForms}
                />
            )}

            {editingProduct && (
                <ProductForm
                    token={token}
                    categories={categories}
                    product={editingProduct}
                    onSaved={handleProductSaved}
                    onCancel={closeForms}
                />
            )}

            {products.length === 0 ? (
                <EmptyPanel icon={FiBox} title="Aucun produit disponible." text="Ajoutez vos premiers articles pour remplir le catalogue administrateur." />
            ) : (
                <div className="dashboard-table-wrap">
                    <table className="dashboard-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Image</th>
                                <th>Produit</th>
                                <th>Prix</th>
                                <th>Stock</th>
                                <th>Ajustement</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {products.map((product) => (
                                <tr key={product.id}>
                                    <td>#{product.id}</td>
                                    <td>
                                        <div className="flex h-16 w-16 items-center justify-center overflow-hidden rounded-[1rem] border border-white/10 bg-white/[0.04]">
                                            {product.image_url ? (
                                                <img
                                                    src={product.image_url}
                                                    alt={product.name}
                                                    className="h-full w-full object-cover"
                                                    loading="lazy"
                                                />
                                            ) : (
                                                <FiImage className="h-5 w-5 text-white/40" />
                                            )}
                                        </div>
                                    </td>
                                    <td>
                                        <div className="min-w-[14rem]">
                                            <p className="font-semibold text-white">{product.name}</p>
                                            <p className="mt-1 text-sm text-white/56">{product.category_name ?? 'Catalogue'}</p>
                                        </div>
                                    </td>
                                    <td className="font-semibold text-white">{formatCurrency(product.price)}</td>
                                    <td>
                                        <TonePill tone={Number(product.stock ?? 0) <= 5 ? 'warn' : 'success'}>
                                            {product.stock}
                                        </TonePill>
                                    </td>
                                    <td>
                                        <StockAdjust product={product} token={token} onUpdated={handleStockUpdate} />
                                    </td>
                                    <td>
                                        <div className="flex flex-col gap-2 sm:flex-row">
                                            <button
                                                type="button"
                                                onClick={() => {
                                                    setShowForm(false);
                                                    setEditingProduct(product);
                                                }}
                                                className="inline-flex items-center gap-2 rounded-full border border-white/10 px-4 py-2 text-sm font-semibold text-white/56 transition hover:bg-white/10 hover:text-white"
                                            >
                                                <FiEdit2 className="h-4 w-4" />
                                                Modifier
                                            </button>
                                            <button
                                                type="button"
                                                onClick={() => handleDelete(product.id)}
                                                disabled={deletingId === product.id}
                                                className="danger-button inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-55"
                                            >
                                                <FiTrash2 className="h-4 w-4" />
                                                {deletingId === product.id ? 'Suppression...' : 'Supprimer'}
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

function UsersTab({ users, loading, error }) {
    if (loading) return <LoadingPanel label="Chargement des utilisateurs..." />;
    if (error) return <ErrorPanel message={error} />;

    if (users.length === 0) {
        return <EmptyPanel icon={FiUsers} title="Aucun utilisateur trouvé." text="Les comptes apparaîtront ici dès qu'ils seront disponibles via l'API." />;
    }

    const activeUsers = users.filter((user) => !user.is_deleted).length;
    const adminUsers = users.filter((user) => user.is_admin).length;
    const confirmedUsers = users.filter((user) => user.email_confirmed).length;

    return (
        <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-3">
                <DashboardMetric
                    icon={FiUsers}
                    label="Utilisateurs"
                    value={users.length}
                    hint="Comptes remontés par l'API d'administration."
                    accent="text-white"
                />
                <DashboardMetric
                    icon={FiUserCheck}
                    label="Confirmés"
                    value={confirmedUsers}
                    hint="Emails déjà vérifiés."
                    accent="text-emerald-300"
                />
                <DashboardMetric
                    icon={FiShield}
                    label="Admins"
                    value={adminUsers}
                    hint="Comptes disposant d'un accès administrateur."
                    accent="text-cyan-300"
                />
            </div>

            <div className="surface-panel rounded-[2rem] p-6">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                    <div>
                        <p className="section-kicker">Gestion utilisateurs</p>
                        <h2 className="mt-3 font-display text-3xl font-bold tracking-[-0.05em] text-white">Une lecture plus claire des comptes.</h2>
                    </div>
                    <TonePill tone="info">{activeUsers} comptes actifs</TonePill>
                </div>
            </div>

            <div className="dashboard-table-wrap">
                <table className="dashboard-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Identité</th>
                            <th>Email</th>
                            <th>Rôle</th>
                            <th>Vérification</th>
                            <th>Statut</th>
                            <th>Inscrit le</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map((user) => (
                            <tr key={user.id} className={user.is_deleted ? 'opacity-55' : ''}>
                                <td>#{user.id}</td>
                                <td>
                                    <div className="min-w-[12rem]">
                                        <p className="font-semibold text-white">{user.username || user.userName || '—'}</p>
                                        <p className="mt-1 text-sm text-white/56">{user.prenom || user.nom ? `${user.prenom ?? ''} ${user.nom ?? ''}`.trim() : 'Profil standard'}</p>
                                    </div>
                                </td>
                                <td>{user.email}</td>
                                <td>
                                    {user.is_admin ? <TonePill tone="info">Admin</TonePill> : <TonePill tone="neutral">Client</TonePill>}
                                </td>
                                <td>
                                    {user.email_confirmed ? <TonePill tone="success">Confirmé</TonePill> : <TonePill tone="warn">En attente</TonePill>}
                                </td>
                                <td>
                                    {user.is_deleted ? <TonePill tone="danger">Supprimé</TonePill> : <TonePill tone="success">Actif</TonePill>}
                                </td>
                                <td className="whitespace-nowrap">{formatDateTime(user.created_at)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function CategoriesTab({ categories, token, setCategories }) {
    const [form, setForm] = useState({ name: '', description: '' });
    const [editingId, setEditingId] = useState(null);
    const [editForm, setEditForm] = useState({ name: '', description: '' });
    const [saving, setSaving] = useState(false);
    const [deletingId, setDeletingId] = useState(null);

    const handleCreate = async (event) => {
        event.preventDefault();
        setSaving(true);
        const t = toast.loading('Création de la catégorie...');
        try {
            const res = await createCategory(form, token);
            setCategories((prev) => [...prev, res.data]);
            setForm({ name: '', description: '' });
            toast.success('Catégorie créée', { id: t });
        } catch (err) {
            toast.error(err.message, { id: t });
        } finally {
            setSaving(false);
        }
    };

    const handleEdit = (category) => {
        setEditingId(category.id);
        setEditForm({ name: category.name, description: category.description ?? '' });
    };

    const handleUpdate = async (event) => {
        event.preventDefault();
        setSaving(true);
        const t = toast.loading('Mise à jour...');
        try {
            const res = await updateCategory(editingId, editForm, token);
            setCategories((prev) => prev.map((c) => (c.id === editingId ? res.data : c)));
            setEditingId(null);
            toast.success('Catégorie mise à jour', { id: t });
        } catch (err) {
            toast.error(err.message, { id: t });
        } finally {
            setSaving(false);
        }
    };

    const handleDelete = async (id) => {
        if (!window.confirm('Supprimer cette catégorie ?')) return;
        setDeletingId(id);
        const t = toast.loading('Suppression...');
        try {
            await deleteCategory(id, token);
            setCategories((prev) => prev.filter((c) => c.id !== id));
            toast.success('Catégorie supprimée', { id: t });
        } catch (err) {
            toast.error(err.message, { id: t });
        } finally {
            setDeletingId(null);
        }
    };

    return (
        <div className="space-y-6">
            {/* ── Formulaire création ── */}
            <form onSubmit={handleCreate} className="surface-panel rounded-[2rem] p-6">
                <p className="section-kicker">Catégories</p>
                <h2 className="mt-3 font-display text-3xl font-bold tracking-[-0.05em] text-white">Ajouter une catégorie.</h2>
                <div className="mt-6 grid gap-4 sm:grid-cols-2">
                    <input
                        value={form.name}
                        onChange={(e) => setForm((p) => ({ ...p, name: e.target.value }))}
                        className="dashboard-input"
                        placeholder="Nom de la catégorie"
                        required
                    />
                    <input
                        value={form.description}
                        onChange={(e) => setForm((p) => ({ ...p, description: e.target.value }))}
                        className="dashboard-input"
                        placeholder="Description (optionnel)"
                    />
                </div>
                <button type="submit" disabled={saving} className="button-primary mt-4 inline-flex items-center gap-2 rounded-full px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-55">
                    <FiPlus className="h-4 w-4" />
                    {saving ? 'Création...' : 'Créer'}
                </button>
            </form>

            {/* ── Liste ── */}
            {categories.length === 0 ? (
                <EmptyPanel icon={FiTag} title="Aucune catégorie." text="Ajoutez votre première catégorie via le formulaire ci-dessus." />
            ) : (
                <div className="dashboard-table-wrap">
                    <table className="dashboard-table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Nom</th>
                                <th>Description</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {categories.map((cat) => (
                                <tr key={cat.id}>
                                    <td>#{cat.id}</td>
                                    <td>
                                        {editingId === cat.id ? (
                                            <input
                                                value={editForm.name}
                                                onChange={(e) => setEditForm((p) => ({ ...p, name: e.target.value }))}
                                                className="dashboard-input min-w-[10rem] text-sm"
                                            />
                                        ) : (
                                            <span className="font-semibold text-white">{cat.name}</span>
                                        )}
                                    </td>
                                    <td>
                                        {editingId === cat.id ? (
                                            <input
                                                value={editForm.description}
                                                onChange={(e) => setEditForm((p) => ({ ...p, description: e.target.value }))}
                                                className="dashboard-input min-w-[12rem] text-sm"
                                                placeholder="Description"
                                            />
                                        ) : (
                                            <span className="text-white/56">{cat.description || '—'}</span>
                                        )}
                                    </td>
                                    <td>
                                        {editingId === cat.id ? (
                                            <div className="flex gap-2">
                                                <button type="button" onClick={handleUpdate} disabled={saving} className="button-primary rounded-full px-4 py-2 text-sm font-semibold disabled:opacity-55">
                                                    {saving ? '...' : 'Enregistrer'}
                                                </button>
                                                <button type="button" onClick={() => setEditingId(null)} className="button-secondary rounded-full px-4 py-2 text-sm font-semibold">
                                                    Annuler
                                                </button>
                                            </div>
                                        ) : (
                                            <div className="flex gap-2">
                                                <button type="button" onClick={() => handleEdit(cat)} className="inline-flex items-center gap-1.5 rounded-full border border-white/10 px-4 py-2 text-sm font-semibold text-white/56 transition hover:bg-white/10 hover:text-white">
                                                    <FiEdit2 className="h-3.5 w-3.5" />
                                                    Modifier
                                                </button>
                                                <button type="button" onClick={() => handleDelete(cat.id)} disabled={deletingId === cat.id} className="danger-button inline-flex items-center gap-1.5 rounded-full px-4 py-2 text-sm font-semibold disabled:opacity-55">
                                                    <FiTrash2 className="h-3.5 w-3.5" />
                                                    {deletingId === cat.id ? '...' : 'Supprimer'}
                                                </button>
                                            </div>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

const TX_STATUS = {
    completed: { label: 'Complétée', tone: 'success' },
    pending:   { label: 'En attente', tone: 'warn' },
    cancelled: { label: 'Annulée', tone: 'danger' },
};

function exportTransactionsCSV(transactions) {
    const header = ['Référence', 'Date', 'Utilisateur', 'Email', 'Montant', 'Méthode', 'Statut'];
    const rows = transactions.map((tx) => [
        tx.ref_externe ?? '',
        tx.created_at ? new Date(tx.created_at).toLocaleString('fr-FR') : '',
        tx.user?.username ?? '',
        tx.user?.email ?? '',
        Number(tx.amount ?? 0).toFixed(2),
        tx.payment_method ?? '',
        tx.status ?? '',
    ]);
    const csv = [header, ...rows].map((row) => row.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transactions_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

function TransactionsTab({ transactions, loading }) {
    if (loading) return <LoadingPanel label="Chargement des transactions..." />;

    if (transactions.length === 0) {
        return <EmptyPanel icon={FiBarChart2} title="Aucune transaction à afficher." text="Les transactions apparaîtront ici dès qu'elles seront disponibles." />;
    }

    const totalRevenue = transactions.reduce((sum, tx) => sum + Number(tx.amount ?? 0), 0);
    const completed = transactions.filter((tx) => tx.status === 'completed').length;

    return (
        <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-3">
                <DashboardMetric
                    icon={FiBarChart2}
                    label="Transactions"
                    value={transactions.length}
                    hint="Total sur la page courante."
                    accent="text-white"
                />
                <DashboardMetric
                    icon={FiLayers}
                    label="Complétées"
                    value={completed}
                    hint="Paiements validés."
                    accent="text-emerald-300"
                />
                <DashboardMetric
                    icon={FiTrendingUp}
                    label="Revenus"
                    value={formatCurrency(totalRevenue)}
                    hint="Cumul des transactions complétées."
                    accent="text-amber-300"
                />
            </div>

            {/* ── Graphes transactions ── */}
            <div className="grid gap-6 lg:grid-cols-2">
                <section className="surface-panel rounded-[2rem] p-6">
                    <p className="section-kicker">Évolution</p>
                    <h3 className="mt-2 font-display text-2xl font-bold tracking-[-0.04em] text-white">Revenus dans le temps.</h3>
                    <div className="mt-5">
                        <RevenueAreaChart transactions={transactions} />
                    </div>
                </section>
                <section className="surface-panel rounded-[2rem] p-6">
                    <p className="section-kicker">Répartition</p>
                    <h3 className="mt-2 font-display text-2xl font-bold tracking-[-0.04em] text-white">Statuts des transactions.</h3>
                    <div className="mt-5">
                        <TxStatusBarChart transactions={transactions} />
                    </div>
                </section>
            </div>

            <div className="surface-panel rounded-[2rem] p-5">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div>
                        <p className="section-kicker">Historique</p>
                        <h2 className="mt-2 font-display text-2xl font-bold tracking-[-0.04em] text-white">{transactions.length} transaction{transactions.length > 1 ? 's' : ''} chargée{transactions.length > 1 ? 's' : ''}.</h2>
                    </div>
                    <button
                        type="button"
                        onClick={() => exportTransactionsCSV(transactions)}
                        className="button-secondary inline-flex items-center gap-2 rounded-full px-5 py-3 text-sm font-semibold"
                    >
                        <FiDownload className="h-4 w-4" />
                        Exporter CSV
                    </button>
                </div>
            </div>

            <div className="dashboard-table-wrap">
                <table className="dashboard-table">
                    <thead>
                        <tr>
                            <th>Référence</th>
                            <th>Date &amp; heure</th>
                            <th>Utilisateur</th>
                            <th>Produits achetés</th>
                            <th>Montant</th>
                            <th>Méthode</th>
                            <th>Statut</th>
                        </tr>
                    </thead>
                    <tbody>
                        {transactions.map((tx) => (
                            <tr key={tx.id}>
                                <td>
                                    <span className="font-mono text-xs text-white/56">{tx.ref_externe}</span>
                                </td>
                                <td className="whitespace-nowrap">{formatDateTime(tx.created_at)}</td>
                                <td>
                                    <div>
                                        <p className="font-semibold text-white">{tx.user?.username ?? '—'}</p>
                                        <p className="mt-0.5 text-xs text-white/42">{tx.user?.email ?? '—'}</p>
                                    </div>
                                </td>
                                <td>
                                    {tx.items && tx.items.length > 0 ? (
                                        <ul className="space-y-1">
                                            {tx.items.map((item, i) => (
                                                <li key={i} className="flex items-center gap-2 text-sm">
                                                    <span className="font-medium text-white/88">{item.product_name}</span>
                                                    <span className="text-white/42">×{item.quantity}</span>
                                                    <span className="text-white/56">{formatCurrency(item.unity_price)}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    ) : (
                                        <span className="text-white/42">—</span>
                                    )}
                                </td>
                                <td className="font-semibold text-emerald-300">{formatCurrency(tx.amount)}</td>
                                <td className="capitalize">{tx.payment_method}</td>
                                <td>
                                    <TonePill tone={TX_STATUS[tx.status]?.tone ?? 'neutral'}>
                                        {TX_STATUS[tx.status]?.label ?? tx.status}
                                    </TonePill>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

function AdminDashboard() {
    const { token, user } = useAuth();
    const [tab, setTab] = useState('overview');

    const [products, setProducts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [transactions, setTransactions] = useState([]);
    const [users, setUsers] = useState([]);

    const [loadingProducts, setLoadingProducts] = useState(true);
    const [loadingCategories, setLoadingCategories] = useState(true);
    const [loadingTransactions, setLoadingTransactions] = useState(true);
    const [loadingUsers, setLoadingUsers] = useState(true);
    const [usersError, setUsersError] = useState(null);

    const refreshProducts = async () => {
        startTransition(() => setLoadingProducts(true));

        try {
            const data = await fetchProducts();
            startTransition(() => setProducts(data));
        } catch {
            startTransition(() => setProducts([]));
        } finally {
            startTransition(() => setLoadingProducts(false));
        }
    };

    useEffect(() => {
        let active = true;

        const run = async () => {
            startTransition(() => setLoadingProducts(true));

            try {
                const data = await fetchProducts();
                if (!active) return;

                startTransition(() => setProducts(data));
            } catch {
                if (!active) return;

                startTransition(() => setProducts([]));
            } finally {
                if (active) {
                    startTransition(() => setLoadingProducts(false));
                }
            }
        };

        run();

        return () => {
            active = false;
        };
    }, []);

    useEffect(() => {
        let active = true;

        const run = async () => {
            startTransition(() => setLoadingCategories(true));

            try {
                const data = await fetchCategories();
                if (!active) return;

                startTransition(() => setCategories(data));
            } catch {
                if (!active) return;

                startTransition(() => setCategories([]));
            } finally {
                if (active) {
                    startTransition(() => setLoadingCategories(false));
                }
            }
        };

        run();

        return () => {
            active = false;
        };
    }, []);

    useEffect(() => {
        let active = true;

        const run = async () => {
            startTransition(() => setLoadingTransactions(true));

            try {
                const data = await getAllTransactionsAdmin(token, 1, 50);
                if (!active) return;

                startTransition(() => setTransactions(data.data ?? []));
            } catch {
                if (!active) return;

                startTransition(() => setTransactions([]));
            } finally {
                if (active) {
                    startTransition(() => setLoadingTransactions(false));
                }
            }
        };

        run();

        return () => {
            active = false;
        };
    }, [token]);

    useEffect(() => {
        let active = true;

        const run = async () => {
            startTransition(() => {
                setLoadingUsers(true);
                setUsersError(null);
            });

            try {
                const data = await fetchUsersList(token);
                if (!active) return;

                startTransition(() => setUsers(data));
            } catch (err) {
                if (!active) return;

                startTransition(() => {
                    setUsers([]);
                    setUsersError(err.message);
                });
            } finally {
                if (active) {
                    startTransition(() => setLoadingUsers(false));
                }
            }
        };

        run();

        return () => {
            active = false;
        };
    }, [token]);

    const adminName = user?.prenom || user?.username || user?.userName || 'Admin';
    const lowStockCount = useMemo(
        () => products.filter((product) => Number(product.stock ?? 0) <= 5).length,
        [products]
    );
    const totalRevenue = useMemo(
        () => transactions
            .filter((tx) => tx.status === 'completed')
            .reduce((sum, tx) => sum + Number(tx.amount ?? 0), 0),
        [transactions]
    );
    const activeUsers = useMemo(
        () => users.filter((entry) => !entry.is_deleted).length,
        [users]
    );

    return (
        <div className="dashboard-page space-y-8 pb-12 pt-6">
            <section className="grid gap-6 lg:grid-cols-[1.08fr_0.92fr]">
                <div className="surface-panel rounded-[2.4rem] p-6 sm:p-8">
                    <p className="section-kicker">Espace administration</p>
                    <h1 className="mt-4 font-display text-4xl font-bold tracking-[-0.05em] text-white sm:text-5xl">
                        Bonjour {adminName}, pilotez la boutique depuis un tableau de bord unifié.
                    </h1>
                    <p className="mt-4 max-w-2xl text-base leading-7 text-white/62">
                        Suivez le catalogue, l&apos;activité des comptes et les transactions depuis un cockpit plus lisible et plus cohérent.
                    </p>

                    <div className="mt-6 flex flex-wrap gap-3">
                        <span className="dashboard-chip-soft">Pilotage boutique</span>
                        <span className="dashboard-chip-soft">{products.length} produits chargés</span>
                        <span className="dashboard-chip-soft">{activeUsers} utilisateurs actifs</span>
                    </div>

                    <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                        <button
                            type="button"
                            onClick={() => setTab('products')}
                            className="button-primary inline-flex items-center justify-center gap-2 rounded-full px-6 py-3.5 text-sm font-semibold"
                        >
                            Gérer les produits
                            <FiArrowRight className="h-4 w-4" />
                        </button>
                        <Link to="/products" className="button-secondary inline-flex items-center justify-center gap-2 rounded-full px-6 py-3.5 text-sm font-semibold">
                            Voir la boutique
                            <FiPackage className="h-4 w-4" />
                        </Link>
                    </div>
                </div>

                <div className="surface-panel-dark rounded-[2.4rem] p-6 text-white sm:p-8">
                    <div className="flex items-center justify-between gap-4">
                        <div>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-white/45">Cockpit rapide</p>
                            <h2 className="mt-3 font-display text-3xl font-bold tracking-[-0.05em]">Vue synthétique.</h2>
                        </div>
                        <span className="flex h-12 w-12 items-center justify-center rounded-[1.2rem] border border-white/10 bg-white/[0.08] text-amber-300">
                            <FiShield className="h-5 w-5" />
                        </span>
                    </div>

                    <div className="mt-6 grid gap-4 sm:grid-cols-2">
                        <div className="rounded-[1.7rem] border border-white/10 bg-white/[0.08] p-5">
                            <p className="text-[11px] uppercase tracking-[0.2em] text-white/45">Produits</p>
                            <p className="mt-3 font-display text-4xl font-bold tracking-[-0.05em]">{products.length}</p>
                            <p className="mt-2 text-sm text-white/60">Catalogue actuel prêt à être piloté.</p>
                        </div>
                        <div className="rounded-[1.7rem] border border-white/10 bg-white/[0.08] p-5">
                            <p className="text-[11px] uppercase tracking-[0.2em] text-white/45">Revenus</p>
                            <p className="mt-3 font-display text-4xl font-bold tracking-[-0.05em]">{formatCurrency(totalRevenue)}</p>
                            <p className="mt-2 text-sm text-white/60">Cumul du rapport transactions.</p>
                        </div>
                    </div>

                    <div className="mt-4 rounded-[1.7rem] border border-white/10 bg-white/[0.08] p-5">
                        <p className="text-[11px] uppercase tracking-[0.2em] text-white/45">Points d&apos;attention</p>
                        <div className="mt-3 flex flex-wrap gap-3">
                            <span className="rounded-full bg-white/10 px-4 py-2 text-sm text-white/80">{lowStockCount} stock bas</span>
                            <span className="rounded-full bg-white/10 px-4 py-2 text-sm text-white/80">{transactions.length} rapports</span>
                            <span className="rounded-full bg-white/10 px-4 py-2 text-sm text-white/80">{activeUsers} utilisateurs actifs</span>
                        </div>
                    </div>
                </div>
            </section>

            <section className="surface-panel rounded-[2rem] p-3">
                <div className="flex flex-wrap gap-2">
                    {ADMIN_TABS.map((item) => {
                        const Icon = item.icon;

                        return (
                            <button
                                key={item.id}
                                type="button"
                                onClick={() => setTab(item.id)}
                                className={`dashboard-tab ${tab === item.id ? 'dashboard-tab-active' : 'dashboard-tab-inactive'}`}
                            >
                                <Icon className="h-4 w-4" />
                                {item.label}
                            </button>
                        );
                    })}
                </div>
            </section>

            {tab === 'overview' && (
                <OverviewTab products={products} transactions={transactions} users={users} />
            )}

            {tab === 'products' && (
                <ProductsTab
                    products={products}
                    categories={categories}
                    token={token}
                    loading={loadingProducts || loadingCategories}
                    onRefresh={refreshProducts}
                    setProducts={setProducts}
                />
            )}

            {tab === 'categories' && (
                <CategoriesTab categories={categories} token={token} setCategories={setCategories} />
            )}

            {tab === 'users' && (
                <UsersTab users={users} loading={loadingUsers} error={usersError} />
            )}

            {tab === 'transactions' && (
                <TransactionsTab transactions={transactions} loading={loadingTransactions} />
            )}
        </div>
    );
}

export default AdminDashboard;
