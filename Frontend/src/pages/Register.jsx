import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { FiArrowRight, FiEye, FiEyeOff, FiLock, FiMail, FiUser, FiZap } from 'react-icons/fi';
import { register as registerApi } from '../api/authApi';
import useAuth from '../hooks/useAuth';
import Loading from '../components/Loading';

function Register() {
    const navigate = useNavigate();
    const { isAuthenticated } = useAuth();

    const [form, setForm] = useState({
        username: '',
        email: '',
        password: '',
        nom: '',
        prenom: '',
    });
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);

    if (isAuthenticated) return <Navigate to="/" replace />;

    const handleChange = (event) => {
        setForm((current) => ({ ...current, [event.target.name]: event.target.value }));
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);
        const loadingToast = toast.loading('Création de votre compte...');

        try {
            await registerApi(form);
            toast.success('Compte créé avec succès.', { id: loadingToast });
            navigate('/login');
        } catch (err) {
            toast.error(err.message || "Erreur lors de l'inscription", { id: loadingToast });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="relative mx-auto grid min-h-screen max-w-7xl items-center gap-6 px-4 py-24 sm:px-6 lg:grid-cols-[1.02fr_0.98fr] lg:px-8">
            <section className="smoke-panel hidden rounded-[2.8rem] p-8 text-white lg:flex lg:min-h-[44rem] lg:flex-col lg:justify-between lg:p-10">
                <div>
                    <span className="surface-chip-dark inline-flex items-center gap-2 rounded-full px-4 py-2 text-[10px] font-bold uppercase tracking-[0.22em]">
                        <FiZap className="h-3.5 w-3.5 text-amber-300" />
                        Nouveau membre
                    </span>

                    <Link to="/" className="mt-8 inline-block">
                        <p className="font-display text-5xl font-bold tracking-[-0.07em]">
                            Boutik<span className="text-amber-300">Lakay</span>
                        </p>
                    </Link>

                    <h1 className="mt-10 font-display text-[clamp(2.7rem,4vw,4.7rem)] font-bold leading-[0.94] tracking-[-0.06em]">
                        Crée ton compte et garde la main sur toute la boutique.
                    </h1>
                    <p className="mt-5 max-w-xl text-base leading-8 text-white/60">
                        Un seul compte pour suivre tes commandes, retrouver ton panier et gagner du temps lors de tes prochains achats.
                    </p>
                </div>

                <div className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1">
                    {[
                        { value: '48h', label: 'Délai de livraison' },
                        { value: '30j', label: 'Retours sans frais' },
                        { value: '100%', label: 'Paiement sécurisé' },
                    ].map((item) => (
                        <div key={item.label} className="rounded-[1.6rem] border border-white/10 bg-white/[0.05] px-5 py-4">
                            <p className="font-display text-3xl font-bold tracking-[-0.05em] text-amber-300">{item.value}</p>
                            <p className="mt-2 text-[11px] uppercase tracking-[0.18em] text-white/42">{item.label}</p>
                        </div>
                    ))}
                </div>
            </section>

            <section className="flex items-center justify-center">
                <div className="w-full max-w-2xl">
                    <Link to="/" className="mb-6 inline-flex items-center gap-2 smoke-chip rounded-full px-4 py-2 text-sm font-semibold text-white/70 lg:hidden">
                        <FiArrowRight className="h-4 w-4 rotate-180" />
                        Retour à l&apos;accueil
                    </Link>

                    <div className="smoke-panel-soft rounded-[2.6rem] p-7 text-white shadow-[0_26px_80px_rgba(15,23,42,0.18)] sm:p-8">
                        <span className="text-[10px] font-bold uppercase tracking-[0.26em] text-amber-300">
                            Inscription
                        </span>
                        <h2 className="mt-4 font-display text-4xl font-bold tracking-[-0.06em]">
                            Crée ton compte.
                        </h2>
                        <p className="mt-3 max-w-2xl text-sm leading-7 text-white/56">
                            Rejoins Boutik Lakay pour commander plus vite, suivre tes achats et retrouver ta sélection à tout moment.
                        </p>

                        <form onSubmit={handleSubmit} className="mt-8 grid gap-5">
                            <div className="grid gap-5 sm:grid-cols-2">
                                <div>
                                    <label htmlFor="reg-prenom" className="mb-2 block text-[10px] font-bold uppercase tracking-[0.20em] text-white/38">
                                        Prénom
                                    </label>
                                    <div className="relative">
                                        <FiUser className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-white/28" />
                                        <input
                                            id="reg-prenom"
                                            type="text"
                                            name="prenom"
                                            value={form.prenom}
                                            onChange={handleChange}
                                            required
                                            placeholder="Jean"
                                            className="form-input pl-11"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label htmlFor="reg-nom" className="mb-2 block text-[10px] font-bold uppercase tracking-[0.20em] text-white/38">
                                        Nom
                                    </label>
                                    <input
                                        id="reg-nom"
                                        type="text"
                                        name="nom"
                                        value={form.nom}
                                        onChange={handleChange}
                                        required
                                        placeholder="Dupont"
                                        className="form-input"
                                    />
                                </div>
                            </div>

                            <div className="grid gap-5 sm:grid-cols-2">
                                <div>
                                    <label htmlFor="reg-username" className="mb-2 block text-[10px] font-bold uppercase tracking-[0.20em] text-white/38">
                                        Nom d&apos;utilisateur
                                    </label>
                                    <div className="relative">
                                        <FiUser className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-white/28" />
                                        <input
                                            id="reg-username"
                                            type="text"
                                            name="username"
                                            value={form.username}
                                            onChange={handleChange}
                                            required
                                            placeholder="mon_username"
                                            className="form-input pl-11"
                                        />
                                    </div>
                                </div>

                                <div>
                                    <label htmlFor="reg-email" className="mb-2 block text-[10px] font-bold uppercase tracking-[0.20em] text-white/38">
                                        Email
                                    </label>
                                    <div className="relative">
                                        <FiMail className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-white/28" />
                                        <input
                                            id="reg-email"
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
                            </div>

                            <div>
                                <label htmlFor="reg-password" className="mb-2 block text-[10px] font-bold uppercase tracking-[0.20em] text-white/38">
                                    Mot de passe
                                </label>
                                <div className="relative">
                                    <FiLock className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-white/28" />
                                    <input
                                        id="reg-password"
                                        type={showPassword ? 'text' : 'password'}
                                        name="password"
                                        value={form.password}
                                        onChange={handleChange}
                                        required
                                        placeholder="8+ caractères"
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
                                        Inscription...
                                    </>
                                ) : (
                                    <>
                                        Créer mon compte
                                        <FiArrowRight className="h-4 w-4" />
                                    </>
                                )}
                            </button>
                        </form>

                        <p className="mt-8 border-t border-white/[0.08] pt-6 text-center text-sm text-white/42">
                            Déjà membre ?{' '}
                            <Link to="/login" className="font-bold text-amber-300 transition hover:text-amber-200">
                                Se connecter
                            </Link>
                        </p>
                    </div>
                </div>
            </section>
        </div>
    );
}

export default Register;
