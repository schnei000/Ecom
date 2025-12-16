from app import create_app
from app.extension import db, bcrypt
from app.models import User, Categorie, Product

app = create_app()

with app.app_context():
    print("Début du seeding de la base de données...")

    # Étape 1: Supprimer les données existantes pour éviter les doublons
    # L'ordre est important à cause des clés étrangères (on supprime les enfants avant les parents)
    print("Suppression des données existantes...")
    Product.query.delete()
    Categorie.query.delete()
    User.query.delete()
    db.session.commit()

    # Étape 2: Créer des catégories
    print("Création des catégories...")
    cat_electronique = Categorie(nom="Électronique", description="Appareils et gadgets électroniques.")
    cat_livres = Categorie(nom="Livres", description="Livres, e-books et livres audio.")
    cat_vetements = Categorie(nom="Vêtements", description="Vêtements pour hommes, femmes et enfants.")
    
    db.session.add_all([cat_electronique, cat_livres, cat_vetements])
    db.session.commit() # On commit pour que les catégories aient un ID

    # Étape 3: Créer des produits
    print("Création des produits...")
    prod1 = Product(name="Smartphone XYZ", description="Un smartphone dernier cri avec un appareil photo de 108MP.", price=799.99, stock=50, category_id=cat_electronique.id)
    prod2 = Product(name="Ordinateur Portable Pro", description="Puissant et léger, parfait pour les professionnels.", price=1299.00, stock=30, category_id=cat_electronique.id)
    prod3 = Product(name="Le Seigneur des Anneaux", description="L'intégrale de la trilogie en édition collector.", price=45.50, stock=100, category_id=cat_livres.id)
    prod4 = Product(name="T-shirt en Coton Bio", description="Confortable, stylé et respectueux de l'environnement.", price=29.99, stock=200, category_id=cat_vetements.id)

    db.session.add_all([prod1, prod2, prod3, prod4])

    # Étape 4: Créer des utilisateurs (un admin et un utilisateur normal)
    print("Création des utilisateurs...")
    admin_user = User(
        username="admin",
        email="admin@example.com",
        password=bcrypt.generate_password_hash("adminpassword").decode('utf-8'),
        nom="Admin",
        prenom="Super",
        is_admin=True
    )

    normal_user = User(
        username="johndoe",
        email="john.doe@example.com",
        password=bcrypt.generate_password_hash("userpassword").decode('utf-8'),
        nom="Doe",
        prenom="John"
    )

    db.session.add_all([admin_user, normal_user])

    # Étape 5: Commit final
    db.session.commit()

    print("Seeding terminé avec succès !")
