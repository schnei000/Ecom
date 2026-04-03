import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
    FiArrowRight,
    FiFacebook,
    FiInstagram,
    FiMail,
    FiMapPin,
    FiPhone,
    FiTwitter,
    FiZap,
} from 'react-icons/fi';

const FOOTER_COLUMNS = [
    {
        title: 'Boutique',
        links: [
            { label: 'Accueil', to: '/' },
            { label: 'Catalogue', to: '/products' },
            { label: 'Nouveautés', to: '/products' },
            { label: 'Collections', to: '/products' },
        ],
    },
    {
        title: 'Parcours',
        links: [
            { label: 'Mon compte', to: '/dashboard' },
            { label: 'Commandes', to: '/dashboard' },
            { label: 'Paiement', to: '/products' },
            { label: 'Livraison', to: '/' },
        ],
    },
    {
        title: 'Maison',
        links: [
            { label: 'Notre histoire', to: '/' },
            { label: 'Vision design', to: '/' },
            { label: 'Confidentialité', to: '/' },
            { label: 'Conditions', to: '/' },
        ],
    },
];

const SOCIALS = [
    { icon: FiInstagram, label: 'Instagram' },
    { icon: FiFacebook, label: 'Facebook' },
    { icon: FiTwitter, label: 'Twitter' },
];

const FOOTER_METRICS = [
    { value: '48h', label: 'Livraison express' },
    { value: '30j', label: 'Retours gratuits' },
    { value: '24/7', label: 'Support dédié' },
];

