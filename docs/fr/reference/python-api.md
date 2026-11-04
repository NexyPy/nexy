# API Python

Chaque nom Nexy exporte vers votre code Python, par module. Un test vérifie cette page par rapport au code dans
dans les deux sens : un nom répertorié ici doit exister et un nom que le code exporte doit être répertorié ici.

## `nexy`

Composants pour les modèles `.nexy` et les hooks de requête.

| Nom | Qu'est-ce que c'est |
|---|---|
| `Audio`, `Video` | lecteurs natifs `<audio>` et `<video>`, voir [composants](../views/nexy/components.md) |
| `Image` | et `<img>` qui se charge paresseusement par défaut |
| `Link` | un côté client `<a>` avec prélecture facultative |
| `Import` | importer un composant client dans une page `.nexy` |
| `Template` | rendre les modèles Jinja2 et Markdown |
| `Vite` | la balise client Vite dont chaque page a besoin |
| `Form` | un espace réservé sans comportement : utilisez un simple `<form>` avec une [action](../guides/actions.md) |
| `usePathname` | le chemin de la requête en cours |
| `useSearchParams` | la chaîne de requête sous forme de dict |
| `useParams` | les paramètres du chemin dynamique sous forme de dict, comme `useParams()` sur le client |
| `useQuery` | le nom original de `useParams`, conservé pour les pages existantes (il ne lit pas la chaîne de requête) |
| `useRequest` | la demande actuelle, pour ce que les autres hooks ne couvrent pas |
| `useHeaders` | les en-têtes de requête sous forme de dict avec des noms en minuscules |
| `useUrl` | l'URL complète : `.scheme`, `.hostname`, `.path`, `.query` |
| `useIsActive` | si un lien pointe vers la page courante ou vers l'un de ses parents, pour une barre de navigation |
| `useRouter` | `path`, `base_url` et `url_for` de la demande en cours |
| `useSession` | le dict de session, vide lorsque les sessions sont désactivées |
| `useCookies` | la demande de cookies comme un dict |
| `useToc` | la table des matières de la page courante, au format HTML |
| `useViews` | restitue un fichier de vue tel que `about.tsx` à partir d'un gestionnaire |
| `setMetadata`, `useMetadata` | nommer les balises de titre et de tête d'une page et les écrire dans la mise en page |
| `redirect`, `permanentRedirect` | envoyer le visiteur ailleurs (307, 308) et arrêter la requête |
| `notFound`, `forbidden`, `unauthorized` | répondez au 404, 403 ou 401 de n'importe où |

Les hooks fonctionnent uniquement à l'intérieur d'une requête : voir [hooks](../routing/fbr/navigation/hooks.md).

## `nexy.http`

Le vocabulaire HTTP d'un gestionnaire. Importez depuis ici plutôt que depuis FastAPI, vos gestionnaires dépendent donc
sur le contrat de Nexy.

| Nom | Qu'est-ce que c'est |
|---|---|
| `Request`, `Response` | la requête entrante et une réponse sortante |
| `HTTPException` | arrêter le gestionnaire avec un statut et un `detail` |
| `status` | codes d'état nommés, tels que `status.HTTP_404_NOT_FOUND` |
| `Depends` | exécutez d'abord une fonction et transmettez son résultat dans |
| `Header`, `Cookie`, `Query`, `Path`, `Body` | où un paramètre provient de |
| `Form`, `File`, `UploadFile` | champs de formulaire et téléchargements (besoin de `python-multipart`) |
| `BackgroundTasks` | travail qui s'exécute après l'envoi de la réponse |
| `JSONResponse`, `HTMLResponse`, `PlainTextResponse` | réponses avec un type de contenu fixe |
| `RedirectResponse` | une redirection HTTP |
| `redirect`, `permanentRedirect` | déclenchent une redirection (307, 308) depuis une page, un gestionnaire, un contrôleur ou un garde |
| `notFound`, `forbidden`, `unauthorized` | relancer un 404, 403 ou 401 aux mêmes endroits |
| `FileResponse`, `StreamingResponse` | répondent avec un fichier ou un flux |

## `nexy.decorators`

| Nom | Qu'est-ce que c'est |
|---|---|
| `Action` | transformer une fonction en un point de terminaison `POST`, voir [actions](../guides/actions.md) |
| `revalidate` | indique au navigateur quelles pages une action a rendues obsolètes |
| `Module`, `Controller` | déclarent un module et un contrôleur dans le [routeur modulaire](../routing/modular/README.md) |
| `Injectable`, `Container`, `Scope` | [injection de dépendances](../routing/modular/dependency-injection.md) et ses durées de vie |
| `UseGuard`, `Middleware` | gardent ou enveloppent un gestionnaire, voir [gardes](../routing/modular/guards-and-metadata.md) |
| `UseRoute`, `useRoute`, `RouteMeta` | nommer une route et la décrire pour OpenAPI |
| `UseResponse`, `ResponseMeta` | décrire la réponse d'un itinéraire |
| `HTTP_METHODS` | les méthodes HTTP qu'un fichier de gestionnaire peut définir |
| `ACTIONS_STORE` | le registre des actions, pour les outillages et les tests |

## `nexy.testing`

| Nom | Qu'est-ce que c'est |
|---|---|
| `render` | le HTML d'un composant `.nexy` pour des accessoires donnés, sans serveur, voir [testing](../guides/testing.md) |

## Où ensuite

- [Config](config.md) : les champs `use*` derrière ces noms
- [Exceptions et erreurs](exceptions.md) : à quoi répond chaque échec
- [Index de la documentation](../README.md) : la page de ce que vous construisez