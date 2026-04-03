import { startTransition, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import {
    ResponsiveContainer,
    AreaChart,
    Area,
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
    FiCheckCircle,
    FiCreditCard,
    FiEdit2,
    FiHome,
    FiLock,
    FiLogOut,
    FiMail,
    FiMinus,
    FiPackage,
    FiPlus,
    FiSave,
    FiShoppingBag,
    FiTrash2,
    FiUser,
} from 'react-icons/fi';
import useAuth from '../../hooks/useAuth';
import useTheme from '../../hooks/useTheme';
import { getCart, updateCartItem, removeFromCart, clearCart } from '../../api/cartApi';
import { getOrders, createOrder, cancelOrder } from '../../api/orderApi';
import { pay } from '../../api/transactionApi';
import { updateProfile, changePassword } from '../../api/authApi';
import Loading from '../../components/Loading';
import { formatCurrency, formatDate } from '../../utils/format';

const USER_TABS = [
    { id: 'cart', label: 'Mon panier', icon: FiShoppingBag },
    { id: 'orders', label: 'Mes commandes', icon: FiPackage },
    { id: 'account', label: 'Mon compte', icon: FiUser },
];

const ORDER_STATUS = {
    pending: { label: 'En attente', className: 'bg-amber-400/15 text-amber-300 border border-amber-500/20' },
    paid: { label: 'Payée', className: 'bg-emerald-500/12 text-emerald-300 border border-emerald-500/16' },
    cancelled: { label: 'Annulée', className: 'bg-rose-500/12 text-rose-300 border border-rose-500/16' },
};

async function fetchCartItems(token) {
    const data = await getCart(token);
    return data ?? [];
}

async function fetchOrdersList(token) {
    return await getOrders(token);
}

async function fetchUserSummary(token) {
    const [cartItems, orders] = await Promise.all([
        fetchCartItems(token),
        fetchOrdersList(token),
    ]);

    return {
        cartItems: cartItems.reduce((sum, item) => sum + (item.quantity ?? 0), 0),
        ordersCount: orders.length,
        pendingOrders: orders.filter((order) => order.status === 'pending').length,
        spentAmount: orders
            .filter((order) => order.status === 'paid')
            .reduce((sum, order) => sum + Number(order.total_amount ?? 0), 0),
    };
}

function resolveUserProfile(user) {
    const firstName = user?.prenom || user?.first_name || '';
    const lastName = user?.nom || user?.last_name || '';
    const username = user?.username || user?.userName || 'compte';
    const fullName = `${firstName} ${lastName}`.trim() || username;
    const initials = `${firstName?.[0] ?? ''}${lastName?.[0] ?? ''}`.trim().toUpperCase() || username[0]?.toUpperCase() || '?';

    return {
        firstName: firstName || username,
        lastName,
        username,
        fullName,
        initials,
        email: user?.email || '—',
        roleLabel: user?.is_admin ? 'Administrateur' : 'Client',
    };
}

function StatusPill({ status }) {
    const meta = ORDER_STATUS[status] ?? {
        label: status ?? 'Inconnu',
        className: 'border border-white/10 bg-white/[0.06] text-white/70',
    };

    return (
        <span className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold ${meta.className}`}>
            {meta.label}
        </span>
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
                    <p className="font-display text-2xl font-bold tracking-[-0.04em] text-white">Une erreur est survenue</p>
                    <p className="mt-2 text-sm leading-6 text-white/56">{message}</p>
                </div>
            </div>
        </div>
    );
}

function EmptyPanel({ icon, title, text, actionLabel, actionTo }) {
    const Icon = icon;

    return (
        <div className="surface-panel rounded-[2rem] px-6 py-14">
            <div className="mx-auto flex max-w-md flex-col items-center text-center">
                <span className="flex h-16 w-16 items-center justify-center rounded-[1.4rem] border border-white/10 bg-white/[0.08] text-amber-300">
                    <Icon className="h-6 w-6" />
                </span>
                <p className="mt-5 font-display text-3xl font-bold tracking-[-0.04em] text-white">{title}</p>
                <p className="mt-3 text-sm leading-6 text-white/56">{text}</p>
                {actionLabel && actionTo && (
                    <Link to={actionTo} className="button-secondary mt-6 inline-flex items-center gap-2 rounded-full px-6 py-3 text-sm font-semibold">
                        {actionLabel}
                        <FiArrowRight className="h-4 w-4" />
                    </Link>
                )}
            </div>
        </div>
    );
}

/* ─────────────── Chart helpers (User) ─────────────── */
const USER_PIE_COLORS = { paid: '#10b981', pending: '#f59e0b', cancelled: '#f43f5e' };

function useUserChartColors() {
    const { theme } = useTheme();
    const dark = theme === 'dark';
    return {
        tick:   dark ? 'rgba(255,255,255,0.4)'  : 'rgba(9,9,11,0.5)',
        grid:   dark ? 'rgba(255,255,255,0.06)' : 'rgba(9,9,11,0.08)',
        legend: dark ? 'rgba(255,255,255,0.65)' : 'rgba(9,9,11,0.65)',
        tooltip: dark ? '#1c1c1c' : '#ffffff',
        tooltipBorder: dark ? 'rgba(255,255,255,0.10)' : 'rgba(9,9,11,0.10)',
    };
}

function UserChartTooltip({ active, payload, label, formatVal }) {
    const c = useUserChartColors();
    if (!active || !payload?.length) return null;
    return (
        <div style={{ background: c.tooltip, border: `1px solid ${c.tooltipBorder}` }} className="rounded-[1rem] px-4 py-3 shadow-xl">
            {label && <p className="mb-2 text-[10px] font-semibold uppercase tracking-[0.18em]" style={{ opacity: 0.5 }}>{label}</p>}
            {payload.map((entry, i) => (
                <p key={i} className="text-sm font-semibold" style={{ color: entry.color ?? entry.fill }}>
                    {entry.name}: {formatVal ? formatVal(entry.value) : entry.value}
                </p>
            ))}
        </div>
    );
}

function SpendingAreaChart({ orders }) {
    const data = useMemo(() => {
        const map = {};
        orders.filter((o) => o.status === 'paid').forEach((order) => {
            if (!order.created_at) return;
            const d = new Date(order.created_at);
            const key = d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
            if (!map[key]) map[key] = { date: key, montant: 0, ts: d.getTime() };
            map[key].montant += Number(order.total_amount ?? 0);
        });
        return Object.values(map).sort((a, b) => a.ts - b.ts);
    }, [orders]);

    if (data.length === 0) {
        return (
            <div className="flex h-44 items-center justify-center text-sm text-white/35">
                Passe ta première commande pour voir ton historique.
            </div>
        );
    }

    const c = useUserChartColors();
    return (
        <ResponsiveContainer width="100%" height={190}>
            <AreaChart data={data} margin={{ top: 8, right: 8, left: -10, bottom: 0 }}>
                <defs>
                    <linearGradient id="gradSpending" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.28} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={c.grid} vertical={false} />
                <XAxis dataKey="date" tick={{ fill: c.tick, fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fill: c.tick, fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v}`} />
                <Tooltip content={<UserChartTooltip formatVal={(v) => formatCurrency(v)} />} />
                <Area type="monotone" dataKey="montant" name="Dépenses" stroke="#10b981" strokeWidth={2.5} fill="url(#gradSpending)" dot={false} activeDot={{ r: 5, fill: '#10b981', stroke: c.tooltip, strokeWidth: 2 }} />
            </AreaChart>
        </ResponsiveContainer>
    );
}

