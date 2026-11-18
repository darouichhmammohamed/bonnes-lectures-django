# 📚 Bonnes Lectures – Application web Django

Application web de **partage de livres et d'avis de lecture**, développée avec **Django** pendant les TP de *Framework Web 1* (Université d'Orléans, 2026-2027).

Les utilisateurs connectés peuvent ajouter des livres et des auteurs, et publier des avis notés de 1 à 5. Chacun ne peut modifier que ce qu'il a créé.

## Fonctionnalités

**Livres**
- Liste paginée (10 livres par page) et page de détail
- Ajout, modification et suppression (réservés au propriétaire du livre)
- Plusieurs auteurs par livre (relation *many-to-many*)
- **ISBN-13 validé** : 13 chiffres, préfixe 978 ou 979, clé de contrôle calculée

**Avis**
- Avis avec texte et note de 1 à 5 sur chaque livre
- Liste paginée des avis (5 par page) sur la page du livre
- Modification et suppression réservées à l'auteur de l'avis

**Auteurs**
- Liste des auteurs triée par nom, page de détail
- Ajout et modification (réservée au propriétaire)

**Comptes**
- Connexion et déconnexion avec le système d'authentification de Django
- Pages d'ajout et de modification protégées par `@login_required`
- Interface d'administration Django (`/admin`)

## Technologies

| Domaine | Outils |
|---|---|
| Langage | Python 3 |
| Framework | Django 6 |
| Base de données | SQLite (ORM Django, 12 migrations) |
| Interface | Templates Django + Bootstrap 5 (`django-bootstrap5`) |
| Tests | `django.test.TestCase` (22 tests) |

## Points techniques intéressants

### Un champ de modèle personnalisé : `IsbnField`
Le fichier [`mainapp/isbn.py`](mainapp/isbn.py) définit :
- une classe **`Isbn`** qui découpe un ISBN (`978-2-07-036822-8` → préfixe, groupe, éditeur, titre, clé), calcule et vérifie la **clé de contrôle** ;
- un champ **`IsbnField`** (hérite de `models.Field`) : en base, l'ISBN est stocké comme texte, et Django le relit automatiquement comme un objet `Isbn` (`from_db_value`, `to_python`, `get_prep_value`).

```python
Isbn.validate("978-2-07-036822-8")   # ✅ valide
Isbn.validate("978-2-07-036822-9")   # ❌ ValidationError : clé de contrôle incorrecte
```

### Chaque utilisateur ne modifie que ses propres données
```python
book = get_object_or_404(Book, id=book_id, owner=request.user)
```
Si un utilisateur essaie de modifier le livre d'un autre, il obtient une erreur **404**.

### Évolution du modèle par migrations
Les 12 migrations montrent l'évolution du projet de TP en TP : ajout des avis, puis des auteurs, passage d'un auteur en texte à une vraie relation, ajout du propriétaire, puis d'une relation *many-to-many* entre livres et auteurs.

## Structure du projet

```
├── manage.py
├── requirements.txt
├── bonnes_lectures/          Configuration du projet (settings, urls)
└── mainapp/                  Application principale
    ├── models.py             Book, Review, Author
    ├── isbn.py               Classe Isbn + champ IsbnField
    ├── forms.py              Formulaires (ModelForm)
    ├── views.py              Vues (liste, détail, ajout, modification, suppression)
    ├── urls.py               Routes de l'application
    ├── tests.py              Tests unitaires et tests des vues
    ├── migrations/           Historique du schéma de la base
    └── templates/            Pages HTML (Bootstrap 5)
```

## Routes principales

| URL | Page |
|---|---|
| `/` | Accueil |
| `/book/` | Liste des livres |
| `/book/<id>` | Détail d'un livre et ses avis |
| `/new_book/` | Ajouter un livre (connexion requise) |
| `/book/<id>/new_review/` | Ajouter un avis (connexion requise) |
| `/author/` | Liste des auteurs |
| `/accounts/login/` | Connexion |
| `/admin/` | Administration Django |

## Installation et lancement

Prérequis : **Python 3.12** ou plus.

```bash
git clone https://github.com/darouichhmammohamed/bonnes-lectures-django.git
cd bonnes-lectures-django
python -m venv .venv
```

Activer l'environnement virtuel :
- Windows : `.venv\Scripts\activate`
- Linux / macOS : `source .venv/bin/activate`

Puis :
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Ouvrir **http://127.0.0.1:8000** dans le navigateur.

> La clé secrète de Django est lue dans la variable d'environnement `DJANGO_SECRET_KEY`. Sans elle, une clé de développement est utilisée : elle ne doit pas servir en production.

## Tests

```bash
python manage.py test
```

Les 22 tests couvrent la validation des ISBN, le champ `IsbnField`, les modèles, et les vues : pages publiques, redirection vers la connexion, protection des données d'un autre utilisateur, ajout d'un livre et d'un avis.

## Auteur

**Mohamed Aziz Darouich Hmam** – étudiant en L2 à l'Université d'Orléans
