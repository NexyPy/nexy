# Configuration

La configuration est une classe dans `nexyconfig.py` à la racine du projet. Nexy le charge à partir du répertoire dans lequel il s'exécute ; un projet sans le fichier utilise les valeurs par défaut.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    usePort = 3000
    useTitle = "My App"
    useAliases = {"@": "src"}
```

## Serveur

| Champ | Par défaut | Signification |
|---|---|---|
| `usePort` | `3000` | port pour `dev` et `start` |
| `useHost` | `"0.0.0.0"` | lier l'adresse |
| `useSslKeyfile`, `useSslCertfile` | `None` | servir HTTPS directement |
| `useDevTools` | `True` | la barre d'outils `nexy dev` ajoute à chaque page (informations sur la page, itinéraires, erreurs, configuration) ; `False` le supprime. Jamais présent en production |
| `useHealth` | `False` | servir `GET /health/live` et `GET /health/ready` pour les équilibreurs de charge et les sondes Kubernetes ; voir [Déployer](../deployment/README.md#built-in-endpoints) |
| `useMaxBodySize` | `1048576` | le plus grand corps de requête lu par un travailleur, en octets (1 Mio) ; un plus grand est un `413`, et `0` désactive la limite. Élevez-le pour un itinéraire qui prend en charge les téléchargements de fichiers |
| `useSiteUrl` | `None` | l'origine publique du site, telle que `"https://example.com"` ; une fois réglé, Nexy sert `/sitemap.xml` et `/robots.txt`. Voir [Plan du site et robots.txt](../guides/sitemap.md) |
| `useWorkers` | `0` | traite `nx start` exécutions ; `0` est un par processeur sous Linux et macOS, un sous Windows |
| `useCSR` | `False` | mode de routage côté client ; `.nexy` les itinéraires sont désactivés |
| `useBasePath` | `None` | préfixe public pour l'ensemble de l'application, tel que `"/app"` ; les requêtes en dehors de celui-ci répondent 404, et les liens générés, les itinéraires clients, les appels à l'action et les actifs portent le préfixe. Voir [Déployer](../deployment/README.md#serve-under-a-sub-path) |
| `useImageWidths` | `[320, 640, 960, 1280]` | les largeurs de pixels `nx build` génèrent pour les images locales ; la conversion nécessite `Pillow`, et sans cela, les images conservent leur URL d'origine. Voir [Image](../routing/fbr/navigation/linking-and-navigating.md#image) |

## Base de données

| Champ | Par défaut | Signification |
|---|---|---|
| `useORM` | `None` | l'ORM du projet : `"SQLModel"`, `"SQLAlchemy"` ou `"Tortoise-ORM"`. `nx new` l'écrit et `nx migrate` en choisit Alembic ou Aerich ; sans cela, `nx migrate` prend le premier ORM installé. Voir [Bases de données](../guides/databases.md#migrations) |

## Itinéraires

| Champ | Par défaut | Signification |
|---|---|---|
| `useRouter` | `None` | une instance ou une classe `APIRouter` montée à côté des routes basées sur des fichiers ; `None` signifie basé sur un fichier uniquement |
| `excludeDirs` | `["templates", "extension", "docs"]` | répertoires ignorés lors de l'analyse des itinéraires |
| `useAliases` | `None` | importer des alias, par ex. `{"@": "src"}` (`@/components/Counter.tsx` signifie `src/components/Counter.tsx`) ; `nx new` écrit celui que vous avez choisi, et Vite et `tsconfig.json` le suivent |

## Front-end

| Champ | Par défaut | Signification |
|---|---|---|
| `useFF` | `None` | fabrique de framework client : `react()`, `vue()`, `svelte()`, `solid()`, `preact()` |
| `useVite` | `True` | créer et servir des bundles clients avec Vite |
| `useMarkdownExtensions` | `[]` | extensions supplémentaires pour le rendu `.md`/`.mdx` |
| `useWatchExtensions` | `None` | extensions supplémentaires surveillées par le serveur de développement |
| `useWatchExcludePatterns` | `None` | modèles globaux que le serveur de développement ignore |

> **Bon à savoir** : `NexyConfigModel` déclare `useVite = False` ; la valeur par défaut du runtime `Config` est `True`.

## Noms de fichiers réservés

Chaque champ ajoute des extensions à un rôle réservé. `useLayoutExtensions = ["md"]` rend `layout.md` réservé, exactement comme `layout.nexy`.

| Champ | Ajoute des extensions à |
|---|---|
| `useLayoutExtensions` | `layout.*` |
| `useNotFoundExtensions` | `notfound.*` |
| `useErrorsExtensions` | `errors.*` |
| `useForbiddenExtensions` | `forbidden.*` |
| `useUnauthorizedExtensions` | `unauthorized.*` |
| `useLoadingExtensions` | `loading.*` |

## Documentation API

| Champ | Par défaut | Signification |
|---|---|---|
| `useDocs` | `"dev"` | où la page de référence Scalar et `/openapi.json` sont servis : `"dev"` sur `nx dev` uniquement, `True` en production également (le schéma répertorie chaque route et action du serveur), `False` nulle part |
| `useDocsUrl` | `"/docs"` | chemin de la page de référence de l'API |
| `useRedocsUrl` | `"/redocs"` | déclaré mais aucune route n'est montée |
| `useTitle` | `"Nexy App"` | Titre de OpenAPI et titre de la page (`"Nexy"` dans `NexyConfigModel`) |

### `/docs` gratuit pour une page du projet

La référence API répond à `/docs` avant toute route, donc `src/routes/docs.nexy` ou `src/routes/docs/[[...slug]].nexy` n'y sont jamais servis. `nx dev` et `nx start` nomment une telle page au démarrage. Déplacez la référence avec `useDocsUrl` :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useDocsUrl = "/api-reference"
```