function OrderStatusPieChart({ orders }) {
    const c = useUserChartColors();
    const data = useMemo(() => {
        const paid = orders.filter((o) => o.status === 'paid').length;
        const pending = orders.filter((o) => o.status === 'pending').length;
        const cancelled = orders.filter((o) => o.status === 'cancelled').length;
        return [
            { name: 'Payées', value: paid, fill: USER_PIE_COLORS.paid },
            { name: 'En attente', value: pending, fill: USER_PIE_COLORS.pending },
            { name: 'Annulées', value: cancelled, fill: USER_PIE_COLORS.cancelled },
        ].filter((d) => d.value > 0);
    }, [orders]);

    if (data.length === 0) {
        return <div className="flex h-44 items-center justify-center text-sm text-white/35">Aucune commande enregistrée.</div>;
    }

    return (
        <ResponsiveContainer width="100%" height={190}>
            <PieChart>
                <Pie data={data} cx="50%" cy="44%" innerRadius={46} outerRadius={72} paddingAngle={4} dataKey="value" stroke="none">
                    {data.map((entry, i) => (
                        <Cell key={i} fill={entry.fill} />
                    ))}
                </Pie>
                <Tooltip content={<UserChartTooltip />} />
                <Legend formatter={(value) => <span style={{ color: c.legend, fontSize: 12 }}>{value}</span>} iconType="circle" iconSize={8} />
            </PieChart>
        </ResponsiveContainer>
    );
}

