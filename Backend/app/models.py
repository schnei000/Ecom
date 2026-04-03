from .extension import db
from datetime import datetime, timezone
from flask import has_request_context, url_for


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    nom = db.Column(db.String(80), nullable=False)
    prenom = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    orders = db.relationship('Order', backref='user', lazy=True)
    transactions = db.relationship('Transaction', backref='user', lazy=True)
    panier_items = db.relationship('Panier', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'nom': self.nom,
            'prenom': self.prenom,
            'is_admin': self.is_admin,
            'email_confirmed': self.email_confirmed,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    # Numeric(10,2) évite les erreurs de représentation IEEE 754 sur les montants
    price = db.Column(db.Numeric(10, 2), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    is_deleted = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        # Contrainte nommée requise pour la compatibilité SQLite batch mode d'Alembic
        db.UniqueConstraint('name', name='uq_products_name'),
        db.CheckConstraint('price >= 0', name='check_price_non_negative'),
        db.CheckConstraint('stock >= 0', name='check_stock_non_negative'),
    )

    order_items = db.relationship('OrderItem', backref='product', lazy=True)
    panier_items = db.relationship('Panier', backref='product', lazy=True)

    def __repr__(self):
        return f"<Product {self.name}>"

    def to_dict(self):
        image_url = None
        if self.image_filename:
            if has_request_context():
                image_url = url_for('products.get_product_image', filename=self.image_filename, _external=True)
            else:
                image_url = f"/api/v1/uploads/products/{self.image_filename}"

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'stock': self.stock,
            'price': float(self.price) if self.price is not None else None,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'image_url': image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)

    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f"<Category {self.name}>"

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


class Panier(db.Model):
    __tablename__ = "panier"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.CheckConstraint('quantity > 0', name='check_panier_quantity_positive'),
        db.UniqueConstraint('user_id', 'product_id', name='uq_panier_user_product'),
        db.Index('ix_panier_user_id', 'user_id'),
        db.Index('ix_panier_product_id', 'product_id'),
    )

    def __repr__(self):
        return f"<Panier {self.id}>"

    def to_dict(self):
        product_data = None
        if self.product and not self.product.is_deleted:
            product_data = {
                'name': self.product.name,
                'price': float(self.product.price) if self.product.price is not None else None,
                'stock': self.product.stock
            }
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'product': product_data,
            'quantity': self.quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Order(db.Model):
    __tablename__ = "orders"
    __table_args__ = (
        db.Index('ix_orders_user_id', 'user_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    transaction = db.relationship('Transaction', uselist=False, backref='order', lazy=True)

    def __repr__(self):
        return f"<Order {self.id}>"

    def to_dict(self, include_items=False):
        data = {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount) if self.total_amount is not None else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_items:
            data['items'] = []
            for item in self.items:
                item_data = item.to_dict()
                if item.product:
                    item_data['product_name'] = item.product.name
                    item_data['product_description'] = item.product.description
                    # product_available = False si le produit a été soft-deleted depuis la commande
                    item_data['product_available'] = not item.product.is_deleted
                else:
                    item_data['product_name'] = "Produit inconnu"
                    item_data['product_description'] = ""
                    item_data['product_available'] = False
                data['items'].append(item_data)
        return data


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    # Prix figé au moment de la commande (indépendant des modifications futures du produit)
    unity_price = db.Column(db.Numeric(10, 2), nullable=False)

    __table_args__ = (
        db.CheckConstraint('quantity > 0', name='check_orderitem_quantity_positive'),
        db.Index('ix_order_items_order_id', 'order_id'),
        db.Index('ix_order_items_product_id', 'product_id'),
    )

    def __repr__(self):
        return f"<OrderItem {self.id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'quantity': self.quantity,
            'unity_price': float(self.unity_price) if self.unity_price is not None else None
        }


class Transaction(db.Model):
    __tablename__ = "transactions"
    __table_args__ = (
        db.Index('ix_transactions_user_id', 'user_id'),
        db.Index('ix_transactions_order_id', 'order_id'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    ref_externe = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    payment_method = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Transaction {self.id}>"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'order_id': self.order_id,
            'ref_externe': self.ref_externe,
            'amount': float(self.amount) if self.amount is not None else None,
            'status': self.status,
            'payment_method': self.payment_method,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    # unique=True : un JTI ne peut être révoqué qu'une fois
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    # expires_at permet la purge automatique des entrées obsolètes
    expires_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    @classmethod
    def purge_expired(cls):
        """Supprime les tokens dont la date d'expiration est passée."""
        cls.query.filter(cls.expires_at < datetime.now(timezone.utc)).delete(synchronize_session=False)
        db.session.commit()
