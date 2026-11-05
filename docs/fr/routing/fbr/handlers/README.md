# Gestionnaires de routes

Un fichier `.py` sous `src/routes/` est un gestionnaire d'API. Le chemin du fichier est l'URL et chaque fonction nommée d'après une méthode HTTP devient un point de terminaison.

## Créer un point de terminaison

```python filename="src/routes/api/items.py"
from nexy.http import Request
from pydantic import BaseModel


class Item(BaseModel):
    name: str


async def GET(request: Request):
    return {"items": []}


async def POST(request: Request, body: Item):
    return {"created": body.name}
```

Ce fichier répond à `GET /api/items` et `POST /api/items`.

Noms de fonctions pris en charge : `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `HEAD`. `SOCKET` ouvre un WebSocket sur le même chemin - voir [WebSocket](../realtime/websocket.md).

## Le vocabulaire HTTP

Importez ce dont un gestionnaire a besoin depuis `nexy.http` :

```python
from nexy.http import Depends, Header, HTTPException, JSONResponse, Request, status
```

Il expose les classes de requêtes et de réponses (`Request`, `Response`, `JSONResponse`, `HTMLResponse`, `PlainTextResponse`, `RedirectResponse`, `StreamingResponse`, `FileResponse`), les sources des paramètres (`Header`, `Query`, `Cookie`, `Path`, `Body`), `Depends`, `BackgroundTasks`, `HTTPException` et `status`. Les gestionnaires écrits sur ce module dépendent du contrat de Nexy, et non du moteur qui les sert. Les modèles Pydantic décrivent les corps et les réponses comme d'habitude.

## Paramètres

| Source | Comment ça arrive |
|---|---|
| Segment de chemin `[id]` | argument de fonction `id`, converti en son annotation |
| Chaîne de requête | `page: int = 1` |
| Corps JSON | Pydantic argument du modèle |
| FastAPI primitives | `Depends`, `Header`, `Cookie`, `Form`, `UploadFile` - inchangées |

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

Le segment de chemin est `{id}`, donc FastAPI valide `id: int`. Une valeur qui n'est pas un entier répond à `404`, car une route dynamique capture n'importe quelle URL et une URL qui ne peut pas être convertie n'existe pas. Voir [Validation et erreurs](validation-and-errors.md).

## Réponses

| Retourner | Réponse |
|---|---|
| `dict`, `list`, `BaseModel` | JSON |
| `JSONResponse`, `HTMLResponse`, n'importe quel `Response` | exactement comme déclaré |
| `None` | réponse vide - renvoie un `Response` à la place lorsque le statut est important |

Pour un code de statut ou un type de contenu personnalisé, renvoyez un objet de réponse :

```python filename="src/routes/api/items.py"
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"created": True}, status_code=201)
```

## Erreurs

Augmentez FastAPI exceptions pour les clients. Un client qui envoie `Accept: application/json` reçoit `{"detail": "..."}` avec le statut que vous avez généré ; un navigateur reçoit la page d'erreur. `notfound.nexy` rend `404` et `errors.nexy` rend `500`, chacun étant limité à son répertoire. Voir [Validation et erreurs](validation-and-errors.md) et [Pages d'erreur](../errors/README.md).

## OpenAPI

Chaque route API apparaît dans le schéma généré, car les routes sont des routes simples FastAPI. Le schéma est servi à `/openapi.json` et rendu par Scalar à `/docs`. Désactivez les deux avec `useDocs = False` dans `nexyconfig.py`.

## Prochaines étapes

- [Dépendances](../dependencies/README.md) : authentification et configuration partagées par gestionnaire ou par répertoire
- [Validation et erreurs](validation-and-errors.md) : `422`, `404` et erreurs JSON
- [Routage](../../README.md) : chemin du fichier vers l'URL
- [Actions](../../../guides/actions.md) : points de terminaison avec chemins générés
- [Configuration](../../../reference/config.md) : middleware, CORS, sessions