/* ─────────────── CartTab ─────────────── */
function CartTab({ token, onSync }) {
    const [cart, setCart] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [ordering, setOrdering] = useState(false);
    const [orderMsg, setOrderMsg] = useState(null);

    const refreshCart = async () => {
        startTransition(() => {
            setLoading(true);
            setError(null);
        });

        try {
            const items = await fetchCartItems(token);

            startTransition(() => {
                setCart(items);
            });
        } catch (err) {
            startTransition(() => {
                setError(err.message);
            });
        } finally {
            startTransition(() => {
                setLoading(false);
            });
        }
    };

    useEffect(() => {
        let active = true;

        const run = async () => {
            startTransition(() => {
                setLoading(true);
                setError(null);
            });

            try {
                const items = await fetchCartItems(token);
                if (!active) return;

                startTransition(() => {
                    setCart(items);
                });
            } catch (err) {
                if (!active) return;

                startTransition(() => {
                    setError(err.message);
                });
            } finally {
                if (active) {
                    startTransition(() => {
                        setLoading(false);
                    });
                }
            }
        };

        run();

        return () => {
            active = false;
        };
    }, [token]);

    const itemCount = cart.reduce((sum, item) => sum + (item.quantity ?? 0), 0);
    const total = cart.reduce((sum, item) => sum + (Number(item.product?.price ?? 0) * Number(item.quantity ?? 0)), 0);

    const handleUpdateQty = async (productId, newQty) => {
        try {
            await updateCartItem(productId, newQty, token);
            await refreshCart();
            onSync?.();
            window.dispatchEvent(new Event('cart-updated'));
            toast.success('Quantité mise à jour');
        } catch (err) {
            toast.error(err.message);
        }
    };

    const handleRemove = async (productId) => {
        try {
            await removeFromCart(productId, token);
            await refreshCart();
            onSync?.();
            window.dispatchEvent(new Event('cart-updated'));
            toast.success('Article retiré du panier');
        } catch (err) {
            toast.error(err.message);
        }
    };

    const handleClear = async () => {
        if (!window.confirm('Vider le panier ?')) return;

        const loadingToast = toast.loading('Vidage du panier...');

        try {
            await clearCart(token);
            await refreshCart();
            onSync?.();
            window.dispatchEvent(new Event('cart-updated'));
            toast.success('Panier vidé', { id: loadingToast });
        } catch (err) {
            toast.error(err.message, { id: loadingToast });
        }
    };

    const handleOrder = async () => {
        setOrdering(true);
        setOrderMsg(null);

        const loadingToast = toast.loading('Création de la commande...');

        try {
            const response = await createOrder(token);
            const orderId = response?.data?.order_id;

            toast.success(`Commande #${orderId} créée`, { id: loadingToast });

            setOrderMsg({
                type: 'success',
                text: `Ta commande #${orderId} a bien été créée.`,
            });

            await refreshCart();
            onSync?.();
            window.dispatchEvent(new Event('cart-updated'));
        } catch (err) {
            toast.error(err.message, { id: loadingToast });
            setOrderMsg({
                type: 'error',
                text: err.message,
            });
        } finally {
            setOrdering(false);
        }
    };

    if (loading) return <LoadingPanel label="Chargement du panier..." />;
    if (error) return <ErrorPanel message={error} />;

    if (cart.length === 0) {
        return (
            <EmptyPanel
                icon={FiShoppingBag}
                title="Ton panier attend sa sélection."
                text="Parcours le catalogue et ajoute des produits à ton panier pour les retrouver ici."
                actionLabel="Explorer les produits"
                actionTo="/products"
            />
        );
    }

    return (
        <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <div className="space-y-4">
                {orderMsg && (
                    <div className={`surface-panel rounded-[1.7rem] px-5 py-4 ${orderMsg.type === 'success' ? 'border border-emerald-500/14' : 'border border-rose-500/14'}`}>
                        <div className="flex items-start gap-3">
                            <span className={`mt-0.5 flex h-10 w-10 items-center justify-center rounded-[1rem] ${orderMsg.type === 'success' ? 'bg-emerald-500/12 text-emerald-300' : 'bg-rose-500/12 text-rose-300'}`}>
                                {orderMsg.type === 'success' ? <FiCheckCircle className="h-[1.125rem] w-[1.125rem]" /> : <FiAlertCircle className="h-[1.125rem] w-[1.125rem]" />}
                            </span>
                            <div>
                                <p className="font-semibold text-white">{orderMsg.type === 'success' ? 'Commande prête' : 'Action interrompue'}</p>
                                <p className="mt-1 text-sm leading-6 text-white/56">{orderMsg.text}</p>
                            </div>
                        </div>
                    </div>
                )}

                {cart.map((item) => (
                    <article key={item.id} className="surface-panel card-lift rounded-[2rem] p-5 sm:p-6">
                        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
                            <div className="flex-1">
                                <div className="flex flex-wrap items-center gap-2">
                                    <span className="dashboard-chip-soft">Produit</span>
                                    {(item.product?.stock ?? 0) > item.quantity ? (
                                        <span className="dashboard-chip-soft text-emerald-300">En stock</span>
                                    ) : (
                                        <span className="dashboard-chip-soft text-amber-300">Stock limité</span>
                                    )}
                                </div>
                                <h3 className="mt-4 font-display text-2xl font-bold tracking-[-0.04em] text-white">
                                    {item.product?.name ?? `Produit #${item.product_id}`}
                                </h3>
                                <p className="mt-2 text-sm leading-6 text-white/56">
                                    {formatCurrency(item.product?.price ?? 0)} par unité
                                </p>
                            </div>

                            <button
                                type="button"
                                onClick={() => handleRemove(item.product_id)}
                                className="danger-button inline-flex items-center gap-2 self-start rounded-full px-4 py-2 text-sm font-semibold"
                            >
                                <FiTrash2 className="h-4 w-4" />
                                Retirer
                            </button>
                        </div>

                        <div className="mt-6 flex flex-col gap-4 border-t border-white/10 pt-5 sm:flex-row sm:items-end sm:justify-between">
                            <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] p-1">
                                <button
                                    type="button"
                                    onClick={() => item.quantity > 1 ? handleUpdateQty(item.product_id, item.quantity - 1) : handleRemove(item.product_id)}
                                    className="flex h-10 w-10 items-center justify-center rounded-full bg-white/[0.08] text-white transition hover:bg-white/[0.14]"
                                >
                                    <FiMinus className="h-4 w-4" />
                                </button>
                                <span className="min-w-10 text-center text-sm font-semibold text-white">{item.quantity}</span>
                                <button
                                    type="button"
                                    onClick={() => handleUpdateQty(item.product_id, item.quantity + 1)}
                                    disabled={(item.product?.stock ?? 0) <= item.quantity}
                                    className="flex h-10 w-10 items-center justify-center rounded-full bg-white/[0.08] text-white transition hover:bg-white/[0.14] disabled:cursor-not-allowed disabled:opacity-35"
                                >
                                    <FiPlus className="h-4 w-4" />
                                </button>
                            </div>

                            <div className="text-right">
                                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-white/40">Sous-total</p>
                                <p className="mt-2 font-display text-3xl font-bold tracking-[-0.05em] text-white">
                                    {formatCurrency((item.product?.price ?? 0) * item.quantity)}
                                </p>
                            </div>
                        </div>
                    </article>
                ))}
            </div>

            <aside className="surface-panel rounded-[2rem] p-6 xl:sticky xl:top-28">
                <p className="section-kicker">Résumé panier</p>
                <h3 className="mt-3 font-display text-3xl font-bold tracking-[-0.05em] text-white">Ta sélection.</h3>
                <p className="mt-3 text-sm leading-6 text-white/56">
                    Vérifie tes articles avant de passer commande. Le total est calculé en temps réel.
                </p>

                <div className="mt-6 grid gap-4">
                    <DashboardMetric
                        icon={FiShoppingBag}
                        label="Articles"
                        value={itemCount}
                        hint="Quantité totale actuellement dans le panier."
                        accent="text-white"
                    />
                    <DashboardMetric
                        icon={FiCreditCard}
                        label="Montant"
                        value={formatCurrency(total)}
                        hint="Total estimé avant validation."
                        accent="text-amber-300"
                    />
                </div>

                <div className="mt-6 rounded-[1.7rem] border border-white/10 bg-white/[0.08] px-5 py-5 text-white">
                    <div className="flex items-start justify-between gap-3">
                        <div>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-white/45">Finaliser</p>
                            <p className="mt-2 text-sm leading-6 text-white/70">Confirme ta sélection pour créer ta commande et procéder au paiement.</p>
                        </div>
                        <FiCheckCircle className="mt-1 h-5 w-5 text-amber-300" />
                    </div>
                </div>

                <div className="mt-6 flex flex-col gap-3">
                    <button
                        type="button"
                        onClick={handleOrder}
                        disabled={ordering}
                        className="button-primary inline-flex items-center justify-center gap-2 rounded-full px-6 py-3.5 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-55"
                    >
                        {ordering ? 'Commande en cours...' : 'Commander maintenant'}
                        <FiArrowRight className="h-4 w-4" />
                    </button>

                    <button
                        type="button"
                        onClick={handleClear}
                        className="button-secondary inline-flex items-center justify-center gap-2 rounded-full px-6 py-3.5 text-sm font-semibold"
                    >
                        <FiTrash2 className="h-4 w-4" />
                        Vider le panier
                    </button>
                </div>
            </aside>
        </div>
    );
}

