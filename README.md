# BoutikLakay — Plateforme E-commerce Full-Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1.2-black?logo=flask&logoColor=white)
![React](https://img.shields.io/badge/React-19.2-61DAFB?logo=react&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind-4.1-38B2AC?logo=tailwind-css&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-production-336791?logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-orange)
![Tests](https://img.shields.io/badge/Tests-11%20fichiers%20%7C%201984%20lignes-green)

**Application e-commerce complète avec API REST Flask + SPA React — déployable sur Render + Vercel**

[Documentation API (Swagger)](#documentation-api) • [Installation locale](#installation) • [Déploiement](#déploiement)

</div>

---

## Table des matières

- [Présentation](#présentation)
- [Fonctionnalités](#fonctionnalités)
- [Technologies](#technologies)
- [Structure du projet](#structure-du-projet)
- [Modèles de données](#modèles-de-données)
- [Référence API](#référence-api)
- [Installation](#installation)
- [Variables d'environnement](#variables-denvironnement)
- [Tests](#tests)
- [Déploiement](#déploiement)
- [Sécurité](#sécurité)

---

## Présentation

BoutikLakay est une **plateforme e-commerce production-ready** développée en architecture full-stack découplée :

| Couche | Technologie | Hébergement |
|---|---|---|
| **API REST** | Flask 3.1 + PostgreSQL | Render |
| **SPA** | React 19 + Vite + Tailwind CSS | Vercel |

30+ endpoints · 8 tables · 11 fichiers de tests · Documentation Swagger interactive

---

## Fonctionnalités

### Client
- Catalogue produits avec recherche temps réel (debounce 300ms), filtres (prix, catégorie, stock), tri et pagination
- Panier persistant avec badge compteur dynamique et widget flottant
- Création de commandes avec déduction atomique du stock (verrous `FOR UPDATE`)
- Simulation de paiement avec choix du moyen de paiement
- Annulation de commande avec restitution automatique du stock
- Dashboard utilisateur : panier, historique commandes, gestion du compte
- Mise à jour du profil, changement de mot de passe, suppression de compte
- Réinitialisation de mot de passe par email

### Administrateur
- Dashboard avec métriques (utilisateurs, produits, commandes, transactions)
- Graphiques : courbe de ventes, répartition des statuts de commandes, montants par méthode
- CRUD complet produits (avec upload d'image) et catégories
- Ajustement de stock (delta ou valeur absolue)
- Vue paginée de tous les utilisateurs
- Vue toutes transactions + rapport quotidien

### Plateforme
- Authentification JWT : token accès (1h) + refresh (30j) avec rotation
- Révocation de token à la déconnexion (table `TokenBlocklist`)
- Contrôle d'accès basé sur les rôles (`is_admin`)
- Documentation Swagger/OpenAPI à `/apidocs/`
- Theme clair/sombre
- Support proxy inverse (Nginx/Render)

---

## Technologies

### Backend

| Package | Version | Rôle |
|---|---|---|
| Flask | 3.1.2 | Framework web |
| Flask-SQLAlchemy | 3.1.1 | ORM |
| Flask-Migrate | 4.1.0 | Migrations (Alembic) |
| Flask-JWT-Extended | 4.7.1 | Authentification JWT |
| Flask-Bcrypt | 1.0.1 | Hachage de mots de passe |
| Flask-CORS | 6.0.1 | CORS |
| Flask-Limiter | 4.1.1 | Rate limiting |
| Flasgger | 0.9.7.1 | Documentation Swagger/OpenAPI |
| psycopg2-binary | 2.9.11 | Driver PostgreSQL |
| email-validator | 2.3.0 | Validation email (RFC 5322) |
| python-dotenv | 1.2.2 | Variables d'environnement |
| gunicorn | 21.2.0 | Serveur WSGI production |
| redis | 7.3.0 | Rate limiting distribué (optionnel) |

### Frontend

| Package | Version | Rôle |
|---|---|---|
| React | 19.2.0 | Framework UI |
| Vite | 7.2.4 | Build tool |
| React Router DOM | 7.11.0 | Routing côté client |
| Tailwind CSS | 4.1.18 | CSS utility-first |
| Recharts | 3.8.1 | Graphiques admin |
| React Hot Toast | 2.6.0 | Notifications |
| React Icons | 5.6.0 | Icônes |

---

## Structure du projet

```
Ecom/
├── Backend/
│   ├── app/
│   │   ├── __init__.py          # App factory, extensions, headers sécurité OWASP
│   │   ├── config.py            # Configs Dev / Testing / Production
│   │   ├── extension.py         # Initialisation extensions Flask
│   │   ├── models.py            # Modèles SQLAlchemy (8 tables)
│   │   ├── logging_config.py    # Configuration logging structuré
│   │   ├── routes/
│   │   │   ├── auth.py          # /auth/v1 — register, login, logout, refresh, reset
│   │   │   ├── users.py         # /auth/v1 — profil, mot de passe, compte
│   │   │   ├── products.py      # /api/v1/products — CRUD + upload image
│   │   │   ├── categories.py    # /api/v1/categories — CRUD
│   │   │   ├── panier.py        # /api/v1/panier — panier
│   │   │   ├── order.py         # /api/v1/order(s) — commandes
│   │   │   └── transaction.py   # /api/v1/pay, /transactions — paiements
│   │   └── utils/
│   │       └── decorators.py    # @admin_required
│   ├── migrations/
│   │   └── versions/            # 8 migrations Alembic
│   ├── tests/                   # 11 fichiers de tests, 1 984 lignes
│   ├── app.py                   # Point d'entrée Gunicorn
│   ├── seed.py                  # Peuplement BDD (catégories, produits, users)
│   ├── requirements.txt
│   ├── render.yaml              # Config déploiement Render
│   └── .env.example
│
└── Frontend/
    ├── src/
    │   ├── api/                 # Modules clients API
    │   │   ├── authApi.js       # Auth, profil, users admin
    │   │   ├── ProductApi.js    # Produits et catégories
    │   │   ├── cartApi.js       # Panier
    │   │   ├── orderApi.js      # Commandes
    │   │   └── transactionApi.js # Paiements
    │   ├── components/
    │   │   ├── Navbar.jsx       # Navigation, menu utilisateur, badge panier
    │   │   ├── ProductCard.jsx  # Carte produit avec fallback image
    │   │   ├── Loading.jsx      # Spinner (sm/md/lg/xl)
    │   │   └── FloatingCart.jsx # Widget panier flottant avec animation
    │   ├── context/
    │   │   ├── AuthProvider.jsx # Contexte authentification (JWT, user)
    │   │   ├── CartProvider.jsx # Contexte panier (items, totaux)
    │   │   └── ThemeProvider.jsx # Contexte thème clair/sombre
    │   ├── hooks/
    │   │   ├── useAuth.js
    │   │   ├── useCategories.js
    │   │   ├── useTheme.js
    │   │   └── useScrollReveal.js
    │   ├── layout/
    │   │   ├── MainLayout.jsx
    │   │   ├── AuthLayout.jsx
    │   │   ├── DashboardLayout.jsx
    │   │   └── AdminLayout.jsx
    │   ├── pages/
    │   │   ├── Home.jsx         # Hero, catégories, produits vedettes
    │   │   ├── Products.jsx     # Catalogue avec filtres et pagination
    │   │   ├── ProductDetail.jsx
    │   │   ├── Login.jsx
    │   │   ├── Register.jsx
    │   │   ├── NotFound.jsx
    │   │   └── dashboard/
    │   │       ├── UserDashboard.jsx   # Onglets : Panier / Commandes / Compte
    │   │       └── AdminDashboard.jsx  # Onglets : Vue d'ensemble / Produits / Catégories / Users / Transactions
    │   └── routes/
    │       ├── AppRoutes.jsx
    │       ├── PrivateRoutes.jsx
    │       └── AdminRoutes.jsx
    ├── vercel.json              # Config Vercel (SPA rewrites)
    └── .env.example
```

---

## Modèles de données

```
User                               Product
───────────────────────────────    ────────────────────────────────
id, email (unique)                 id, name (unique)
username (unique)                  description, stock (≥ 0)
password_hash                      price Numeric(10,2) (≥ 0)
nom, prenom                        category_id → Category
is_admin, email_confirmed          image_filename, is_deleted
is_deleted                         created_at, updated_at
created_at, updated_at

Category                           Panier
───────────────────────────────    ────────────────────────────────
id, name, description              id
                                   user_id → User
                                   product_id → Product
                                   quantity (> 0)
                                   UNIQUE (user_id, product_id)

Order                              OrderItem
───────────────────────────────    ────────────────────────────────
id, user_id → User                 id, order_id → Order
total_amount Numeric(10,2)         product_id → Product
status: pending|paid|cancelled     quantity (> 0)
created_at, updated_at             unity_price (figé à la commande)

Transaction                        TokenBlocklist
───────────────────────────────    ────────────────────────────────
id, user_id → User                 id, jti (unique)
order_id → Order                   created_at, expires_at
ref_externe (unique)
amount Numeric(10,2)
status: pending|successful
        |failed|cancelled
payment_method
created_at, updated_at
```

---

## Référence API

> Documentation interactive : `http://localhost:5000/apidocs/`

### Authentification — `/auth/v1`

| Méthode | Endpoint | Auth | Limite | Description |
|---|---|---|---|---|
| POST | `/register` | — | 10/min | Création de compte |
| POST | `/login` | — | 5/min | Connexion → access + refresh tokens |
| POST | `/refresh` | Refresh token | — | Renouveler l'access token |
| POST | `/logout` | Bearer | — | Révoquer le token courant |
| POST | `/request-reset` | — | 3/min | Envoyer email de réinitialisation |
| POST | `/reset-password` | — | — | Réinitialiser le mot de passe |

### Utilisateurs — `/auth/v1`

| Méthode | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/me` | Bearer | Profil de l'utilisateur connecté |
| PUT/PATCH | `/me` | Bearer | Mettre à jour le profil |
| PATCH | `/me/password` | Bearer | Changer le mot de passe |
| POST | `/me/delete` | Bearer | Supprimer le compte (soft delete) |
| GET | `/users` | Admin | Liste paginée de tous les utilisateurs |

### Produits — `/api/v1`

| Méthode | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/products` | — | Liste paginée avec filtres |
| GET | `/products/<id>` | — | Détail d'un produit |
| POST | `/products` | Admin | Créer un produit (multipart/form-data) |
| PUT/PATCH | `/products/<id>` | Admin | Modifier un produit |
| DELETE | `/products/<id>` | Admin | Supprimer un produit (soft delete) |
| PATCH | `/products/<id>/stock` | Admin | Ajuster le stock |
| GET | `/uploads/products/<filename>` | — | Servir l'image d'un produit |

**Paramètres GET /products :** `page`, `per_page` (max 100), `search`, `min_price`, `max_price`, `in_stock`, `category_id`

### Catégories — `/api/v1`

| Méthode | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/categories` | — | Liste paginée |
| GET | `/categories/<id>` | — | Détail |
| GET | `/categories/<id>/products` | — | Produits de la catégorie |
| POST | `/categories` | Admin | Créer |
| PUT/PATCH | `/categories/<id>` | Admin | Modifier |
| DELETE | `/categories/<id>` | Admin | Supprimer |

### Panier — `/api/v1/panier`

| Méthode | Endpoint | Auth | Limite | Description |
|---|---|---|---|---|
| GET | `/view` | Bearer | — | Voir le panier |
| POST | `/add` | Bearer | 20/min | Ajouter un article (ou augmenter la qté) |
| PUT | `/update/<product_id>` | Bearer | — | Modifier la quantité |
| DELETE | `/delete/<product_id>` | Bearer | — | Supprimer un article |
| DELETE | `/clear` | Bearer | — | Vider le panier |

### Commandes — `/api/v1`

| Méthode | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/order` | Bearer | Créer une commande depuis le panier |
| GET | `/orders` | Bearer | Historique des commandes |
| GET | `/orders/<id>` | Bearer | Détail d'une commande |
| POST | `/orders/<id>/cancel` | Bearer | Annuler (restitue le stock) |

### Transactions — `/api/v1`

| Méthode | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `/pay` | Bearer | Simuler un paiement |
| GET | `/transactions` | Bearer | Historique des paiements |
| GET | `/transaction/<id>` | Bearer | Détail d'une transaction |
| POST | `/transaction/<id>/cancel` | Bearer | Annuler une transaction |
| GET | `/admin/transactions` | Admin | Toutes les transactions |
| GET | `/transactions/daily` | Admin | Rapport quotidien |

---

## Installation

### Prérequis

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+ (production) ou SQLite (développement)

### Backend

```bash
cd Backend

# Créer et activer l'environnement virtuel
python -m venv virtual
source virtual/bin/activate      # Linux/Mac
# ou
virtual\Scripts\activate         # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env (SECRET_KEY, JWT_SECRET_KEY, DATABASE_URL…)

# Créer les tables
flask db upgrade

# (Optionnel) Données de démonstration
python seed.py

# Lancer le serveur de développement
python app.py
# → http://localhost:5000
# → Swagger : http://localhost:5000/apidocs/
```

### Frontend

```bash
cd Frontend

# Installer les dépendances
npm install

# Configurer l'URL de l'API
cp .env.example .env
# VITE_API_BASE_URL=http://localhost:5000

# Lancer le serveur de développement
npm run dev
# → http://localhost:5173
```

### Comptes de démonstration (après seed.py)

Les mots de passe sont lus depuis les variables d'environnement `SEED_ADMIN_PASSWORD` et `SEED_USER_PASSWORD`.

| Rôle | Email | Username |
|---|---|---|
| Admin | `admin@example.com` | `admin` |
| Utilisateur | `john.doe@example.com` | `johndoe` |

---

## Variables d'environnement

### Backend — `.env`

```env
# Flask
FLASK_ENV=development          # development | production
FLASK_DEBUG=false

# Sécurité (OBLIGATOIRE en production)
SECRET_KEY=change-me
JWT_SECRET_KEY=change-me

# Base de données
DATABASE_URL=sqlite:///ecommerce.db
# Production : postgresql://user:password@host:port/dbname

# JWT
JWT_ACCESS_TOKEN_EXPIRES=3600      # 1 heure (secondes)
JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 jours (secondes)

# CORS
CORS_ORIGINS=http://localhost:5173

# Rate Limiting
RATELIMIT_STORAGE_URI=memory://    # Développement
# RATELIMIT_STORAGE_URI=redis://localhost:6379  # Production avec Redis

# Uploads produits
PRODUCT_IMAGE_UPLOAD_FOLDER=instance/uploads/products

# Email (réinitialisation de mot de passe)
SMTP_HOST=sandbox.smtp.mailtrap.io
SMTP_PORT=587
SMTP_USER=votre_user
SMTP_PASSWORD=votre_password
FRONTEND_URL=http://localhost:5173

# Données seed
SEED_ADMIN_PASSWORD=AdminPass123!
SEED_USER_PASSWORD=UserPass123!

# Serveur
SERVER_HOST=127.0.0.1
SERVER_PORT=5000
LOG_LEVEL=INFO
```

### Frontend — `.env`

```env
VITE_API_BASE_URL=http://localhost:5000
```

---

## Tests

```bash
cd Backend

# Lancer tous les tests
pytest

# Avec rapport de couverture
pytest --cov=app --cov-report=term-missing

# Un fichier spécifique
pytest tests/test_security.py -v
```

### Couverture — 11 fichiers, 1 984 lignes

| Fichier | Ce qui est testé |
|---|---|
| `test_auth.py` | Register, login, refresh, logout, validation JWT |
| `test_users.py` | Profil, mise à jour, changement de mot de passe, suppression |
| `test_products.py` | CRUD, filtres, pagination, soft delete |
| `test_categories.py` | CRUD complet |
| `test_panier.py` | Ajout, modification, suppression, vidage, sécurité stock |
| `test_orders.py` | Création, annulation, déduction stock, une seule commande pending |
| `test_transactions.py` | Paiement, annulation, rapport admin quotidien |
| `test_product_images.py` | Upload, validation type/taille, service d'image |
| `test_security.py` | Rate limiting, SQL injection, CORS, contournement auth, timing attacks |
| `conftest.py` | Fixtures pytest, client de test, initialisation BDD |

---

## Déploiement

### Architecture cible

```
Navigateur
    │
    ▼
Vercel (React SPA)
    │  requêtes HTTPS vers /api/v1 et /auth/v1
    ▼
Render (Flask + Gunicorn — 4 workers)
    │
    ▼
Render PostgreSQL
```

### Étape 1 — Backend sur Render

1. Aller sur [render.com](https://render.com) → **New → Web Service**
2. Connecter le dépôt GitHub — Render détecte automatiquement `render.yaml`
3. Cliquer **Deploy**
4. Après le premier déploiement, ouvrir le **Shell** Render et exécuter :
   ```bash
   flask db upgrade
   python seed.py    # optionnel : données de démo
   ```
5. Noter l'URL du service (ex : `https://bouticlakay-api.onrender.com`)

### Étape 2 — Frontend sur Vercel

1. Aller sur [vercel.com](https://vercel.com) → **New Project**
2. Importer le dépôt GitHub, définir le **Root Directory** sur `Frontend/`
3. Ajouter la variable d'environnement :
   ```
   VITE_API_BASE_URL = https://bouticlakay-api.onrender.com
   ```
4. Cliquer **Deploy**
5. Noter l'URL Vercel (ex : `https://bouticlakay.vercel.app`)

### Étape 3 — Mettre à jour CORS

Sur Render → votre service → **Environment** → modifier :
```
CORS_ORIGINS = https://bouticlakay.vercel.app
```
Puis redéployer le backend.

### Variables d'environnement Render (récapitulatif)

| Variable | Valeur |
|---|---|
| `FLASK_ENV` | `production` |
| `DATABASE_URL` | injecté automatiquement par Render |
| `SECRET_KEY` | généré automatiquement par Render |
| `JWT_SECRET_KEY` | généré automatiquement par Render |
| `CORS_ORIGINS` | URL Vercel réelle |
| `RATELIMIT_STORAGE_URI` | `memory://` (ou URL Redis pour la montée en charge) |

---

## Sécurité

### OWASP Top 10

| Catégorie | Implémentation |
|---|---|
| A01 Broken Access Control | `@admin_required` avec re-vérification en BDD à chaque requête |
| A02 Cryptographic Failures | Bcrypt (12 rounds) + JWT HS256 |
| A03 Injection | SQLAlchemy ORM + requêtes paramétrées |
| A05 Security Misconfiguration | Headers OWASP sur toutes les réponses |
| A07 Authentication Failures | Rate limiting par endpoint + rotation de tokens |
| A09 Logging Failures | Logging structuré avec masquage des données sensibles |

### Headers de sécurité (toutes les réponses)

```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains  (production uniquement)
```

### Autres protections

- **Timing attacks** : hash factice exécuté même si l'utilisateur n'existe pas
- **Overselling** : verrous `SELECT FOR UPDATE` sur le stock lors de l'ajout au panier
- **Double paiement** : contrainte d'unicité `ref_externe` sur les transactions
- **Token volé** : table `TokenBlocklist` + purge probabiliste (1/100) des tokens expirés
- **Soft delete** : les données utilisateurs et produits sont conservées pour l'audit

---

## Auteur

**[Votre Nom]**

- Portfolio : [votre-site.com](#)
- LinkedIn : [linkedin.com/in/votre-profil](#)
- GitHub : [@votre-username](#)

---

<div align="center">

Made with Flask + React

</div>
