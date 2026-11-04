# Configuration

La configuration est une classe dans `nexyconfig.py` à la racine du projet. Nexy le charge depuis le répertoire dans lequel il
arrive; un projet sans le fichier utilise les valeurs par défaut.

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
| `useHost` | `"0.0.0.0"` | adresse de liaison |
| `useSslKeyfile`, `useSslCertfile` | `None` | servent HTTPS directement |
| `useDevTools` | `True` | la barre d'outils `nexy dev` ajoute à chaque page (informations sur la page, itinéraires, erreurs, configuration) ; `False` le supprime. Jamais présent en production |
| `useWorkers` | `0` | traite `nx start` exécutions ; `0` est un par processeur sous Linux et macOS, un sous Windows |
| `useCSR` | `False` | mode de routage côté client ; `.nexy` les itinéraires sont désactivés |

## Itinéraires

| Champ | Par défaut | Signification |
|---|---|---|
| `useRouter` | `None` | une instance ou une classe `APIRouter` montée à côté des routes basées sur des fichiers ; `None` signifie basé sur un fichier uniquement |
| `excludeDirs` | `["templates", "extension", "docs"]` | répertoires ignorés lors de l'analyse des itinéraires |
| `useAliases` | `None` | importer des alias, par ex. `{"@": "src"}` (`@/components/Counter.tsx` signifie `src/components/Counter.tsx`) ; `nx new` écrit celui que vous avez choisi, et Vite et `tsconfig.json` le suivent |

## Front-end

| Champ | Valeur par défaut | Signification |
|---|---|---|
| `useFF` | `None` | fabrique de framework client : `react()`, `vue()`, `svelte()`, `solid()`, `preact()` |
| `useVite` | `True` | créer et servir des bundles clients avec Vite |
| `useMarkdownExtensions` | `[]` | extensions supplémentaires pour le rendu `.md`/`.mdx` |
| `useWatchExtensions` | `None` | extensions supplémentaires surveillées par le serveur de développement |
| `useWatchExcludePatterns` | `None` | modèles globaux que le serveur de développement ignore |

> **Bon à savoir** : `NexyConfigModel` déclare `useVite = False`; la valeur par défaut du runtime `Config` est
> `True`.

## Noms de fichiers réservés

Chaque champ ajoute des extensions à un rôle réservé. `useLayoutExtensions = ["md"]` fait `layout.md`
réservé, exactement comme `layout.nexy`.

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
| `useDocs` | `True` | servir le schéma OpenAPI et sa page de référence Scalar |
| `useDocsUrl` | `"/docs"` | chemin de la page de référence de l'API |
| `useRedocsUrl` | `"/redocs"` | déclaré mais aucune route n'est montée |
| `useTitle` | `"Nexy App"` | Titre OpenAPI et titre de la page (`"Nexy"` dans `NexyConfigModel`) |

## Middleware

| Champ | Par défaut | Signification |
|---|---|---|
| `useMiddlewares` | `[]` | Classes middleware ASGI |
| `useCORS` | `None` | kwargs pour `CORSMiddleware` |
| `useGZip` | `None` | kwargs pour `GZipMiddleware` |
| `useTrustedHost` | `None` | kwargs pour `TrustedHostMiddleware` |
| `useSession` | `None` | kwargs pour `SessionMiddleware` |
| `useAuth` | `None` | configuration du middleware d'authentification |
| `useHTTPSRedirect` | `False` | rediriger HTTP vers HTTPS |

## Marquage

| Champ | Par défaut | Signification |
|---|---|---|
| `useTocDepth` | `"2-6"` | niveaux de titres inclus dans la table des matières |
| `useTocTitle` | `"Table of Contents"` | Titre de la table des matières |
| `useTocAuto` | `True` | générer la table des matières des pages Markdown |

## Routes en dehors de l'arborescence des fichiers

Créez un FastAPI `APIRouter` et montez-le avec `useRouter`. Il est servi à côté du fichier
itinéraires :

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

## Étapes suivantes

- [i18n](../guides/i18n.md) : internationalisation
- [Frontend](../guides/frontend.md) : `useFF` et la version client
- [Déployer](../deployment/README.md) : options de production