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

## Limitation du débit

`useRateLimit` répond `429 Too Many Requests` à une adresse client qui envoie plus de `requests` requêtes dans une fenêtre de `per` secondes.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useRateLimit = {"requests": 60, "per": 60, "paths": ["/api/", "/_nx_"]}
```

Nexy garantit qu'une requête dépassant la limite obtient un `429` avec un en-tête `Retry-After`, les secondes restantes dans la fenêtre, et n'atteint jamais vos routes, actions ou middleware.

Nexy garantit que sans `useRateLimit` aucun middleware de limite de débit n'est ajouté.

Nexy garantit que les sondes `useHealth` ne sont jamais limitées.

`paths` est facultatif : sans cela, tout chemin est limité. Les actions du serveur sont servies sous `/_nx_`, de sorte que ce préfixe les limite toutes.

La fenêtre est fixe et partagée par tous les clients : les décomptes recommencent à chaque multiple de `per` secondes. Un client peut donc envoyer jusqu'à deux fois `requests` à travers le bord d'une fenêtre.

Les comptes vivent dans la mémoire de chaque travailleur. Avec `useWorkers` au-dessus de un, un client peut envoyer `requests` à chaque travailleur, et les décomptes recommencent au redémarrage du serveur.

L'adresse du client est celle qu'uvicorn donne à la demande. Derrière un proxy inverse sur la même machine, uvicorn le lit depuis `X-Forwarded-For` ; pour un proxy sur une autre machine, indiquez son adresse dans la variable d'environnement `FORWARDED_ALLOW_IPS`, ou chaque client partage l'adresse du proxy.

Votre application est responsable d'une limite partagée par plusieurs Workers ou serveurs : un proxy inverse ou un store tel que Redis.

## HTTPS

Servez HTTPS directement avec `useSslKeyfile` et `useSslCertfile`, ou terminez TLS sur un proxy inverse et définissez `useHTTPSRedirect`. En développement, le serveur de développement Vite reste sur HTTP de bouclage derrière l'origine Nexy, donc TLS ne l'atteint jamais.

## Liste de contrôle de production

- `useDocs = False` si le schéma OpenAPI ne doit pas être public.
- `useTrustedHost` défini sur vos domaines, pour bloquer les attaques d'en-tête d'hôte.
- `useCORS` avec des origines explicites, jamais `["*"]` avec des informations d'identification.
- Un vrai `secret_key` pour les sessions, lu depuis l'environnement.
- Props transmis aux composants client sont échappés en HTML par Nexy. Ne marquez pas les entrées utilisateur `| safe` dans les modèles.

## Gardes et dépendances

La protection par route utilise des dépendances FastAPI. Un `dependencies.py` dans un répertoire de routes s'applique à tout ce qui se trouve en dessous : voir [Dépendances](../routing/fbr/dependencies/README.md). Dans le routeur modulaire, utilisez [`@UseGuard`](../routing/modular/guards-and-metadata.md).

## Prochaines étapes

- [Configuration](../reference/config.md) : chaque champ middleware
- [Déployer](../deployment/README.md)
- [Performances](../deployment/performance.md)
