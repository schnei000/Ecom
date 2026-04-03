import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { FiArrowRight, FiEye, FiEyeOff, FiLock, FiMail, FiShield, FiZap } from 'react-icons/fi';
import { login as loginApi } from '../api/authApi';
import useAuth from '../hooks/useAuth';
import Loading from '../components/Loading';

function Login() {
    const { login, isAuthenticated } = useAuth();
    const navigate = useNavigate();

    const [form, setForm] = useState({ email: '', password: '' });
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    if (isAuthenticated) return <Navigate to="/" replace />;

    const handleChange = (event) => {
        setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        const loadingToast = toast.loading('Connexion en cours...');

        try {
            const data = await loginApi(form);
            login({
                user: data.data.user,
                token: data.data.access_token,
                refresh_token: data.data.refresh_token,
            });
            toast.success('Connexion réussie.', { id: loadingToast });
            navigate('/');
        } catch (err) {
            toast.error(err.message || 'Identifiants invalides', { id: loadingToast });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="relative mx-auto grid min-h-screen max-w-7xl items-center gap-6 px-4 py-24 sm:px-6 lg:grid-cols-[1.08fr_0.92fr] lg:px-8">
            <section className="smoke-panel hidden rounded-[2.8rem] p-8 text-white lg:flex lg:min-h-[42rem] lg:flex-col lg:justify-between lg:p-10">
                <div>
                    <span className="surface-chip-dark inline-flex items-center gap-2 rounded-full px-4 py-2 text-[10px] font-bold uppercase tracking-[0.22em]">
                        <FiZap className="h-3.5 w-3.5 text-amber-300" />
                        Espace membre
                    </span>

                    <Link to="/" className="mt-8 inline-block">
                        <p className="font-display text-5xl font-bold tracking-[-0.07em]">
                            Boutik<span className="text-amber-300">Lakay</span>
                        </p>
                    </Link>

                    <h1 className="mt-10 font-display text-[clamp(2.8rem,4vw,4.8rem)] font-bold leading-[0.94] tracking-[-0.06em]">
                        Retrouve ton panier, tes commandes et tes favoris.
                    </h1>
                    <p className="mt-5 max-w-xl text-base leading-8 text-white/60">
                        Connecte-toi en quelques secondes pour reprendre ton achat là où tu l&apos;avais laissé.
                    </p>
                </div>

                <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
                    {[
                        { value: '24/7', label: 'Support visible' },
                        { value: '100%', label: 'Paiement protégé' },
                        { value: '1 clic', label: 'Retour au catalogue' },
                    ].map((item) => (
                        <div key={item.label} className="rounded-[1.6rem] border border-white/10 bg-white/[0.05] px-5 py-4">
                            <p className="font-display text-3xl font-bold tracking-[-0.05em] text-amber-300">{item.value}</p>
                            <p className="mt-2 text-[11px] uppercase tracking-[0.18em] text-white/42">{item.label}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section className="flex items-center justify-center">
                <div className="w-full max-w-lg">
                    <Link to="/" className="mb-6 inline-flex items-center gap-2 smoke-chip rounded-full px-4 py-2 text-sm font-semibold text-white/70 lg:hidden">
                        <FiArrowRight className="h-4 w-4 rotate-180" />
                        Retour à l&apos;accueil
                    </Link>

                    <div className="smoke-panel-soft rounded-[2.6rem] p-7 text-white shadow-[0_26px_80px_rgba(15,23,42,0.18)] sm:p-8">
                        <span className="text-[10px] font-bold uppercase tracking-[0.26em] text-amber-300">
                            Connexion
                        </span>
                        <h2 className="mt-4 font-display text-4xl font-bold tracking-[-0.06em]">
                            Bon retour.
                        </h2>
                        <p className="mt-3 text-sm leading-7 text-white/56">
                            Accède à ton compte pour suivre tes commandes, gérer ton panier et finaliser tes achats.
                        </p>

                        <form onSubmit={handleSubmit} className="mt-8 space-y-5">
                            <div>
                                <label htmlFor="login-email" className="mb-2 block text-[10px] font-bold uppercase tracking-[0.20em] text-white/38">
                                    Email
                                </label>
                                <div className="relative">
                                    <FiMail className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-white/28" />
                                    <input
                                        id="login-email"
                                        type="email"
                                        name="email"
                                        value={form.email}
                                        onChange={handleChange}
                                        required
                                        placeholder="vous@email.com"
                                        className="form-input pl-11"
                                    />
                                </div>
                            </div>

                            <div>
                                <label htmlFor="login-password" className="mb-2 block text-[10px] font-bold uppercase tracking-[0.20em] text-white/38">
                                    Mot de passe
                                </label>
                                <div className="relative">
                                    <FiLock className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-white/28" />
                                    <input
                                        id="login-password"
                                        type={showPassword ? 'text' : 'password'}
                                        name="password"
                                        value={form.password}
                                        onChange={handleChange}
                                        required
                                        placeholder="••••••••"
                                        className="form-input pl-11 pr-11"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowPassword((v) => !v)}
                                        className="absolute right-4 top-1/2 -translate-y-1/2 text-white/40 transition hover:text-white/70"
                                    >
                                        {showPassword ? <FiEyeOff className="h-4 w-4" /> : <FiEye className="h-4 w-4" />}
                                    </button>
                                </div>
                            </div>

                            <button type="submit" disabled={loading} className="btn-amber mt-2 flex w-full items-center justify-center gap-2 px-6 py-3.5 text-sm disabled:cursor-not-allowed disabled:opacity-55">
                                {loading ? (
                                    <>
                                        <Loading size="sm" />
                                        Connexion...
                                    </>
                                ) : (
                                    <>
                                        Se connecter
                                        <FiArrowRight className="h-4 w-4" />
                                    </>
                                )}
                            </button>
                        </form>

                        <div className="mt-8 rounded-[1.6rem] border border-white/10 bg-white/[0.05] p-5">
                            <div className="flex items-start gap-3">
                                <span className="mt-0.5 flex h-11 w-11 items-center justify-center rounded-[1rem] bg-white/10 text-amber-300">
                                    <FiShield className="h-[1.125rem] w-[1.125rem]" />
                                </span>
                                <div>
                                    <p className="text-sm font-semibold text-white">Accès protégé</p>
                                    <p className="mt-2 text-sm leading-6 text-white/54">
                                        Tes informations et tes commandes restent accessibles dans un espace sécurisé et lisible.
                                    </p>
                                </div>
                            </div>
                        </div>

                        <p className="mt-8 border-t border-white/[0.08] pt-6 text-center text-sm text-white/42">
                            Pas encore de compte ?{' '}
                            <Link to="/register" className="font-bold text-amber-300 transition hover:text-amber-200">
                                Créer un compte
                            </Link>
                        </p>
                    </div>
                </div>
            </section>
        </div>
    );
}

export default Login;
