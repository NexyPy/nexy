# SSR (rendu serveur)

## Définition

SSR est la valeur par défaut : le serveur restitue la page au format HTML pour chaque requête. Rien ne l'active, et aucun indicateur ne le désactive - un projet en mode serveur s'affiche à chaque requête à moins qu'une page ne déclare `revalidate`.

## Comment ça marche

<!-- router:fbr,custom -->
| Fichier d'itinéraire | Qu'est-ce qui produit le HTML | Quand |
|---|---|---|
| `.nexy` | le module Python compilé, via Jinja2 | chaque demande |
| `.md` | Markdown, puis la mise en page la plus proche | chaque demande |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | le framework, rendu dans Node | à la construction lorsque la route n'a pas de tracé, sinon dans le navigateur |
| `.py` | rien : il renvoie du JSON ou un `Response` | - |

Une page Markdown et un gestionnaire, côte à côte dans le même projet :

```md filename="src/routes/changelog.md"
# Changelog

Rendered to HTML on every request, then wrapped in the nearest layout.
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

Une route de composants est le seul cas qui nécessite une deuxième phrase. En production, un composant route **sans** une mise en page est servi avec le HTML produit lors de la construction, et le composant l'hydrate. Avec une mise en page, ou en développement, le conteneur est vide et le composant s'affiche dans le navigateur - la page est alors un shell qui se remplit tout seul.

Le composant route du tableau, sans mise en page, donc la production sert son HTML dès le build :

```tsx filename="src/routes/pricing.tsx"
export default function Pricing() {
  return <h1>Pricing</h1>;
}
```
<!-- /router -->

<!-- router:modular -->
| Un contrôleur revient | Qu'est-ce qui produit le HTML | Quand |
|---|---|---|
| `useViews("....nexy")` | le module Python compilé, via Jinja2 | chaque demande |
| un `dict`, une liste, un modèle | rien : FastAPI répond à JSON | - |

Une vue et un point de terminaison JSON, côte à côte dans le même module :

```nexy filename="src/apps/changelog_view.nexy"
<h1>Changelog</h1>
<p>Rendered to HTML on every request.</p>
```

```python filename="src/apps/site_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/changelog")
class ChangelogController:
    async def get(self):
        return useViews("src/apps/changelog_view.nexy")


@Controller("/api/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```
<!-- /router -->

## Cycle de vie du rendu

<!-- router:fbr,custom -->
1. La requête atteint le routeur basé sur des fichiers. Le chemin correspond et les segments dynamiques sont convertis en types déclarés par le composant.

   ```nexy filename="src/routes/orders/[id].nexy"
   ---
   identifiant : prop[int]
   ---
   <h1>Commande n°{{ id + 1000 }}</h1>
   ```

   `/orders/42` rend `Order #1042`; `/orders/abc` répond à `404`.
2. Le composant s'exécute. Celui qui attend sur Node - un document client - s'exécute dans un pool de threads, afin de ne pas bloquer la boucle d'événements.
3. Le corps est diffusé sous la forme `text/html`. Un composant qui génère des morceaux les diffuse au fur et à mesure qu'il les crée.
4. Le navigateur reçoit du HTML. Les îles s'hydratent conformément à leur [directive](islands.md).

Une erreur générée lors du rendu est transformée en page par `errors.nexy` lorsque le projet en possède une : voir [pages d'erreur](../routing/fbr/errors/README.md).
<!-- /router -->

<!-- router:modular -->
1. La demande parvient au contrôleur. Ses paramètres de chemin sont convertis en types déclarés par la méthode et transmis à la vue :

   ```python filename="src/apps/order_controller.py"
   à partir de nexy.decorators import Controller
   à partir de nexy.hooks, importez useViews


   @Controller("/commandes/{id}")
   classe OrderController :
       async def get(self, id:int):
           return useViews("src/apps/order_view.nexy", context={"id": id})
   ```

   ```nexy filename="src/apps/order_view.nexy"
   ---
   identifiant : prop[int]
   ---
   <h1>Commande n°{{ id + 1000 }}</h1>
   ```

   `/orders/42/` rend `Order #1042`; `/orders/abc/` répond à `404`.
2. La vue s'exécute et `useViews` renvoie son HTML comme réponse.
3. Le navigateur reçoit du HTML. Les îles s'hydratent conformément à leur [directive](islands.md).

Une erreur générée lors du rendu reçoit une réponse avec la page d'erreur par défaut.
<!-- /router -->

## Quand utiliser

- La page montre quelque chose que le lecteur possède : une session, un compte, un panier.
- Les données doivent être récentes à chaque chargement.
- Le contenu doit être au format HTML pour les robots d'exploration qui n'exécutent pas JavaScript.
- Le rendu de la page est peu coûteux : une requête, un modèle.

Le premier cas, une page qui accueille le lecteur de la session. `useSession` lit la session de `useSession` dans `nexyconfig.py`, sans laquelle il échoue :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/compte.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/account_view.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

## Configuration

<!-- router:fbr,custom -->
Aucun. Deux issues, et elles n’ont pas le même grain :

| Quitter la RSS pour | Fais ceci | Céréales |
|---|---|---|
| une page, avec un cache | `revalidate = 60` dans son contenu → [ISR](isr.md) | page |
| l'ensemble du projet, acheminé par le client | `useCSR = True` dans `nexyconfig.py` → [RSE](csr.md) | projet |

Le commutateur à l'échelle du projet, dans `nexyconfig.py`. Le mode client nécessite un framework client :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```
<!-- /router -->

<!-- router:modular -->
Aucun. Chaque vue renvoyée par un contrôleur est rendue à chaque requête : [ISR](isr.md) et [CSR](csr.md) sont des modes du routeur basé sur les fichiers.
<!-- /router -->

## Exemple

<!-- router:fbr,custom -->
```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` exécute ce modèle une fois, avec `slug` défini sur `hello`. Une seconde requête le relance : rien n'est conservé entre les deux. La chaîne de requête n'est pas un accessoire - lisez-la avec les hooks dans [navigation](../routing/fbr/navigation/hooks.md).
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/blog_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/post_view.nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello/` exécute cette vue une fois, avec `slug` défini sur `hello`. Une seconde requête le relance : rien n'est conservé entre les deux. La chaîne de requête n'est pas un accessoire - lisez-la avec `useSearchParams`.
<!-- /router -->

## Limites

- **Un rendu par requête.** Deux visiteurs dans la même seconde paient chacun pour le rendu et pour les requêtes qui le sous-tendent.
- **Pas de cache.** Il n'y a pas de cache de réponses partagé à réchauffer : avec les routes de fichiers, [ISR](isr.md) en ajoute un, par URL.
- **Le streaming n'aide qu'un composant qui produit.** Une requête lente en haut de la page retarde toujours le premier octet.
- **Pas de sortie statique.** En mode serveur, rien n'est figé à la construction : il n'y a pas de mode SSG, ni de commande d'exportation. Voir [Rendu](README.md).
- **L'échappement automatique est désactivé** dans les modèles `.nexy`. Échappez aux valeurs non fiables avec `| e`.

<!-- router:fbr,custom -->
```nexy filename="src/routes/search.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/search_view.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

## Prochaines étapes

<!-- router:fbr,custom -->
- [ISR](isr.md) : met en cache cette page par URL
<!-- /router -->
- [Îles](islands.md) : conservez SSR et rendez un widget interactif
<!-- router:fbr,custom -->
- [CSR](csr.md) : navigation manuelle vers le navigateur
<!-- /router -->
- [Performances](../deployment/performance.md)
