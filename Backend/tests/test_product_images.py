import io
from pathlib import Path

from flask_bcrypt import Bcrypt

from app.extension import db
from app.models import Category, Product, User


def _configure_uploads(app, tmp_path):
    upload_dir = tmp_path / 'product-images'
    upload_dir.mkdir(parents=True, exist_ok=True)
    app.config['PRODUCT_IMAGE_UPLOAD_FOLDER'] = str(upload_dir)
    return upload_dir


def _create_admin_headers(client, app):
    with app.app_context():
        bcrypt = Bcrypt(app)
        admin = User(
            username='admin_images',
            email='admin_images@example.com',
            password_hash=bcrypt.generate_password_hash('AdminPass123!').decode('utf-8'),
            nom='Admin',
            prenom='Images',
            is_admin=True,
        )
        db.session.add(admin)
        db.session.commit()

    response = client.post('/auth/v1/login', json={
        'email': 'admin_images@example.com',
        'password': 'AdminPass123!',
    })

    assert response.status_code == 200
    token = response.get_json()['data']['access_token']
    return {'Authorization': f'Bearer {token}'}


def _create_category(app, name='Image Test'):
    with app.app_context():
        category = Category(name=name, description='Categorie de test')
        db.session.add(category)
        db.session.commit()
        return category.id


def _create_product(app, category_id, image_filename=None):
    with app.app_context():
        product = Product(
            name='Produit image',
            description='Produit pour test image',
            price=99.99,
            stock=8,
            category_id=category_id,
            image_filename=image_filename,
        )
        db.session.add(product)
        db.session.commit()
        return product.id


def test_admin_can_create_product_with_image(client, app, tmp_path):
    upload_dir = _configure_uploads(app, tmp_path)
    admin_headers = _create_admin_headers(client, app)
    category_id = _create_category(app, name='Creation Image')

    response = client.post(
        '/api/v1/products',
        data={
            'name': 'Produit illustré',
            'description': 'Produit avec image',
            'price': '149.90',
            'stock': '12',
            'category_id': str(category_id),
            'image': (io.BytesIO(b'fake-png-bytes'), 'produit.png'),
        },
        headers=admin_headers,
        content_type='multipart/form-data',
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload['data']['image_url']
    assert '/api/v1/uploads/products/' in payload['data']['image_url']

    saved_files = list(upload_dir.iterdir())
    assert len(saved_files) == 1
    assert saved_files[0].suffix == '.png'


def test_admin_can_replace_product_image_on_update(client, app, tmp_path):
    upload_dir = _configure_uploads(app, tmp_path)
    admin_headers = _create_admin_headers(client, app)
    category_id = _create_category(app, name='Update Image')

    old_file = upload_dir / 'old-image.png'
    old_file.write_bytes(b'old-image-content')
    product_id = _create_product(app, category_id, image_filename=old_file.name)

    response = client.put(
        f'/api/v1/products/{product_id}',
        data={
            'name': 'Produit image',
            'description': 'Produit mis a jour',
            'price': '109.50',
            'stock': '6',
            'category_id': str(category_id),
            'image': (io.BytesIO(b'new-png-bytes'), 'new-image.png'),
        },
        headers=admin_headers,
        content_type='multipart/form-data',
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload['data']['image_url']
    assert '/api/v1/uploads/products/' in payload['data']['image_url']

    saved_files = list(upload_dir.iterdir())
    assert len(saved_files) == 1
    assert saved_files[0].name != old_file.name
    assert not old_file.exists()
