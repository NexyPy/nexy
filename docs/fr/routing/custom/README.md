# Inclure un routeur FastAPI existant dans Nexy

Pour inclure un routeur FastAPI existant dans Nexy, définissez `useRouter` sur celui `APIRouter` dans la classe `NexyConfig` de `nexyconfig.py` : ses routes sont servies telles quelles, à côté des fichiers de `src/routes/`.

## Quand utiliser un routeur personnalisé

- **Migration progressive** : une application FastAPI se déplace vers Nexy route par route, et ses anciennes routes continuent de répondre entre-temps.
- **Réutilisation du code** : un package expose déjà un `APIRouter`, pour l'authentification ou la facturation.
- **Un backend que vous conservez** : l'API reste simple FastAPI, et Nexy ajoute les pages.

## Réglez `useRouter` dans `nexyconfig.py`

Le routeur est n'importe quel FastAPI `APIRouter`, écrit de la même manière que vous en écrivez déjà un :

```python filename="src/legacy/api.py"
from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/status")
async def status():
    return {"status": "ok"}


@router.get("/users/{id}")
async def user(id: int):
    return {"id": id}
```

`useRouter` est un champ de la classe `NexyConfig`, comme chaque paramètre du projet :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.api import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

`nx dev` répond ensuite à `GET /api/status` et `GET /api/users/{id}`, et `/docs` les répertorie.

> [!NOTE]
> `useRouter` dans `nexyconfig.py` est un paramètre. `from nexy import useRouter` est une autre chose : le hook qu'une page `.nexy` utilise pour lire l'itinéraire actuel. Ne l'importez pas pour configurer le routeur.

## Plusieurs routeurs

`useRouter` prend un routeur. Rassemblez-en plusieurs sous un même parent avec `include_router` :

```python filename="src/legacy/__init__.py"
from fastapi import APIRouter

from .api import router as api
from .auth import router as auth

router = APIRouter()
router.include_router(api)
router.include_router(auth, prefix="/auth")
```

```python filename="src/legacy/auth.py"
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
async def login():
    return {"token": "demo"}
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import router


class NexyConfig(NexyConfigModel):
    useRouter = router
```

## Pages et acheminer les fichiers à côté

`src/routes/` est toujours lu pendant que `useRouter` est défini : une page `.nexy` ou un fichier de route `.py` répond à côté des routes incluses.

```nexy filename="src/routes/index.nexy"
---
title = "Home"
---
<h1>{{ title }}</h1>
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"ok": True}
```

Deux limites lorsque `useRouter` est défini :

- les pages ne sont pas enveloppées par `layout.nexy` ;
- `useCSR = True` est refusé : `nx dev` et `nx build` répondent `useCSR requires file-based routing`.

Une URL reçoit une réponse une fois. Donnez un préfixe au routeur inclus, ici `/api`, et conservez les fichiers de `src/routes/` hors des chemins qu'il utilise.

## Toute une application FastAPI

`useRouter` prend une application `APIRouter`, pas une `FastAPI`. Les itinéraires d'une application reposent sur son attribut `router` :

```python filename="src/legacy/service.py"
from fastapi import FastAPI

service = FastAPI(title="Billing")


@service.get("/billing/invoices")
async def invoices():
    return []
```

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy.service import service


class NexyConfig(NexyConfigModel):
    useRouter = service.router
```

Le middleware, les gestionnaires d'exceptions et les événements de démarrage de l'application restent en arrière-plan : déplacez-les vers `useMiddlewares` et les autres champs de `nexyconfig.py`.

## Dépendances, authentification et base de données

Le routeur s'exécute dans le processus Nexy, donc `Depends`, les schémas de sécurité et les sessions de base de données fonctionnent comme dans l'application d'origine :

```python filename="src/legacy/secure.py"
from fastapi import APIRouter, Depends, Header, HTTPException


def require_token(x_token: str = Header("")) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=401, detail="Bad token")


router = APIRouter(prefix="/secure", dependencies=[Depends(require_token)])


@router.get("/data")
async def data():
    return {"data": 42}
```

## Testez-le

```python filename="tests/test_legacy.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_the_included_route_answers():
    assert TestClient(app).get("/api/status").json() == {"status": "ok"}
```

## Prochaines étapes

- [De FastAPI vers Nexy](../../coming-from/fastapi.md) : déplacez les routes vers les fichiers, une à une
- [Routage basé sur des fichiers](../fbr/README.md)
- [Routage modulaire](../modular/README.md) : `useRouter = AppModule`
