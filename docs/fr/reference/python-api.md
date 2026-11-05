# Python API

Chaque nom Nexy exporte vers votre code Python, par module. Un test vérifie cette page par rapport au code dans les deux sens : un nom répertorié ici doit exister et un nom que le code exporte doit être répertorié ici.

## `nexy`

Composants pour les modèles `.nexy` et les hooks de requête.

| Nom | Qu'est-ce que c'est |
|---|---|
| `Audio`, `Video` | lecteurs natifs `<audio>` et `<video>`, voir [composants](../views/nexy/components.md) |
| `Image` | un `<img>` qui se charge paresseusement par défaut |
| `Link` | un côté client `<a>` avec prélecture optionnelle |
| `Import` | importer un composant client dans une page `.nexy` |
| `Template` | rendre les modèles Jinja2 et Markdown |
| `Vite` | la balise client Vite dont chaque page a besoin |
| `Form` | un espace réservé sans comportement : utilisez un simple `<form>` avec une [action](../guides/actions.md) |
| `usePathname` | le chemin de la requête en cours |
| `useSearchParams` | la chaîne de requête sous forme de dict |
| `useParams` | les paramètres de chemin dynamique sous forme de dict, comme `useParams()` sur le client |
| `useQuery` | le nom original de `useParams`, conservé pour les pages existantes (il ne lit pas la chaîne de requête) |
| `useRequest` | la demande en cours, pour ce que les autres hooks ne couvrent pas |
| `useHeaders` | les en-têtes de requête sous forme de dict avec des noms en minuscules |
| `useUrl` | l'URL complète : `.scheme`, `.hostname`, `.path`, `.query` |
| `useIsActive` | si un lien pointe vers la page courante ou vers un de ses parents, pour une barre de navigation |
| `useRouter` | `path`, `base_url` et `url_for` de la demande en cours |
| `useSession` | le dict de session, vide lorsque les sessions sont désactivées |
| `useCookies` | la demande de cookies comme un dict |
| `useToc` | la table des matières de la page courante, au format HTML |
| `useViews` | rendre un fichier de vue tel que `about.tsx` à partir d'un gestionnaire |
| `setMetadata`, `useMetadata` | nommer les balises de titre et de tête d'une page et les écrire dans la mise en page |
| `redirect`, `permanentRedirect` | envoyer le visiteur ailleurs (307, 308) et arrêter la requête |
| `notFound`, `forbidden`, `unauthorized` | répondez au 404, 403 ou 401 de n'importe où |

Les hooks fonctionnent uniquement à l'intérieur d'une requête : voir [hooks](../routing/fbr/navigation/hooks.md).

```nexy filename="src/routes/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## `nexy.http`

Le vocabulaire HTTP d'un gestionnaire. Importez depuis ici plutôt que depuis FastAPI, vos gestionnaires dépendent donc du contrat de Nexy.

| Nom | Qu'est-ce que c'est |
|---|---|
| `Request`, `Response` | la demande entrante et une réponse sortante |
| `HTTPException` | arrêter le gestionnaire avec un statut et un `detail` |
| `status` | codes d'état nommés, tels que `status.HTTP_404_NOT_FOUND` |
| `Depends` | exécuter d'abord une fonction et transmettre son résultat |
| `Header`, `Cookie`, `Query`, `Path`, `Body` | d'où vient un paramètre |
| `Form`, `File`, `UploadFile` | champs de formulaire et téléchargements (besoin de `python-multipart`) |
| `BackgroundTasks` | travail qui s'exécute après l'envoi de la réponse |
| `JSONResponse`, `HTMLResponse`, `PlainTextResponse` | réponses avec un type de contenu fixe |
| `RedirectResponse` | une redirection HTTP |
| `redirect`, `permanentRedirect` | déclencher une redirection (307, 308) depuis une page, un gestionnaire, un contrôleur ou un garde |
| `notFound`, `forbidden`, `unauthorized` | lever un 404, 403 ou 401 aux mêmes endroits |
| `FileResponse`, `StreamingResponse` | répondre avec un fichier ou un stream |

```python filename="src/routes/api/items/[id].py"
from nexy.http import Depends, Header, HTTPException, status


def api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad key")
    return x_api_key


async def GET(id: int, key: str = Depends(api_key)):
    return {"id": id}
```

## `nexy.decorators`

| Nom | Qu'est-ce que c'est |
|---|---|
| `Action` | transformer une fonction en un point de terminaison `POST`, voir [actions](../guides/actions.md) |
| `revalidate` | indiquer au navigateur quelles pages une action a rendues obsolètes |
| `Module`, `Controller` | déclarer un module et un contrôleur dans le [routeur modulaire](../routing/modular/README.md) |
| `Injectable`, `Container`, `Scope` | [injection de dépendances](../routing/modular/dependency-injection.md) et ses durées de vie |
| `UseGuard`, `Middleware` | garder ou envelopper un gestionnaire, voir [gardes](../routing/modular/guards-and-metadata.md) |
| `UseRoute`, `useRoute`, `RouteMeta` | nommer un itinéraire et le décrire pour OpenAPI |
| `UseResponse`, `ResponseMeta` | décrire la réponse d'un itinéraire |
| `HTTP_METHODS` | les méthodes HTTP qu'un fichier de gestionnaire peut définir |
| `ACTIONS_STORE` | le registre des actions, pour les outillages et les tests |

```python filename="src/actions/posts.py"
from nexy.decorators import Action, revalidate


@Action
async def publish(post_id: int) -> bool:
    revalidate("/blog")
    return True
```

## `nexy.testing`

| Nom | Qu'est-ce que c'est |
|---|---|
| `render` | le HTML d'un composant `.nexy` pour des accessoires donnés, sans serveur, voir [tests](../guides/testing.md) |

```python filename="tests/test_button.py"
from nexy.testing import render


def test_the_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

## Où ensuite

- [Configuration](config.md) : les champs `use*` derrière ces noms
- [Exceptions et erreurs](exceptions.md) : à quoi répond chaque échec
- [Index de la documentation](../README.md) : la page de ce que vous construisez
