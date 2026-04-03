# 🤝 Guide de Contribution - BoutikLakay

Merci de votre intérêt pour contribuer à **BoutikLakay** ! Ce guide vous aidera à démarrer.

---

## 📋 Code of Conduct

Soyez respectueux et professionnel dans toutes vos interactions. Nous visons à créer une communauté accueillante pour tous.

---

## 🚀 Comment Contribuer

### 1. Fork & Clone

```bash
# Fork le projet sur GitHub, puis :
git clone https://github.com/votre-username/Ecom.git
cd Ecom
```

### 2. Créer une Branche

```bash
git checkout -b feature/ma-nouvelle-fonctionnalite
# ou
git checkout -b fix/correction-bug
```

**Convention de nommage** :
- `feature/` - Nouvelles fonctionnalités
- `fix/` - Corrections de bugs
- `docs/` - Documentation
- `refactor/` - Refactoring
- `test/` - Ajout de tests
- `style/` - Changements de style/formatting

### 3. Développer

Installez les dépendances et lancez l'environnement de dev :

```bash
# Backend
cd Backend
python -m venv virtual
source virtual/bin/activate
pip install -r requirements.txt
flask run

# Frontend
cd Frontend
npm install
npm run dev
```

### 4. Tester

Assurez-vous que vos changements ne cassent rien :

```bash
# Backend
cd Backend
pytest

# Frontend
cd Frontend
npm run lint
```

### 5. Commit

Utilisez des messages de commit clairs et descriptifs :

```bash
git add .
git commit -m "feat: ajoute système de wishlist utilisateur"
```

**Convention Conventional Commits** :
- `feat:` - Nouvelle fonctionnalité
- `fix:` - Correction de bug
- `docs:` - Documentation
- `style:` - Formatting, point-virgules manquants, etc.
- `refactor:` - Refactoring de code
- `test:` - Ajout de tests
- `chore:` - Maintenance, dépendances, etc.

### 6. Push & Pull Request

```bash
git push origin feature/ma-nouvelle-fonctionnalite
```

Puis créez une Pull Request sur GitHub avec :
- **Titre clair** décrivant le changement
- **Description** : Qu'est-ce qui change et pourquoi ?
- **Screenshots** si changements UI
- **Tests** : Comment avez-vous testé ?

---

## 📝 Standards de Code

### Python (Backend)

- Suivez **PEP 8**
- Utilisez **type hints** quand possible
- Docstrings pour toutes les fonctions publiques
- Maximum 100 caractères par ligne

```python
def calculate_total(items: list[CartItem]) -> float:
    """
    Calcule le total d'un panier.

    Args:
        items: Liste des articles du panier

    Returns:
        Total en euros
    """
    return sum(item.price * item.quantity for item in items)
```

### JavaScript/React (Frontend)

- Utilisez **ES6+** moderne
- Composants fonctionnels + hooks
- Nommage en **camelCase** pour variables
- Nommage en **PascalCase** pour composants
- Maximum 80 caractères par ligne

```javascript
// ✅ Bon
const MyComponent = ({ product }) => {
    const [isLoading, setIsLoading] = useState(false);

    return <div>{product.name}</div>;
};

// ❌ Éviter
function my_component(props) {
    var loading = false;
    return <div>{props.product.name}</div>;
}
```

---

## 🧪 Tests

### Backend

Ajoutez des tests pour toute nouvelle fonctionnalité :

```python
# tests/test_cart.py
def test_add_to_cart_success(client, auth_headers):
    """Test ajout produit au panier avec stock suffisant"""
    response = client.post(
        '/api/v1/panier/add',
        json={'product_id': 1, 'quantity': 2},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json['message'] == 'Produit ajouté au panier'
```

### Frontend

```javascript
// src/components/__tests__/ProductCard.test.jsx
import { render, screen } from '@testing-library/react';
import ProductCard from '../ProductCard';

test('affiche le nom du produit', () => {
    const product = { id: 1, name: 'Test Product', price: 10 };
    render(<ProductCard product={product} />);
    expect(screen.getByText('Test Product')).toBeInTheDocument();
});
```

