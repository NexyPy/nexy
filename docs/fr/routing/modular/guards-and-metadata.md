# Gardes et métadonnées

Décorateurs qui protègent une route et la décrivent dans le schéma OpenAPI.

## Gardes

`@UseGuard(*guards)` fonctionne sur un contrôleur (chaque méthode) ou sur une méthode. Chaque garde est ajouté en tant que
FastAPI `Depends`, il déclare donc les paramètres dont il a besoin et déclenche pour rejeter l'appel :

```python filename="src/apps/admin/admin_controller.py"
from fastapi import Header, HTTPException
from nexy.decorators import Controller, UseGuard


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller(prefix="/admin")
@UseGuard(require_token)
class AdminController:
    async def get(self) -> dict:
        return {"ok": True}
```

## Décorateur middleware

`@Middleware(*middlewares)` se comporte de la même manière : ce sont des dépendances FastAPI, pas ASGI
middleware. Pour un véritable middleware ASGI, utilisez `useMiddlewares` dans
[Config](../../reference/config.md) ou [Middleware et sécurité](../../guides/middleware-and-security.md).

## Métadonnées de l'itinéraire

`@UseRoute(...)` définit les métadonnées OpenAPI. Cela ne change pas le chemin.

| Argument | Signification |
|---|---|
| `name` | nom de l'itinéraire |
| `tags` | Balises OpenAPI |
| `summary`, `description` | texte dans la référence API |
| `deprecated` | marque l'opération comme obsolète |
| `include_in_schema` | masquer la route du schéma |
| `operation_id` | identifiant d'opération explicite |
| `openapi_extra` | champs OpenAPI supplémentaires |

## Réponses

`@UseResponse(...)` définit `status_code`, `response_class`, `response_model`, `responses` et le
options de sérialisation.

```python
from nexy.decorators import Controller, UseResponse, UseRoute


@Controller(prefix="/users")
class UserController:
    @UseRoute(summary="List users", tags=["users"])
    @UseResponse(status_code=200)
    async def get(self) -> list[dict]:
        return []
```

La référence API générée est servie à `/docs` sauf si `useDocs = False`.

## Prochaines étapes

- [Injection de dépendances](dependency-injection.md)
- [API routes](../fbr/handlers/README.md) : les mêmes options pour les gestionnaires basés sur des fichiers