function OrdersTab({ token, onSync }) {
    const [orders, setOrders] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [paying, setPaying] = useState(null);
    const [cancelling, setCancelling] = useState(null);

    const refreshOrders = async () => {
        startTransition(() => {
            setLoading(true);
            setError(null);
        });

        try {
            const data = await fetchOrdersList(token);
            startTransition(() => {
                setOrders(data);
            });
        } catch (err) {
            startTransition(() => {
                setError(err.message);
            });
        } finally {
            startTransition(() => {
                setLoading(false);
            });
        }
    };

    useEffect(() => {
        let active = true;

        const run = async () => {
            startTransition(() => {
                setLoading(true);
                setError(null);
            });

            try {
                const data = await fetchOrdersList(token);
                if (!active) return;

                startTransition(() => {
                    setOrders(data);
                });
            } catch (err) {
                if (!active) return;

                startTransition(() => {
                    setError(err.message);
                });
            } finally {
                if (active) {
                    startTransition(() => {
                        setLoading(false);
                    });
                }
            }
        };

        run();

        return () => {
            active = false;
        };
    }, [token]);

    const pendingCount = orders.filter((order) => order.status === 'pending').length;
    const totalSpent = orders
        .filter((order) => order.status === 'paid')
        .reduce((sum, order) => sum + Number(order.total_amount ?? 0), 0);

    const handlePay = async (order) => {
        setPaying(order.id);
        const loadingToast = toast.loading('Traitement du paiement...');

        try {
            await pay(order.id, order.total_amount, 'card', token);
            toast.success(`Paiement effectué pour la commande #${order.id}`, { id: loadingToast });
            await refreshOrders();
            onSync?.();
        } catch (err) {
            toast.error(err.message, { id: loadingToast });
        } finally {
            setPaying(null);
        }
    };

    const handleCancel = async (id) => {
        if (!window.confirm('Annuler cette commande ?')) return;

        setCancelling(id);
        const loadingToast = toast.loading('Annulation...');

        try {
            await cancelOrder(id, token);
            toast.success('Commande annulée', { id: loadingToast });
            await refreshOrders();
            onSync?.();
        } catch (err) {
            toast.error(err.message, { id: loadingToast });
        } finally {
            setCancelling(null);
        }
    };

    if (loading) return <LoadingPanel label="Chargement des commandes..." />;
    if (error) return <ErrorPanel message={error} />;

    if (orders.length === 0) {
        return (
            <EmptyPanel
                icon={FiPackage}
                title="Aucune commande pour le moment."
                text="Passe ta première commande depuis le panier. Ton historique apparaîtra ici."
                actionLabel="Retour à la boutique"
                actionTo="/products"
            />
        );
    }

    return (
        <div className="space-y-6">
            <div className="grid gap-4 md:grid-cols-3">
                <DashboardMetric
                    icon={FiPackage}
                    label="Commandes"
                    value={orders.length}
                    hint="Historique total enregistré sur ton compte."
                    accent="text-white"
                />
                <DashboardMetric
                    icon={FiAlertCircle}
                    label="En attente"
                    value={pendingCount}
                    hint="Commandes qui attendent encore une action."
                    accent="text-amber-300"
                />
                <DashboardMetric
                    icon={FiCreditCard}
                    label="Déjà payé"
                    value={formatCurrency(totalSpent)}
                    hint="Montant total déjà réglé."
                    accent="text-emerald-300"
                />
            </div>

            {/* ── Graphes statistiques ── */}
            <div className="grid gap-6 lg:grid-cols-2">
                <section className="surface-panel rounded-[2rem] p-6">
                    <p className="section-kicker">Finances</p>
                    <h3 className="mt-2 font-display text-2xl font-bold tracking-[-0.04em] text-white">Dépenses dans le temps.</h3>
                    <p className="mt-1 text-xs text-white/45">Cumul de tes commandes payées par date.</p>
                    <div className="mt-5">
                        <SpendingAreaChart orders={orders} />
                    </div>
                </section>

                <section className="surface-panel rounded-[2rem] p-6">
                    <p className="section-kicker">Commandes</p>
                    <h3 className="mt-2 font-display text-2xl font-bold tracking-[-0.04em] text-white">Répartition par statut.</h3>
                    <p className="mt-1 text-xs text-white/45">Vue d&apos;ensemble de l&apos;état de tes commandes.</p>
                    <div className="mt-5">
                        <OrderStatusPieChart orders={orders} />
                    </div>
                </section>
            </div>

            <div className="grid gap-4">
                {orders.map((order) => (
                    <article key={order.id} className="surface-panel card-lift rounded-[2rem] p-5 sm:p-6">
                        <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">
                            <div>
                                <div className="flex flex-wrap items-center gap-3">
                                    <StatusPill status={order.status} />
                                    <span className="dashboard-chip-soft">Commande #{order.id}</span>
                                </div>
                                <h3 className="mt-4 font-display text-2xl font-bold tracking-[-0.04em] text-white">
                                    Suivi de commande
                                </h3>
                                <p className="mt-2 text-sm leading-6 text-white/56">
                                    Créée le {formatDate(order.created_at)}.
                                </p>
                            </div>

                            <div className="text-left lg:text-right">
                                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-white/40">Montant</p>
                                <p className="mt-2 font-display text-4xl font-bold tracking-[-0.05em] text-white">
                                    {formatCurrency(order.total_amount)}
                                </p>
                            </div>
                        </div>

                        <div className="mt-6 flex flex-col gap-3 border-t border-white/10 pt-5 sm:flex-row sm:items-center sm:justify-between">
                            <div className="rounded-full border border-white/[0.08] bg-white/[0.04] px-4 py-2 text-sm text-white/50">
                                Statut actuel: <span className="font-semibold text-white/80">{ORDER_STATUS[order.status]?.label ?? order.status}</span>
                            </div>

                            {order.status === 'pending' ? (
                                <div className="flex flex-col gap-3 sm:flex-row">
                                    <button
                                        type="button"
                                        onClick={() => handlePay(order)}
                                        disabled={paying === order.id}
                                        className="button-primary rounded-full px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-55"
                                    >
                                        {paying === order.id ? 'Paiement...' : 'Payer maintenant'}
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => handleCancel(order.id)}
                                        disabled={cancelling === order.id}
                                        className="danger-button rounded-full px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-55"
                                    >
                                        {cancelling === order.id ? 'Annulation...' : 'Annuler'}
                                    </button>
                                </div>
                            ) : (
                                <span className="text-sm font-medium text-white/56">
                                    {order.status === 'paid' ? 'Commande déjà réglée.' : 'Commande finalisée.'}
                                </span>
                            )}
                        </div>
                    </article>
                ))}
            </div>
        </div>
    );
}

