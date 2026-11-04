# Fichiers middleware

Un `middleware.py` dans un répertoire routes encapsule les requêtes traitées par ce répertoire. Comme les mises en page et
`dependencies.py`, les fichiers s'empilent depuis la racine vers le bas, le plus à l'extérieur en premier.

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request
from nexy.http import JSONResponse


async def middleware(request: Request, call_next):
    if request.headers.get("authorization") != "Bearer secret":
        return JSONResponse({"detail": "login required"}, status_code=401)
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

La fonction est `async def middleware(request, call_next)` : la signature de FastAPI
`@app.middleware("http")`. Appelez `await call_next(request)` pour continuer vers l'itinéraire, ou renvoyez un
réponse pour s'arrêter là. Le code après l'appel s'exécute à la sortie et peut modifier la réponse.

## Ce qu'il enveloppe

Un middleware s'applique aux **routes dont le fichier est dans son répertoire** ou inférieur, aux pages et API
gestionnaires, les groupes d'itinéraires inclus :

```text
src/routes/
├─ middleware.py             every route
├─ open.py                   root only
├─ admin/
│  ├─ middleware.py          /admin and everything below
│  └─ users/
│     ├─ middleware.py       /admin/users and below
│     └─ index.py            root > admin > users
└─ (shop)/
   ├─ middleware.py          only the routes in this group
   └─ cart.py                root > shop     (URL: /cart)
```

Pour une requête à `/admin/users` l'ordre est `root`, `admin`, `users`, puis l'itinéraire. Un groupe n'a pas
URL qui lui est propre, elle est donc mise en correspondance via l'itinéraire qui sert la demande, et non via l'URL.

Une URL qui ne correspond à aucune route (un 404) ne reçoit que le middleware des répertoires qui ne sont pas des groupes,
sélectionné par préfixe d'URL. `[slug]` correspond à un segment et `[...rest]` correspond au reste.

## Ce qu'il n'enveloppe pas

- URL du framework et des actifs : `/__nexy__/`, `/_nexy/`, `/public/`, `/assets/` et `/@...` (Vite).
- Gestionnaires WebSocket et durée de vie du serveur : uniquement les requêtes HTTP.
- Fichiers dans les répertoires commençant par `_` ou `.`.

## Middleware, dépendances ou gardes

| Utiliser | Lorsque |
|---|---|
| `middleware.py` | vous avez également besoin de la **réponse** : en-têtes, redirections, timing, court-circuit pour toute une zone |
| [`dependencies.py`](../dependencies/README.md) | vous avez besoin de paramètres analysés ou d'injecter une valeur (utilisateur actuel, session de base de données) |
| `@UseGuard` sur un gestionnaire | une route nécessite une vérification supplémentaire |
| `useMiddlewares` dans [config](../../../reference/config.md) | un middleware ASGI pour l'ensemble de l'application (CORS, GZip, sessions) |

Les fichiers middleware exécutent des dépendances **avant** : la requête a réussi chaque `middleware.py` de ses
répertoires lorsque les dépendances démarrent.

## Règles

- Le fichier doit définir `async def middleware(request, call_next)`. Sinon Nexy s'arrête au démarrage et
  nomme le fichier.
- C'est un module Python normal : importez ce dont vous avez besoin. Il est chargé une fois, au démarrage du serveur.
- Ce n'est jamais un itinéraire : `/middleware` est une 404.
- Vérification du chemin de base sur `request.scope["path"]`, jamais sur `request.url.path` ou sur l'en-tête `Host` : depuis
  CVE-2026-48710, l'objet URL peut être en désaccord avec le chemin reçu par le serveur. Voir
  [Sécurité](../../../reference/security.md).

## Coût

Un projet sans aucun `middleware.py` ne rapporte rien : la couche n'est pas installée. Avec des fichiers, chacun
le middleware correspondant ajoute une Starlette `BaseHTTPMiddleware` ; gardez-les petits.

## Prochaines étapes

- [Héritage](../inheritance.md)
- [Dépendances](../dependencies/README.md)
- [Middleware et sécurité](../../../guides/middleware-and-security.md)