Ou désactivez-le avec `useDocs = False`, qui arrête également de diffuser `/openapi.json`. Pendant que la référence est activée, gardez les itinéraires du projet hors de ce chemin.

## Intergiciel

| Champ | Par défaut | Signification |
|---|---|---|
| `useMiddlewares` | `[]` | Classes de middleware ASGI |
| `useCORS` | `None` | kwargs pour `CORSMiddleware` |
| `useGZip` | `None` | kwargs pour `GZipMiddleware` |
| `useTrustedHost` | `None` | kwargs pour `TrustedHostMiddleware` |
| `useSession` | `None` | kwargs pour `SessionMiddleware` |
| `useAuth` | `None` | configuration du middleware d'authentification |
| `useHTTPSRedirect` | `False` | rediriger HTTP vers HTTPS |
| `useRateLimit` | `None` | les requêtes qu'une adresse client peut envoyer par fenêtre, telles que `{"requests": 60, "per": 60}` ; un de plus est un `429` avec `Retry-After`, et `"paths": ["/api/"]` limite uniquement ces préfixes. Chaque travailleur compte pour lui-même. Voir [Limitation de débit](../guides/middleware-and-security.md#rate-limiting) |

## Markdown

| Champ | Par défaut | Signification |
|---|---|---|
| `useTocDepth` | `"2-6"` | niveaux de titres inclus dans la table des matières |
| `useTocTitle` | `"Table of Contents"` | Titre de la table des matières |
| `useTocAuto` | `True` | générer la table des matières pour Markdown pages |

## Itinéraires en dehors de l’arborescence des fichiers

Construisez un FastAPI `APIRouter` et montez-le avec `useRouter`. Il est servi à côté des routes basées sur des fichiers :

```python filename="nexyconfig.py"
from fastapi import APIRouter
from nexy.core.models import NexyConfigModel

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


class NexyConfig(NexyConfigModel):
    useRouter = router
```

Les valeurs par défaut ci-dessus sont lues à partir de `nexy/core/config.py`.

## Déclaré, pas encore lu

Ces champs existent dans `NexyConfigModel` mais aucun code ne les consomme. Leur définition n'a aucun effet :

`useViteDevUrl`, `useRTL`.

## Prochaines étapes

- [i18n](../guides/i18n.md) : internationalisation
- [Frontend](../guides/frontend.md) : `useFF` et la version client
- [Déployer](../deployment/README.md) : options de production