function AccountTab() {
    const { user, token, Logout, updateUser } = useAuth();
    const profile = resolveUserProfile(user);

    const [editMode, setEditMode] = useState(false);
    const [profileForm, setProfileForm] = useState({
        prenom: user?.prenom ?? '',
        nom: user?.nom ?? '',
        username: user?.username ?? '',
        email: user?.email ?? '',
    });
    const [profileSaving, setProfileSaving] = useState(false);

    const [pwForm, setPwForm] = useState({ current_password: '', new_password: '', confirm_password: '' });
    const [pwSaving, setPwSaving] = useState(false);

    const handleProfileChange = (event) => {
        const { name, value } = event.target;
        setProfileForm((prev) => ({ ...prev, [name]: value }));
    };

    const handleProfileSave = async (event) => {
        event.preventDefault();
        setProfileSaving(true);
        const t = toast.loading('Mise à jour du profil...');
        try {
            const res = await updateProfile(profileForm, token);
            updateUser(res.data ?? res.user ?? profileForm);
            toast.success('Profil mis à jour', { id: t });
            setEditMode(false);
        } catch (err) {
            toast.error(err.message, { id: t });
        } finally {
            setProfileSaving(false);
        }
    };

    const handlePwChange = (event) => {
        const { name, value } = event.target;
        setPwForm((prev) => ({ ...prev, [name]: value }));
    };

    const handlePwSave = async (event) => {
        event.preventDefault();
        if (pwForm.new_password !== pwForm.confirm_password) {
            toast.error('Les mots de passe ne correspondent pas.');
            return;
        }
        setPwSaving(true);
        const t = toast.loading('Changement du mot de passe...');
        try {
            await changePassword({ current_password: pwForm.current_password, new_password: pwForm.new_password }, token);
            toast.success('Mot de passe modifié', { id: t });
            setPwForm({ current_password: '', new_password: '', confirm_password: '' });
        } catch (err) {
            toast.error(err.message, { id: t });
        } finally {
            setPwSaving(false);
        }
    };

    return (
        <div className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
            <aside className="surface-panel-dark rounded-[2.2rem] p-6 text-white">
                <div className="flex flex-col items-start">
                    <span className="section-kicker text-white/60">Profil</span>
                    <div className="mt-5 flex h-20 w-20 items-center justify-center rounded-[1.8rem] bg-amber-400 text-2xl font-bold text-[#0c0c16]">
                        {profile.initials}
                    </div>
                    <h3 className="mt-5 font-display text-3xl font-bold tracking-[-0.05em]">{profile.fullName}</h3>
                    <p className="mt-2 text-sm text-white/65">@{profile.username}</p>
                </div>

                <div className="mt-6 flex flex-wrap gap-2">
                    <span className="rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm text-white/80">
                        {profile.roleLabel}
                    </span>
                    <span className="rounded-full border border-white/10 bg-white/10 px-4 py-2 text-sm text-white/80">
                        Membre actif
                    </span>
                </div>

                <div className="mt-8 rounded-[1.7rem] border border-white/10 bg-white/[0.08] p-5">
                    <div className="flex items-start gap-3">
                        <span className="mt-0.5 flex h-11 w-11 items-center justify-center rounded-[1rem] bg-white/10 text-amber-300">
                            <FiMail className="h-[1.125rem] w-[1.125rem]" />
                        </span>
                        <div>
                            <p className="text-sm font-semibold text-white">Adresse principale</p>
                            <p className="mt-2 text-sm leading-6 text-white/65">{profile.email}</p>
                        </div>
                    </div>
                </div>

                <button
                    type="button"
                    onClick={Logout}
                    className="mt-8 inline-flex w-full items-center justify-center gap-2 rounded-full border border-white/14 px-5 py-3.5 text-sm font-semibold text-white transition hover:bg-white/10 hover:text-white"
                >
                    <FiLogOut className="h-4 w-4" />
                    Se déconnecter
                </button>
            </aside>

            <div className="space-y-6">
                {/* ── Informations personnelles ── */}
                <section className="surface-panel rounded-[2rem] p-6">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                        <div>
                            <p className="section-kicker">Informations personnelles</p>
                            <h3 className="mt-3 font-display text-3xl font-bold tracking-[-0.05em] text-white">
                                {editMode ? 'Modifier ton profil.' : 'Tes informations.'}
                            </h3>
                        </div>
                        {!editMode && (
                            <button
                                type="button"
                                onClick={() => {
                                    setProfileForm({
                                        prenom: user?.prenom ?? '',
                                        nom: user?.nom ?? '',
                                        username: user?.username ?? '',
                                        email: user?.email ?? '',
                                    });
                                    setEditMode(true);
                                }}
                                className="button-secondary inline-flex items-center gap-2 rounded-full px-5 py-3 text-sm font-semibold"
                            >
                                <FiEdit2 className="h-4 w-4" />
                                Modifier
                            </button>
                        )}
                    </div>

                    {editMode ? (
                        <form onSubmit={handleProfileSave} className="mt-6 grid gap-4 sm:grid-cols-2">
                            <div>
                                <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.2em] text-white/42">Prénom</label>
                                <input name="prenom" value={profileForm.prenom} onChange={handleProfileChange} className="dashboard-input w-full" placeholder="Prénom" />
                            </div>
                            <div>
                                <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.2em] text-white/42">Nom</label>
                                <input name="nom" value={profileForm.nom} onChange={handleProfileChange} className="dashboard-input w-full" placeholder="Nom" />
                            </div>
                            <div>
                                <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.2em] text-white/42">Nom d&apos;utilisateur</label>
                                <input name="username" value={profileForm.username} onChange={handleProfileChange} className="dashboard-input w-full" placeholder="username" required />
                            </div>
                            <div>
                                <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.2em] text-white/42">Email</label>
                                <input name="email" type="email" value={profileForm.email} onChange={handleProfileChange} className="dashboard-input w-full" placeholder="email@exemple.com" required />
                            </div>
                            <div className="flex gap-3 sm:col-span-2">
                                <button type="submit" disabled={profileSaving} className="button-primary inline-flex items-center gap-2 rounded-full px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-55">
                                    <FiSave className="h-4 w-4" />
                                    {profileSaving ? 'Enregistrement...' : 'Enregistrer'}
                                </button>
                                <button type="button" onClick={() => setEditMode(false)} className="button-secondary inline-flex items-center gap-2 rounded-full px-5 py-3 text-sm font-semibold">
                                    Annuler
                                </button>
                            </div>
                        </form>
                    ) : (
                        <div className="mt-6 grid gap-4 sm:grid-cols-2">
                            {[
                                { label: 'Prénom', value: user?.prenom || '—' },
                                { label: 'Nom', value: user?.nom || '—' },
                                { label: "Nom d'utilisateur", value: profile.username },
                                { label: 'Email', value: profile.email },
                                { label: 'Rôle', value: profile.roleLabel },
                            ].map((field) => (
                                <div key={field.label} className="rounded-[1.5rem] border border-white/10 bg-white/[0.05] px-5 py-4">
                                    <p className="text-[11px] font-semibold uppercase tracking-[0.2em] text-white/42">{field.label}</p>
                                    <p className="mt-3 text-sm font-semibold text-white">{field.value}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </section>

                {/* ── Changer le mot de passe ── */}
                <section className="surface-panel rounded-[2rem] p-6">
                    <div className="flex items-center gap-3">
                        <span className="flex h-10 w-10 items-center justify-center rounded-[1rem] border border-white/10 bg-white/[0.08] text-amber-300">
                            <FiLock className="h-4 w-4" />
                        </span>
                        <div>
                            <p className="section-kicker">Sécurité</p>
                            <h3 className="mt-1 font-display text-2xl font-bold tracking-[-0.04em] text-white">Changer le mot de passe.</h3>
                        </div>
                    </div>

                    <form onSubmit={handlePwSave} className="mt-6 grid gap-4 sm:grid-cols-2">
                        <div className="sm:col-span-2">
                            <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.2em] text-white/42">Mot de passe actuel</label>
                            <input name="current_password" type="password" value={pwForm.current_password} onChange={handlePwChange} className="dashboard-input w-full" placeholder="••••••••" required />
                        </div>
                        <div>
                            <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.2em] text-white/42">Nouveau mot de passe</label>
                            <input name="new_password" type="password" value={pwForm.new_password} onChange={handlePwChange} className="dashboard-input w-full" placeholder="••••••••" required />
                        </div>
                        <div>
                            <label className="mb-1.5 block text-[11px] font-semibold uppercase tracking-[0.2em] text-white/42">Confirmer le nouveau</label>
                            <input name="confirm_password" type="password" value={pwForm.confirm_password} onChange={handlePwChange} className="dashboard-input w-full" placeholder="••••••••" required />
                        </div>
                        <div className="sm:col-span-2">
                            <button type="submit" disabled={pwSaving} className="button-primary inline-flex items-center gap-2 rounded-full px-5 py-3 text-sm font-semibold disabled:cursor-not-allowed disabled:opacity-55">
                                <FiSave className="h-4 w-4" />
                                {pwSaving ? 'Modification...' : 'Changer le mot de passe'}
                            </button>
                        </div>
                    </form>
                </section>

                {/* ── Accès rapide ── */}
                <section className="surface-panel rounded-[2rem] p-6">
                    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
                        <div>
                            <p className="section-kicker">Accès rapide</p>
                            <h3 className="mt-3 font-display text-3xl font-bold tracking-[-0.05em] text-white">Continue ta navigation.</h3>
                        </div>
                        <span className="dashboard-chip-soft">Expérience Boutik Lakay</span>
                    </div>

                    <div className="mt-6 grid gap-4 sm:grid-cols-2">
                        <Link to="/products" className="surface-panel card-lift rounded-[1.7rem] p-5 transition hover:border-amber-500/16">
                            <div className="flex h-12 w-12 items-center justify-center rounded-[1.2rem] border border-white/10 bg-white/[0.08] text-amber-300">
                                <FiShoppingBag className="h-5 w-5" />
                            </div>
                            <h4 className="mt-5 font-display text-2xl font-bold tracking-[-0.04em] text-white">Retour à la boutique</h4>
                            <p className="mt-2 text-sm leading-6 text-white/56">Explorez les produits, filtrez rapidement et retrouvez les nouveautés du catalogue.</p>
                        </Link>

                        <Link to="/" className="surface-panel card-lift rounded-[1.7rem] p-5 transition hover:border-amber-500/16">
                            <div className="flex h-12 w-12 items-center justify-center rounded-[1.2rem] border border-white/10 bg-white/[0.08] text-amber-300">
                                <FiHome className="h-5 w-5" />
                            </div>
                            <h4 className="mt-5 font-display text-2xl font-bold tracking-[-0.04em] text-white">Voir l&apos;accueil</h4>
                            <p className="mt-2 text-sm leading-6 text-white/56">Revenez à la vitrine pour découvrir les collections, les promotions et les univers du moment.</p>
                        </Link>
                    </div>
                </section>
            </div>
        </div>
    );
}

