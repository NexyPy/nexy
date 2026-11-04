# Validation et erreurs

Comment un gestionnaire d'API signale une mauvaise requête.

## Validation

Les paramètres du gestionnaire sont validés par FastAPI par rapport à leurs annotations.

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| Problème | État | Corps |
|---|---|---|
| requête, en-tête, cookie ou champ de corps manquant ou invalide | `422` | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| segment **chemin** non valide (`/api/users/abc` pour `id: int`) | `404` | la page introuvable, ou JSON pour `Accept: application/json` |

Un segment de chemin qui ne peut pas être converti est un `404` plutôt qu'un `422` : un itinéraire dynamique capture tout
URL, et il n’existe pas d’URL qui ne peut pas être convertie.

Le corps `422` est la forme standard de FastAPI, donc les clients existants et les SDK générés continuent de fonctionner.

## Réveil d'erreurs

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    item = find(id)
    if item is None:
        raise HTTPException(status_code=404, detail="No such item")
    return item
```

| Le client envoie | Réponse |
|---|---|
| `Accept: application/json` | `{"detail": "No such item"}` avec le statut `404` |
| `Accept: text/html` | la [page d'erreur](../errors/README.md) |
| `Accept: */*` | la page d'erreur |

Définissez `Accept: application/json` dans les clients API. Les navigateurs continuent de recevoir des pages.

## Exceptions non gérées

Une exception selon laquelle votre gestionnaire n'attrape pas les réponses `500`, avec le même choix HTML ou JSON.

## Réponses personnalisées

Renvoyez un objet de réponse lorsque vous contrôlez le corps :

```python
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"error": "conflict"}, status_code=409)
```

## Prochaines étapes

- [Routes API](README.md)
- [Pages d'erreur](../errors/README.md)
- [Tests](../../../guides/testing.md)