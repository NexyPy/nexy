# Middleware et sécurité

Nexy fonctionne sur FastAPI et Starlette, leur middleware s'applique donc. Les plus courants sont une ligne dans `nexyconfig.py`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {
        "allow_origins": ["https://app.example.com"],
        "allow_methods": ["GET", "POST"],
        "allow_credentials": True,
    }
    useGZip = {"minimum_size": 1000}
    useTrustedHost = {"allowed_hosts": ["example.com", "*.example.com"]}
    useHTTPSRedirect = True
    useSession = {"secret_key": "change-me"}
```

Chaque dictionnaire `use*` est transmis sous forme d'arguments de mot-clé au middleware Starlette correspondant : `CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `SessionMiddleware`.

## Votre propre middleware

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` suit des cours de middleware ASGI.

## HTTPS

Servez HTTPS directement avec `useSslKeyfile` et `useSslCertfile`, ou terminez TLS sur un proxy inverse et définissez `useHTTPSRedirect`. En développement, le serveur de développement Vite reste sur HTTP de bouclage derrière l'origine Nexy, donc TLS ne l'atteint jamais.

## Liste de contrôle de production

- `useDocs = False` si le schéma OpenAPI ne doit pas être public.
- `useTrustedHost` défini sur vos domaines, pour bloquer les attaques d'en-tête d'hôte.
- `useCORS` avec des origines explicites, jamais `["*"]` avec des informations d'identification.
- Un vrai `secret_key` pour les sessions, lu depuis l'environnement.
- Les accessoires transmis aux composants clients sont échappés en HTML par Nexy. Ne marquez pas les entrées utilisateur `| safe` dans les modèles.

## Gardes et dépendances

La protection par route utilise des dépendances FastAPI. Un `dependencies.py` dans un répertoire de routes s'applique à tout ce qui se trouve en dessous : voir [Dépendances](../routing/fbr/dependencies/README.md). Dans le routeur modulaire, utilisez [`@UseGuard`](../routing/modular/guards-and-metadata.md).

## Prochaines étapes

- [Configuration](../reference/config.md) : chaque champ middleware
- [Déployer](../deployment/README.md)
- [Performances](../deployment/performance.md)