---

## 🐛 Signaler un Bug

Créez une **Issue** sur GitHub avec :

1. **Titre descriptif**
2. **Description du bug**
   - Comportement attendu
   - Comportement actuel
   - Steps to reproduce
3. **Environnement**
   - OS
   - Navigateur (si frontend)
   - Version Python/Node
4. **Screenshots** si applicable
5. **Logs d'erreur**

**Template** :

```markdown
## Description
Le panier ne met pas à jour la quantité quand je clique sur +

## Steps to Reproduce
1. Aller sur /products
2. Ajouter un produit au panier
3. Aller sur /dashboard
4. Cliquer sur le bouton +
5. La quantité reste à 1

## Comportement Attendu
La quantité devrait augmenter à 2

## Environnement
- OS: Windows 11
- Browser: Chrome 120
- Python: 3.12
- Node: 20.10

## Screenshots
[Ajouter capture d'écran]

## Logs
```
[Error] Failed to update cart item
```
```

---

## 💡 Idées de Contribution

Vous ne savez pas par où commencer ? Voici des idées :

### Fonctionnalités Recherchées
- [ ] Système d'avis et notes produits ⭐⭐⭐⭐⭐
- [ ] Upload d'images produits (S3)
- [ ] Wishlist utilisateur
- [ ] Codes promo et réductions
- [ ] Notifications email
- [ ] Recherche full-text (Elasticsearch)
- [ ] Multi-devises
- [ ] Mode sombre

### Documentation
- [ ] Améliorer les docstrings
- [ ] Ajouter des diagrammes d'architecture
- [ ] Traduire en anglais
- [ ] Créer des tutoriels vidéo

### Tests
- [ ] Augmenter la couverture de tests
- [ ] Ajouter tests E2E (Playwright)
- [ ] Tests de performance (Locust)

### DevOps
- [ ] Configuration Docker
- [ ] CI/CD GitHub Actions
- [ ] Monitoring (Sentry)
- [ ] Logging avancé (ELK Stack)

---

## 🏷️ Labels GitHub

- `good first issue` - Bon pour débutants
- `help wanted` - Besoin d'aide
- `bug` - Quelque chose ne fonctionne pas
- `enhancement` - Nouvelle fonctionnalité
- `documentation` - Amélioration docs
- `security` - Problème de sécurité

---

## 📚 Ressources

### Documentation Officielle
- [Flask](https://flask.palletsprojects.com/)
- [React](https://react.dev/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Tailwind CSS](https://tailwindcss.com/)

### Guides
- [PEP 8 Style Guide](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)

---

## ✅ Checklist Avant de Submit une PR

- [ ] Code suit les standards (PEP 8, ESLint)
- [ ] Tous les tests passent (`pytest`, `npm run test`)
- [ ] Pas de conflits Git
- [ ] Branch à jour avec `main`
- [ ] Commit messages clairs
- [ ] Documentation mise à jour si nécessaire
- [ ] Screenshots ajoutés si changements UI
- [ ] Aucun fichier sensible (.env, credentials)

---

## 🎉 Après la Merge

Une fois votre PR mergée :

1. Supprimez votre branche locale :
   ```bash
   git checkout main
   git pull origin main
   git branch -d feature/ma-fonctionnalite
   ```

2. Votre nom sera ajouté aux contributeurs ! 🎊

3. N'hésitez pas à partager votre contribution sur LinkedIn

---

## 📞 Questions ?

Si vous avez des questions :
- Ouvrez une **Discussion** sur GitHub
- Contactez : [votre.email@example.com]
- Rejoignez notre Discord : [lien]

---

## 🙏 Merci !

Toute contribution, grande ou petite, est appréciée et aide à améliorer le projet pour tous.

**Happy coding ! 🚀**
