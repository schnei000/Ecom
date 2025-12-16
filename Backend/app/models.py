from .extension import db
from datetime import datetime

#------------------------------
# UTILISATEUR
#------------------------------

class User(db.Model):
    __tablename__ = "users"


    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nom = db.Column(db.String(80), nullable=False)
    prenom = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    # relation avec d 'autres tables
    orders = db.relationship('Order', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    panier = db.relationship('Cart', uselist=False, backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"
    
#------------------------------
# PRODUIT
#------------------------------

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key= True)
    name= db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)

    # relation avec d 'autres tables
    orders = db.relationship('OrderItem', backref='product', lazy=True)
    cart_items = db.relationship('CartItem', backref='product', lazy=True)

    def __repr__(self):
        return f"<Product {self.name}>"
    
#------------------------------
# CATEGORIE
#------------------------------

class Categorie(db.Model):
    __tablename__ = "categories"


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # relation avec d 'autres tables
    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f"<Categorie {self.name}>"
    
#------------------------------
# Panier
#------------------------------

class Panier(db.Model):
    __tablename__ = "panier"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    products_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    # relation avec d 'autres tables
    user = db.relationship('User', backref='panier_items', lazy=True)
    product = db.relationship('Product', backref='panier_items', lazy=True)

    def __repr__(self):
        return f"<Panier {self.id}>"
    

#------------------------------
# COMMANDE
#------------------------------

class Order(db.Model):
    __tablename__ = "orders"
   
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relation avec d 'autres tables
    items = db.relationship('OrderItem', backref='order', lazy=True)
    transaction = db.relationship('Transaction', uselist=False, backref='order', lazy=True)

    def __repr__(self):
        return f"<Order {self.id}>"

#------------------------------
# ELEMENT DE COMMANDE
#------------------------------

class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unity_price = db.Column(db.Float, nullable=False)

    # relation avec d 'autres tables
    order = db.relationship('Order', backref='order_items', lazy=True)
    product = db.relationship('Product', backref='order_items', lazy=True)


    def __repr__(self):
        return f"<OrderItem {self.id}>"
    
#------------------------------
# TRANSACTION
#------------------------------

class Transaction(db.Model):

    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key= True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)

    date_transaction = db.Column(db.DateTime, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    payment_method = db.Column(db.String(50), nullable=False)

    # relation avec d 'autres tables
    user = db.relationship('User', backref='transactions', lazy=True)
    order = db.relationship('Order', backref='transactions', lazy=True)

    def __repr__(self):
        return f"<Transaction {self.id}>"


