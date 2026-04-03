# 🚀 Guide de Déploiement - BoutikLakay

Ce guide vous explique comment déployer votre application e-commerce sur des plateformes gratuites.

---

## 📋 Prérequis

Avant de commencer, assurez-vous d'avoir :
- Un compte GitHub avec votre projet poussé
- Un compte Vercel (gratuit) - [vercel.com](https://vercel.com)
- Un compte Render (gratuit) - [render.com](https://render.com)

---

## 🎨 Déploiement Frontend (Vercel)

### Méthode 1 : Via Interface Web (Recommandé)

1. **Connectez-vous à Vercel**
   - Allez sur [vercel.com](https://vercel.com)
   - Cliquez sur "Add New" → "Project"

2. **Importez votre Repository**
   - Connectez votre compte GitHub
   - Sélectionnez le repository `Ecom`

3. **Configuration du Build**
   ```
   Framework Preset: Vite
   Root Directory: Frontend
   Build Command: npm run build
   Output Directory: dist
   Install Command: npm install
   ```

4. **Variables d'Environnement**

   Ajoutez ces variables dans Settings → Environment Variables :

   ```
   VITE_API_BASE_URL = https://votre-api-render.onrender.com/api/v1
   ```

5. **Déployer**
   - Cliquez sur "Deploy"
   - Attendez la fin du build (2-3 minutes)
   - Votre site est en ligne ! 🎉

### Méthode 2 : Via CLI

```bash
cd Frontend

# Installer Vercel CLI
npm i -g vercel

# Se connecter
vercel login

# Déployer
vercel --prod

# Suivre les instructions et configurer :
# - Root directory: Frontend
# - Build command: npm run build
# - Output directory: dist
```

---

## ⚙️ Déploiement Backend (Render)

### Étape 1 : Créer une Base de Données PostgreSQL

1. **Connectez-vous à Render**
   - Allez sur [render.com](https://render.com)
   - Cliquez sur "New +" → "PostgreSQL"

2. **Configuration**
   ```
   Name: bouticlakay-db
   Database: bouticlakay
   User: bouticlakay_user
   Region: Frankfurt (EU) ou Oregon (US)
   Plan: Free
   ```

3. **Créer la base de données**
   - Cliquez sur "Create Database"
   - **IMPORTANT** : Copiez l'URL de connexion (Internal Database URL)

### Étape 2 : Déployer l'API

1. **Créer un Web Service**
   - Cliquez sur "New +" → "Web Service"
   - Connectez votre repository GitHub

2. **Configuration**
   ```
   Name: bouticlakay-api
   Region: Frankfurt (EU) ou Oregon (US)
   Branch: main
   Root Directory: Backend
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   Plan: Free
   ```

3. **Variables d'Environnement**

   Dans "Environment" → "Environment Variables", ajoutez :

   ```bash
   FLASK_ENV=production

   # Collez l'URL de votre base PostgreSQL (Étape 1)
   DATABASE_URL=postgresql://bouticlakay_user:xxx@xxx.render.com/bouticlakay

   # Générez ces clés avec Python :
   # python -c "import secrets; print(secrets.token_urlsafe(32))"
   SECRET_KEY=<votre_secret_key_generee>
   JWT_SECRET_KEY=<votre_jwt_secret_key_generee>

   # Remplacez par l'URL de votre frontend Vercel
   CORS_ORIGINS=https://votre-frontend.vercel.app,http://localhost:5173

   # Rate limiting (memory pour le plan gratuit)
   RATELIMIT_STORAGE_URI=memory://

   # Logging
   LOG_LEVEL=INFO

   # Migrations auto (optionnel)
   FLASK_APP=app.py
   ```

4. **Déployer**
   - Cliquez sur "Create Web Service"
   - Render va build et déployer (5-10 minutes)

5. **Initialiser la Base de Données**

   Une fois le déploiement terminé :

   - Allez dans l'onglet "Shell" de votre service
   - Exécutez :
   ```bash
   flask db upgrade
   python seed.py  # Optionnel : données de test
   ```

### Étape 3 : Lier Frontend et Backend

1. **Récupérez l'URL de votre API Render**
   ```
   https://bouticlakay-api.onrender.com
   ```

2. **Mettez à jour Vercel**
   - Allez dans votre projet Vercel
   - Settings → Environment Variables
   - Modifiez `VITE_API_BASE_URL` :
   ```
   https://bouticlakay-api.onrender.com/api/v1
   ```

3. **Redéployez le Frontend**
   - Allez dans "Deployments"
   - Cliquez sur les 3 points → "Redeploy"

---

## ✅ Vérification du Déploiement

### Frontend (Vercel)

Testez ces pages :
- [ ] Page d'accueil : `https://votre-site.vercel.app`
- [ ] Produits : `https://votre-site.vercel.app/products`
- [ ] Login : `https://votre-site.vercel.app/login`

### Backend (Render)

Testez ces endpoints :
- [ ] Health check : `https://votre-api.onrender.com/`
- [ ] Swagger : `https://votre-api.onrender.com/apidocs/`
- [ ] Produits : `https://votre-api.onrender.com/api/v1/products`

### Test Complet

1. Créez un compte sur le frontend
2. Ajoutez un produit au panier
3. Créez une commande
4. Vérifiez le dashboard

---

## ⚠️ Limitations du Plan Gratuit

### Render Free Tier
- ⏰ **Sleep après 15 min d'inactivité** → Premier appel lent (30s)
- 💾 **750h/mois** → Suffisant pour un portfolio
- 🔄 **Redémarrage requis tous les mois** pour éviter le sleep

**Solution** : Ajouter un cron job qui ping l'API toutes les 10 minutes
```bash
# Utiliser cron-job.org (gratuit)
URL: https://votre-api.onrender.com/api/v1/products
Intervalle: 10 minutes
```

### Vercel Free Tier
- ✅ **Bande passante illimitée**
- ✅ **100 GB-hours/mois** (largement suffisant)
- ✅ **Déploiements illimités**

---

## 🔧 Maintenance

### Mettre à Jour le Déploiement

#### Frontend (Vercel)
1. Poussez vos changements sur GitHub
2. Vercel redéploie automatiquement ! ✨

#### Backend (Render)
1. Poussez vos changements sur GitHub
2. Render redéploie automatiquement ! ✨

### Voir les Logs

#### Vercel
- Dashboard → Votre projet → Deployments → Logs

#### Render
- Dashboard → Votre service → Logs (temps réel)

### Migrations de Base de Données

Si vous ajoutez/modifiez des modèles :

```bash
# Connectez-vous au Shell Render
flask db migrate -m "Description du changement"
flask db upgrade
```

---

## 🐛 Troubleshooting

### Erreur CORS

**Symptôme** : Frontend ne peut pas contacter l'API

**Solution** :
- Vérifiez `CORS_ORIGINS` dans Render
- Ajoutez l'URL Vercel exacte (sans trailing slash)

### Base de Données Non Initialisée

**Symptôme** : Erreur 500 sur tous les endpoints

**Solution** :
```bash
# Shell Render
flask db upgrade
```

### Frontend Affiche l'Erreur de Connexion

**Symptôme** : "Cannot connect to API"

**Solution** :
- Vérifiez que `VITE_API_BASE_URL` est correct dans Vercel
- Assurez-vous que l'API Render est réveillée (visitez `/apidocs/`)

### Rate Limiting Bloque Tout

**Symptôme** : 429 Too Many Requests

**Solution** :
- Pour production, utilisez Redis au lieu de `memory://`
- Ou augmentez les limites dans `app/config.py`

---

## 📊 Monitoring (Optionnel)

### Sentry (Erreurs)

1. Créez un compte gratuit sur [sentry.io](https://sentry.io)
2. Ajoutez dans Render :
   ```
   SENTRY_DSN=<votre_dsn_sentry>
   ```
3. Dans `app/__init__.py`, ajoutez :
   ```python
   import sentry_sdk
   sentry_sdk.init(dsn=os.getenv('SENTRY_DSN'))
   ```

### Uptime Robot (Monitoring)

1. Créez un compte sur [uptimerobot.com](https://uptimerobot.com)
2. Ajoutez un monitor HTTP(s)
3. URL : `https://votre-api.onrender.com/api/v1/products`
4. Recevez des alertes si l'API est down

---

## 🎉 Félicitations !

Votre application e-commerce est maintenant déployée et accessible au monde entier !

### Prochaines Étapes

- [ ] Ajouter un nom de domaine personnalisé (Vercel + Render supportent)
- [ ] Configurer HTTPS (automatique sur Vercel/Render)
- [ ] Ajouter Google Analytics
- [ ] Créer des screenshots pour le README
- [ ] Partager sur LinkedIn ! 🚀

---

## 📞 Support

En cas de problème :
- 📖 [Documentation Vercel](https://vercel.com/docs)
- 📖 [Documentation Render](https://render.com/docs)
- 💬 Communautés Discord : [Vercel](https://vercel.com/discord) | [Render](https://render.com/community)

---

<div align="center">

**Bon déploiement ! 🚀**

</div>
