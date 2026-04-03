import os
from app import create_app
from app.extension import db, bcrypt
from app.models import User, Category, Product, Order, OrderItem, Transaction, Panier

app = create_app()

with app.app_context():
    print("Début du seeding de la base de données...")

    # Étape 1: Supprimer les données existantes pour éviter les doublons
    # L'ordre est crucial à cause des clés étrangères (on supprime les tables dépendantes avant les tables parentes)
    print("Suppression des données existantes...")
    OrderItem.query.delete()
    Transaction.query.delete()
    Panier.query.delete()
    Order.query.delete()
    Product.query.delete()
    Category.query.delete()
    User.query.delete()

    # Étape 2: Créer des catégories
    print("Création des catégories...")
    cat_electronique = Category(name="Électronique", description="Appareils et gadgets électroniques.")
    cat_livres = Category(name="Livres", description="Livres, e-books et livres audio.")
    cat_vetements = Category(name="Vêtements", description="Vêtements pour hommes, femmes et enfants.")
    
    db.session.add_all([cat_electronique, cat_livres, cat_vetements])

    # On flush la session pour que les catégories obtiennent un ID avant de créer les produits
    db.session.flush()

    # Étape 3: Créer des produits
    print("Création des produits...")
    prod1 = Product(name="Smartphone XYZ", description="Un smartphone dernier cri avec un appareil photo de 108MP.", price=799.99, stock=50, category_id=cat_electronique.id)
    prod2 = Product(name="Ordinateur Portable Pro", description="Puissant et léger, parfait pour les professionnels.", price=1299.00, stock=30, category_id=cat_electronique.id)
    prod3 = Product(name="Le Seigneur des Anneaux", description="L'intégrale de la trilogie en édition collector.", price=45.50, stock=100, category_id=cat_livres.id)
    prod4 = Product(name="T-shirt en Coton Bio", description="Confortable, stylé et respectueux de l'environnement.", price=29.99, stock=200, category_id=cat_vetements.id)

    db.session.add_all([prod1, prod2, prod3, prod4])

    # Étape 4: Créer des utilisateurs (un admin et un utilisateur normal)
    print("Création des utilisateurs...")
    admin_password = os.environ.get("SEED_ADMIN_PASSWORD", "AdminPass123!")
    user_password = os.environ.get("SEED_USER_PASSWORD", "UserPass123!")

    admin_user = User(
        username="admin",
        email="admin@example.com",
        password_hash=bcrypt.generate_password_hash(admin_password).decode('utf-8'),
        nom="Admin",
        prenom="Super",
        is_admin=True
    )

    normal_user = User(
        username="johndoe",
        email="john.doe@example.com",
        password_hash=bcrypt.generate_password_hash(user_password).decode('utf-8'),
        nom="Doe",
        prenom="John"
    )

    db.session.add_all([admin_user, normal_user])

    # Étape 5: Commit final
    db.session.commit()

    print("Seeding terminé avec succès !")
