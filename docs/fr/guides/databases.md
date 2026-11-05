# Bases de données

`nx new` peut échafauder un calque de modèle avec SQLModel, SQLAlchemy ou Tortoise-ORM. Nexy n'encapsule pas l'ORM : vous l'utilisez directement, depuis les handlers et les pages.

## Ce que l'échafaudage ajoute

| Fichier | Objectif |
|---|---|
| `src/configs/db.py` | le moteur (SQLModel, SQLAlchemy) ou les `TORTOISE_ORM` réglages |
| `src/models/` | classes de modèles |
| `src/services/` | fonctions qui interrogent les modèles |
| `.env` | `DATABASE_URL`, écrit lorsque vous donnez une URL de base de données pendant `nx new` |

La chaîne de connexion provient de la variable d'environnement `DATABASE_URL`. Lorsqu'il n'est pas configuré, le moteur de l'échafaudage revient à un fichier SQLite local, `dev.db`.

## Utiliser un service dans une page

```nexy filename="src/routes/users/index.nexy"
---
from src.services.user_service import UserService
users = UserService.get_all()
---
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Utiliser un service dans un gestionnaire d'API

```python filename="src/routes/api/users.py"
from src.services.user_service import UserService


async def GET():
    return UserService.get_all()
```

## Tortoise-ORM est asynchrone

Une page s'exécute dans la boucle d'événements du serveur et ne peut pas l'attendre, donc `asyncio.run(...)` échoue avec "ne peut pas être appelée à partir d'une boucle d'événements en cours d'exécution". L'échafaudage `src/configs/db.py` donne à Tortoise une boucle qui lui est propre, dans un seul thread, et deux assistants qui lui envoient une coroutine :

| Où êtes-vous | Appelez | Est-ce que |
|---|---|---|
| le code de synchronisation, tel qu'une page | `run(UserService.get_all())` | l'exécute et renvoie le résultat |
| code asynchrone, tel qu'un gestionnaire ou un contrôleur | `await arun(UserService.get_all())` | le même, sans bloquer le serveur |

```nexy filename="src/routes/users/index.nexy"
---
from src.configs.db import run
from src.services.user_service import UserService
users = run(UserService.get_all())
---
```

Tortoise se connecte la première fois que l'un d'eux est appelé. Appelez le modèle depuis un `async def` (`await UserModel.all()` à l'intérieur d'un service), et non au niveau du module : un appel en dehors d'une coroutine s'exécute avant que Tortoise ne se soit connecté.

Répertoriez tous les modules contenant des modèles dans `TORTOISE_ORM` (l'entrée `models` de `src/configs/db.py`). L'échafaudage répertorie le modèle utilisateur et `aerich.models` ; un modèle dans un module non répertorié est introuvable.

## Migrations

`nx migrate` choisit l'outil pour votre ORM : Alembic pour SQLModel et SQLAlchemy, Aerich pour Tortoise-ORM.

| La commande | fait |
|---|---|
| `nx migrate --init` | initialiser l'outil de migration du projet |
| `nx migrate -m "add users"` | créer une migration à partir des modifications de votre modèle |
| `nx migrate --upgrade` | appliquer les migrations en attente |

Avec Aerich, le premier `nx migrate` exécute `aerich init-db`, ce qui crée ensemble la première migration et les tables ; les suivants exécutent `aerich migrate --name "..."` et `--upgrade` exécutent `aerich upgrade`.

`nx migrate` s'arrête avec un message clair lorsque `DATABASE_URL` est manquant ou que la base de données n'est pas accessible (Alembic uniquement : Aerich signale ses propres erreurs).

### La première migration est faite pour vous

Lorsque vous choisissez un ORM et donnez une URL de base de données, `nx new` configure l'outil de migration, crée la première migration et l'applique, de sorte que la page des utilisateurs réponde au premier `nexy dev`. L'outil de migration (`alembic` ou `aerich`) est installé dans le projet avec l'ORM.

Si la base de données ne répond pas (un serveur PostgreSQL qui ne fonctionne pas, un pilote manquant), `nx new` explique pourquoi, ignore la migration et liste les deux commandes à exécuter lorsqu'elle est prête :

```bash
nexy migrate -m "create tables"
nexy migrate --upgrade
```

Jusqu'à ce que les tables existent, une page qui lit la base de données échoue avec "aucune table de ce type".

### Ajouter un modèle

Alembic compare la base de données avec les modèles importés par `alembic/env.py`. Un modèle dans un nouveau module n'est pas visible tant que ce module n'y est pas importé, à côté du modèle utilisateur :

```python filename="alambic/env.py"
import src.models.user_model  # noqa: F401
import src.models.post_model  # noqa: F401
```

Pour Tortoise-ORM, répertoriez plutôt le module dans `TORTOISE_ORM` (voir ci-dessus).

## Prochaines étapes

- [Tests](testing.md) : tester les gestionnaires sur une base de données temporaire
- [Configuration](../reference/config.md)
- [Déploiement](../deployment/README.md) : définir `DATABASE_URL` en production