function Footer() {
    const [email, setEmail] = useState('');
    const [subscribed, setSubscribed] = useState(false);

    const handleNewsletter = (event) => {
        event.preventDefault();
        if (!email) return;
        setSubscribed(true);
        setEmail('');
    };

    return (
        <footer className="relative overflow-hidden border-t border-(--border) bg-(--bg-base) text-(--text)">
            <div className="relative mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
                <div className="grid gap-8 xl:grid-cols-[1.1fr_0.9fr]">
                    <section className="smoke-panel rounded-2xl p-6 sm:p-8">
                        <div className="flex flex-wrap items-start justify-between gap-6">
                            <div className="max-w-xl">
                                <span className="surface-chip-dark inline-flex items-center gap-2 rounded-full px-3 py-2 text-[10px] font-semibold uppercase tracking-[0.14em]">
                                    <FiZap className="h-3.5 w-3.5 text-amber-400" />
                                    Atelier Boutik Lakay
                                </span>
                                <h2 className="mt-5 font-display text-3xl font-bold tracking-[-0.04em] text-(--text) sm:text-4xl">
                                    Moins de clics. Plus de style.
                                </h2>
                                <p className="mt-4 max-w-lg text-sm leading-7 text-zinc-400 sm:text-base">
                                    Un catalogue sélectionné à la main, une interface qui va à l'essentiel et une livraison que tu peux suivre en temps réel. Mode, tech et culture — réunis au même endroit.
                                </p>
                            </div>

                            <div className="grid min-w-[15rem] gap-3 sm:grid-cols-3 xl:grid-cols-1">
                                {FOOTER_METRICS.map((metric) => (
                                    <div key={metric.label} className="rounded-2xl border border-(--border) bg-(--bg-elevated) px-5 py-4">
                                        <p className="font-display text-3xl font-bold tracking-[-0.04em] text-amber-400">{metric.value}</p>
                                        <p className="mt-2 text-xs uppercase tracking-[0.12em] text-zinc-500">{metric.label}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </section>

                    <section className="grid gap-6 sm:grid-cols-2">
                        <div className="smoke-panel-soft rounded-2xl p-6">
                            <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-amber-400">Newsletter</p>
                            <h3 className="mt-4 font-display text-2xl font-bold tracking-[-0.04em] text-(--text)">
                                Reçois les prochains drops.
                            </h3>
                            <p className="mt-3 text-sm leading-6 text-zinc-400">
                                Nouveautés, capsules et offres du moment directement dans ta boîte mail.
                            </p>

                            {subscribed ? (
                                <div className="mt-6 rounded-xl border border-emerald-500/20 bg-emerald-500/08 px-4 py-4">
                                    <p className="text-sm font-semibold text-emerald-400">Inscription validée.</p>
                                    <p className="mt-1 text-sm text-zinc-400">Tu recevras bientôt nos prochains temps forts.</p>
                                </div>
                            ) : (
                                <form onSubmit={handleNewsletter} className="mt-6">
                                    <label htmlFor="footer-email" className="sr-only">
                                        Adresse e-mail pour la newsletter
                                    </label>
                                    <div className="flex overflow-hidden rounded-xl border border-(--border) bg-(--surface)">
                                        <input
                                            id="footer-email"
                                            type="email"
                                            value={email}
                                            onChange={(event) => setEmail(event.target.value)}
                                            placeholder="votre@email.com"
                                            required
                                            className="min-w-0 flex-1 border-0 bg-transparent px-4 py-3 text-sm text-(--text) placeholder:text-zinc-600 focus:outline-none"
                                        />
                                        <button type="submit" className="btn-amber rounded-none rounded-r-xl px-4 py-3">
                                            <FiArrowRight className="h-4 w-4" />
                                        </button>
                                    </div>
                                </form>
                            )}
                        </div>

                        <div className="smoke-panel-soft rounded-2xl p-6">
                            <p className="text-[10px] font-bold uppercase tracking-[0.16em] text-amber-400">Contact</p>
                            <div className="mt-5 space-y-4 text-sm text-zinc-400">
                                <div className="flex items-start gap-3">
                                    <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-(--border) bg-(--surface) text-amber-400">
                                        <FiMail className="h-4 w-4" />
                                    </span>
                                    <div>
                                        <p className="font-semibold text-(--text)">support@boutiklakay.com</p>
                                        <p className="mt-1 text-zinc-500">Réponse rapide pour commandes et assistance.</p>
                                    </div>
                                </div>

                                <div className="flex items-start gap-3">
                                    <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-(--border) bg-(--surface) text-amber-400">
                                        <FiPhone className="h-4 w-4" />
                                    </span>
                                    <div>
                                        <p className="font-semibold text-(--text)">+509 0000 0000</p>
                                        <p className="mt-1 text-zinc-500">Du lundi au samedi, de 9h à 18h.</p>
                                    </div>
                                </div>

                                <div className="flex items-start gap-3">
                                    <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl border border-(--border) bg-(--surface) text-amber-400">
                                        <FiMapPin className="h-4 w-4" />
                                    </span>
                                    <div>
                                        <p className="font-semibold text-(--text)">Studio digital</p>
                                        <p className="mt-1 text-zinc-500">Service en ligne et expérience premium pensée pour mobile et desktop.</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </section>
                </div>

                <div className="mt-12 grid gap-10 border-t border-(--border) pt-10 lg:grid-cols-[1fr_auto]">
                    <div className="grid gap-8 sm:grid-cols-3">
                        {FOOTER_COLUMNS.map((column) => (
                            <div key={column.title}>
                                <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-zinc-600">
                                    {column.title}
                                </p>
                                <ul className="mt-4 space-y-3">
                                    {column.links.map((link) => (
                                        <li key={link.label}>
                                            <Link to={link.to} className="text-sm text-zinc-400 transition hover:text-(--text)">
                                                {link.label}
                                            </Link>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        ))}
                    </div>

                    <div className="flex flex-col gap-4 lg:items-end">
                        <div className="flex items-center gap-2">
                            {SOCIALS.map((social) => (
                                <Link
                                    key={social.label}
                                    to="/"
                                    aria-label={`Suivre Boutik Lakay sur ${social.label}`}
                                    className="smoke-chip flex h-10 w-10 items-center justify-center rounded-full text-zinc-500 transition hover:border-(--border-hover) hover:text-(--text)"
                                >
                                    <social.icon className="h-4 w-4" />
                                </Link>
                            ))}
                        </div>
                        <p className="text-sm text-zinc-600">
                            Visa · Mastercard · Livraison suivie · Paiement protégé
                        </p>
                    </div>
                </div>

                <div className="mt-10 flex flex-col gap-3 border-t border-(--border) pt-6 text-sm text-zinc-600 sm:flex-row sm:items-center sm:justify-between">
                    <p>© {new Date().getFullYear()} Boutik Lakay. Tous droits réservés.</p>
                    <p>Un seul compte. Tout le catalogue. Zéro friction.</p>
                </div>
            </div>
        </footer>
    );
}

export default Footer;
