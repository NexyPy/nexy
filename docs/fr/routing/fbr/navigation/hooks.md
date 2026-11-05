# Crochets

Les hooks lisent la requête HTTP actuelle depuis une page `.nexy`, un gestionnaire d'API ou un contrôleur modulaire. Leurs noms correspondent aux hooks du routeur client (`@nexy/client`) où ils font la même chose.

> [!REMARQUE]
> les hooks ne fonctionnent que pendant qu’une demande est en cours de traitement. En appeler un ailleurs génère `RuntimeError`.

## Les crochets

| Crochet | Renvoie |
|---|---|
| `usePathname()` | chemin de requête, par ex. `"/blog/post-1"` |
| `useSearchParams()` | chaîne de requête sous la forme `dict[str, str]`, première valeur par clé |
| `useParams()` | paramètres de chemin dynamique, par ex. `{"slug": "post-1"}` |
| `useQuery()` | le nom original de `useParams()`, conservé pour les pages existantes |
| `useRequest()` | la demande Starlette, pour ce que les autres hooks ne couvrent pas |
| `useHeaders()` | les en-têtes de requête comme `dict[str, str]`, les noms en minuscules |
| `useUrl()` | l'URL complète : `.scheme`, `.hostname`, `.port`, `.path`, `.query` |
| `useIsActive(href, exact=False)` | si `href` est la page actuelle ou l'un de ses parents |
| `useRouter()` | `{"path", "base_url", "url_for"}` |
| `useCookies()` | tous les cookies comme `dict[str, str]` |
| `useSession()` | le dict de session, `{}` lorsque les sessions ne sont pas activées |
| `useToc(depth_range="2-6")` | table des matières HTML de la page actuelle, `""` lorsqu'il n'y en a pas |
| `useViews(path, context=None)` | rend une autre vue et renvoie un `HTMLResponse` |

## Lire la demande

```nexy filename="src/routes/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## Un lien actif dans une barre de navigation

`useIsActive` suit la même règle que sur le client : la chaîne de requête, le fragment et une barre oblique finale sont ignorés, un lien vers un parent est actif sur ses enfants sauf si `exact` est défini, et `/` n'est actif que sur `/`.

```nexy filename="src/components/NavLink.nexy"
---
from nexy import useIsActive

href: prop[str]
label: prop[str]
---
<a href="{{ href }}"{% if useIsActive(href) %} aria-current="page"{% endif %}>{{ label }}</a>
```

## Remarques

- `useQuery()` renvoie les paramètres **path**, pas la chaîne de requête, c'est pourquoi `useParams()` existe. La chaîne de requête est `useSearchParams()`.
- `useRouter()` voici le hook de requête. Ce n'est pas le champ de configuration `useRouter` qui monte un `APIRouter`.
- `useSession()` a besoin de `useSession = {...}` dans `nexyconfig.py` ; sans cela, le dict est vide.
- `useViews("about.tsx", {"title": "About"})` renvoie HTML : une vue `.nexy` est rendue par son module compilé, une vue `.tsx`/`.jsx`/`.vue`/`.svelte`/`.mdx` devient un conteneur de montage client.

## Prochaines étapes

- [Pages](../pages/README.md) : segments et mises en page dynamiques
- [Recettes](../../../guides/recipes.md) : un flux de connexion testé basé sur `useSession()`
- [Config](../../../reference/config.md) : activer les sessions et les paramètres régionaux
- [fichiers .nexy](../../../views/nexy/README.md) : où les hooks sont généralement appelés
