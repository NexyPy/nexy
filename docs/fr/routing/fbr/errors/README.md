# Pages d'erreur

Une requête qui échoue devrait quand même répondre comme le reste de votre site : une page dans vos propres mots pour un visiteur, le même échec que JSON pour un client API. Nexy répond aux deux réponses et un fichier remplace chaque réponse.

Cette page est la carte : quel fichier répond à quel statut, et comment créer votre premier. Les pages d'un dossier obtiennent [leur propre page](folder-pages.md).

## Un échec, deux réponses

```diagram filename="qui répond à une demande ayant échoué"
a request that fails
      │
      ├── a browser (Accept: text/html)              ──►  an HTML page
      └── an API client (Accept: application/json)   ──►  {"detail": "…"}  with the same status

the HTML page
      ├── the deepest folder of the URL that holds a file   ──►  your file
      └── no folder of the chain holds one                 ──►  the built-in page
```

## Votre première page

Créez `src/routes/notfound.nexy` et écrivez ce qu'un visiteur doit lire :

```nexy filename="src/routes/notfound.nexy"
---
title: Page not found
---
<h1>Page not found</h1>
<p>The page moved or never existed. <a href="/">Back home</a>.</p>
```

Enregistrez et demandez une URL que rien ne sert :

```bash
curl -i -H "Accept: text/html" http://localhost:3000/nowhere
# HTTP/1.1 404 Not Found
```

Le fichier à la racine des routes répond à l'ensemble du projet ; une copie dans un dossier ne répond qu'à ce dossier et [conserve le reste tel quel](folder-pages.md). Sans aucun fichier, Nexy sert sa page stylisée intégrée.

## Quel fichier répond

| Fichier | Réponses |
|---|---|
| `notfound.nexy` | `404` pour son répertoire |
| `errors.nexy` | `500` pour son répertoire |
| `forbidden.nexy` | `403` pour son répertoire |
| `unauthorized.nexy` | `401` pour son répertoire |
| `loading.nexy` | réservé ; pas encore d'effet d'exécution |

| Situation | Réponse |
|---|---|
| Aucun itinéraire ne correspond à | `404` |
| Un segment dynamique ne peut pas être converti en son annotation | `404` |
| Une exception non gérée, dans une page ou un gestionnaire d'API | `500` |
| `raise HTTPException(status_code=403)` | le statut que vous avez généré, au format HTML ou JSON |
| `notFound()`, `forbidden()`, `unauthorized()` | `404`, `403`, `401`, depuis n'importe où dans une requête |
| `redirect()`, `permanentRedirect()` | une vraie redirection sans page d'erreur |

## Laisser une page ou répondre à partir du code

`redirect`, `permanentRedirect`, `notFound`, `forbidden` et `unauthorized` déclenchent une exception HTTP, donc le même appel fonctionne dans une page `.nexy`, un gestionnaire d'API, un contrôleur modulaire, un garde et un `dependencies.py`. Ils portent les mêmes noms sur le client (`@nexy/client`).

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound, redirect

from src.posts import find

slug: prop[str]
post = find(slug)
if post is None:
    notFound()
if post.moved_to:
    redirect(post.moved_to)
---
<h1>{{ post.title }}</h1>
```

| Appeler | Répondre |
|---|---|
| `redirect(url)` | `307`; `redirect(url, status=303)` transforme un POST en GET après un formulaire |
| `permanentRedirect(url)` | `308` ; les navigateurs et les moteurs de recherche s'en souviennent |
| `notFound(detail=None)` | `404` : la page `notfound`, ou JSON pour un client API |
| `forbidden(detail=None)` | `403` : le visiteur est connu mais ne peut pas le voir |
| `unauthorized(detail=None, scheme=None)` | `401` ; `scheme="Bearer"` ajoute `WWW-Authenticate` |

Une redirection répond avec l'en-tête `Location` et aucune page, également vers un client API. Construisez la destination à partir de valeurs auxquelles vous faites confiance : un `redirect(request.query_params["next"])` envoie les visiteurs là où le lien l'indique. Une destination avec un saut de ligne est refusée.

Une garde protège un dossier entier :

```python filename="src/routes/private/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

## HTML ou JSON

La même exception répond différemment selon qui demande :

- Un navigateur (`Accept: text/html`) obtient une page HTML. Les détails sont échappés en HTML, donc un message construit à partir de l'entrée de l'utilisateur ne peut pas injecter de balisage.
- Un client qui demande du JSON et non une page (`Accept: application/json`) obtient `{"detail": "..."}` avec le même code d'état.

```python filename="src/routes/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    if id > 100:
        raise HTTPException(status_code=403, detail="Out of range")
    return {"id": id}
```

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!REMARQUE]
> un client qui envoie `Accept: */*` (la valeur par défaut de `curl` et de nombreuses bibliothèques HTTP) reçoit la page HTML. Définissez `Accept: application/json` pour les erreurs JSON.

## Exceptions non gérées

Une exception dont rien n'est géré est enregistrée une fois, avec l'exception, son origine et le code qui l'entoure, et répondue en fonction du mode.

| | `nx dev` | `nx start` |
|---|---|---|
| Navigateur | une page avec l'erreur, les lignes de votre code qui l'ont déclenchée et le traçage complet | la page `500` intégrée (ou votre `errors.nexy`) avec une référence |
| Client JSON | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Journal du serveur | l'exception et les lignes de votre code | l'exception et tout le traçage, avec la même référence |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

La référence est de huit caractères, nouveaux à chaque échec. Un visiteur peut le citer et vous trouvez le traçage en le recherchant dans le journal. Ni l'exception ni le code n'atteignent le visiteur en production. Un `errors.nexy` personnalisé remplace la page uniquement ; la ligne de journal reste.

## Erreurs de validation

Un en-tête, un paramètre de requête ou un champ de corps manquant répond à `422` avec le corps JSON de FastAPI, pour chaque client. Voir [Validation et erreurs](../handlers/validation-and-errors.md).

## Prochaines étapes

- [Pages d'erreur par dossier](folder-pages.md) : un 404, 403 ou 401 de votre choix dans un dossier
- [Itinéraires dynamiques](../pages/dynamic-routes.md)
- [Routes API](../handlers/README.md)
- [Tests](../../../guides/testing.md)