function UserDashboard() {
    const [tab, setTab] = useState('cart');
    const [summary, setSummary] = useState({
        cartItems: 0,
        ordersCount: 0,
        pendingOrders: 0,
        spentAmount: 0,
    });
    const { token, user } = useAuth();

    const profile = useMemo(() => resolveUserProfile(user), [user]);

    const refreshSummary = async () => {
        try {
            const nextSummary = await fetchUserSummary(token);
            startTransition(() => {
                setSummary(nextSummary);
            });
        } catch {
            // on garde l interface stable si le résumé échoue
        }
    };

    useEffect(() => {
        let active = true;

        const run = async () => {
            try {
                const nextSummary = await fetchUserSummary(token);
                if (!active) return;

                startTransition(() => {
                    setSummary(nextSummary);
                });
            } catch {
                // on garde l interface stable si le résumé échoue
            }
        };

        run();

        return () => {
            active = false;
        };
    }, [token]);

    return (
        <div className="dashboard-page space-y-8 pb-12 pt-6">
            <section className="grid gap-6 lg:grid-cols-[1.08fr_0.92fr]">
                <div className="surface-panel rounded-[2.4rem] p-6 sm:p-8">
                    <p className="section-kicker">Espace client</p>
                    <h1 className="mt-4 font-display text-4xl font-bold tracking-[-0.05em] text-white sm:text-5xl">
                        Bonjour {profile.firstName}, tout ton espace client est ici.
                    </h1>
                    <p className="mt-4 max-w-2xl text-base leading-7 text-white/62">
                        Suis ton panier, tes commandes et tes informations personnelles depuis une interface simple, lisible et rapide.
                    </p>

                    <div className="mt-6 flex flex-wrap gap-3">
                        <span className="dashboard-chip-soft">{profile.roleLabel}</span>
                        <span className="dashboard-chip-soft">{profile.email}</span>
                        <span className="dashboard-chip-soft">Suivi en temps réel</span>
                    </div>

                    <div className="mt-8 flex flex-col gap-3 sm:flex-row">
                        <Link to="/products" className="button-primary inline-flex items-center justify-center gap-2 rounded-full px-6 py-3.5 text-sm font-semibold">
                            Continuer mes achats
                            <FiArrowRight className="h-4 w-4" />
                        </Link>
                        <button
                            type="button"
                            onClick={() => setTab('orders')}
                            className="button-secondary inline-flex items-center justify-center gap-2 rounded-full px-6 py-3.5 text-sm font-semibold"
                        >
                            Voir mes commandes
                            <FiPackage className="h-4 w-4" />
                        </button>
                    </div>
                </div>

                <div className="surface-panel-dark rounded-[2.4rem] p-6 text-white sm:p-8">
                    <div className="flex items-center justify-between gap-4">
                        <div>
                            <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-white/45">Vue rapide</p>
                            <h2 className="mt-3 font-display text-3xl font-bold tracking-[-0.05em]">Ton activité du moment.</h2>
                        </div>
                        <span className="flex h-14 w-14 items-center justify-center rounded-[1.3rem] bg-amber-400/12 text-amber-300 text-xl font-bold">
                            {profile.initials}
                        </span>
                    </div>

                    <div className="mt-6 grid gap-4 sm:grid-cols-2">
                        <div className="rounded-[1.7rem] border border-white/10 bg-white/[0.08] p-5">
                            <p className="text-[11px] uppercase tracking-[0.2em] text-white/45">Panier</p>
                            <p className="mt-3 font-display text-4xl font-bold tracking-[-0.05em]">{summary.cartItems}</p>
                            <p className="mt-2 text-sm text-white/60">article{summary.cartItems > 1 ? 's' : ''} actuellement en attente</p>
                        </div>
                        <div className="rounded-[1.7rem] border border-white/10 bg-white/[0.08] p-5">
                            <p className="text-[11px] uppercase tracking-[0.2em] text-white/45">Commandes</p>
                            <p className="mt-3 font-display text-4xl font-bold tracking-[-0.05em]">{summary.ordersCount}</p>
                            <p className="mt-2 text-sm text-white/60">{summary.pendingOrders} en attente de paiement ou d action</p>
                        </div>
                    </div>

                    <div className="mt-4 rounded-[1.7rem] border border-white/10 bg-white/[0.08] p-5">
                        <div className="flex items-start gap-3">
                            <span className="mt-0.5 flex h-11 w-11 items-center justify-center rounded-[1rem] bg-white/10 text-amber-300">
                                <FiCreditCard className="h-[1.125rem] w-[1.125rem]" />
                            </span>
                            <div>
                                <p className="text-[11px] uppercase tracking-[0.2em] text-white/45">Montant payé</p>
                                <p className="mt-3 font-display text-4xl font-bold tracking-[-0.05em]">{formatCurrency(summary.spentAmount)}</p>
                                <p className="mt-2 text-sm leading-6 text-white/60">Historique total des commandes déjà réglées sur ton compte.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <section className="surface-panel rounded-[2rem] p-3">
                <div className="flex flex-wrap gap-2">
                    {USER_TABS.map((item) => {
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

            {tab === 'cart' && <CartTab token={token} onSync={refreshSummary} />}
            {tab === 'orders' && <OrdersTab token={token} onSync={refreshSummary} />}
            {tab === 'account' && <AccountTab />}
        </div>
    );
}

export default UserDashboard;
