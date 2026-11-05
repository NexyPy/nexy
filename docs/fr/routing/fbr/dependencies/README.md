# Dépendances et gardiens

Partagez l'authentification, les sessions de base de données et d'autres configurations sur plusieurs routes avec des dépendances FastAPI. Ils fonctionnent à deux niveaux et le niveau répertoire est hérité comme les mises en page.

| Niveau | Où | s'applique à |
|---|---|---|
| Répertoire | `dependencies.py` | chaque itinéraire du répertoire et ci-dessous, pages incluses |
| Gestionnaire | `Depends`, `@UseGuard`, `@Middleware` | un gestionnaire |

## Par répertoire : `dependencies.py`

Un `dependencies.py` déclare une liste `dependencies` de fonctions simples. Nexy enveloppe chacun dans `Depends`.

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

> [!REMARQUE]
> lister les fonctions elles-mêmes. Un objet `Depends(...)` dans la liste est ignoré.

Chaque route sous `src/routes/admin/` nécessite désormais l'en-tête, les gestionnaires `.py` et les pages `.nexy`.

## Héritage

Les dépendances sont collectées depuis la racine des routes jusqu'au répertoire de la route, **le plus à l'extérieur en premier**, exactement comme les mises en page, et les propres gardes du gestionnaire s'exécutent en dernier :

```text
src/routes/
├─ dependencies.py              1. root
└─ admin/
   ├─ dependencies.py           2. admin
   └─ users/
      ├─ dependencies.py        3. users
      └─ index.py               4. handler guards, then the handler
```

Pour `GET /admin/users`, l'ordre est `root`, `admin`, `users`, les fonctions `@UseGuard` du gestionnaire, ses fonctions `@Middleware`, puis le gestionnaire. Un groupe de routes (`(group)/`) est un répertoire comme les autres, donc son `dependencies.py` en fait partie.

## Par gestionnaire

Utilisez `Depends` dans la signature, comme dans n'importe quelle application FastAPI :

```python filename="src/routes/api/me.py"
from nexy.http import Depends, Header, HTTPException


def current_user(authorization: str = Header(...)) -> str:
    if authorization != "Bearer secret":
        raise HTTPException(status_code=401, detail="Unauthorized")
    return "ada"


async def GET(user: str = Depends(current_user)):
    return {"user": user}
```

## Gardes et middleware sur un gestionnaire

`@UseGuard` et `@Middleware` attachent des dépendances FastAPI à un gestionnaire sans changer sa signature. Les deux sont des dépendances, pas un middleware ASGI :

```python filename="src/routes/admin/users/index.py"
from nexy.decorators import Middleware, UseGuard


def audit() -> None: ...


def must_be_staff(x_staff: str = Header(...)) -> None: ...


@UseGuard(must_be_staff)
@Middleware(audit)
async def GET():
    return {"ok": True}
```

Pour un véritable middleware ASGI (CORS, GZip, sessions, les vôtres), utilisez les options `useMiddlewares` et `use*` dans [Middleware et sécurité](../../../guides/middleware-and-security.md).

## Échec d'une dépendance

Une dépendance rejette une demande en augmentant. `HTTPException` répond avec le statut que vous avez généré, en tant que JSON pour les clients API (`Accept: application/json`) et en tant que page d'erreur pour les navigateurs. Voir [Validation et erreurs](../handlers/validation-and-errors.md).

## Prochaines étapes

- [Héritage](../inheritance.md)
- [Gestionnaires](../handlers/README.md)
- [Middleware et sécurité](../../../guides/middleware-and-security.md)
