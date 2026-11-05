# Exceptions et erreurs

Une demande peut échouer à quatre endroits, et Nexy répond à chacun différemment. Cette page est l'index : recherchez le statut que vous voyez, puis la ligne qui l'a produit, puis le fichier qui décide du corps.

> [!NOTE]
> Trois éléments sont distincts et faciles à confondre : la **réponse HTTP** (un statut et un corps), la **page d'erreur** (`notfound.nexy`, `errors.nexy`) et la **ligne de journal** (ce que vous lisez dans le terminal). La modification de la page ne modifie pas le statut et la personnalisation de la page ne masque pas le journal.

## La version courte

| Que s'est-il passé | Statut | Le navigateur voit | Le client API voit |
|---|---|---|---|
| aucune route ne correspond à l'URL | `404` | `notfound.nexy`, sinon la page intégrée | `{"detail": "Not Found"}` |
| un segment de chemin ne correspond pas à son annotation | `404` | la même page | `{"detail": "Not Found"}` |
| une requête, un en-tête, un cookie ou un champ de corps est manquant ou invalide | Corps JSON de `422` | FastAPI Corps JSON de | Corps JSON de FastAPI |
| `notFound()` | `404` | la page | `{"detail": ...}` |
| `unauthorized()` | `401` | la page intégrée | `{"detail": ...}` |
| `forbidden()` | `403` | la page intégrée | `{"detail": ...}` |
| `raise HTTPException(409, ...)` | `409` | la page intégrée | `{"detail": ...}` |
| une exception, rien n'a été détecté | `500` | `errors.nexy`, sinon la page intégrée | `{"detail", "reference"}` |
| `redirect(url)` | `307` | la destination, pas de page | la destination, pas de corps |
| `permanentRedirect(url)` | `308` | la destination, pas de page | la destination |

Un client API est une requête dont l'entête `Accept` demande du JSON et non une page :

```bash
curl -H "Accept: application/json" http://localhost:3000/api/items/500
# {"detail":"Out of range"}
```

> [!WARNING]
> `curl` envoie `Accept: */*` par défaut, qui récupère la page HTML. Ajoutez `-H "Accept: application/json"` lorsque vous testez la forme JSON. Les navigateurs continuent de recevoir des pages.

## D'où vient un échec

```diagram filename="Une demande, quatre sorties"
Browser ──► Middleware ──► Router ──► Page or handler
                 │            │             │
                 │            │             ├─ return ───────────► 200
                 │            │             ├─ HTTPException ────► its status
                 │            │             └─ other exception ───► 500
                 │            └─ no match ────────────────────────► 404
                 └─ raises ──────────────────────────────────────► 500
```

| Étape | Ce qui peut échouer | La réponse |
|---|---|---|
| Middleware | vos `middleware.py`, CORS, sessions | le statut de l'exception, sinon `500` |
| Routeur | l'URL ne correspond à aucun fichier | `404` |
| Validation | un segment de chemin ne peut pas être converti | `404` |
| Validation | d'une requête, d'un en-tête, d'un cookie ou d'un champ de corps | `422` |
| Page, gestionnaire, action, garde | `HTTPException` | son statut |
| Page, gestionnaire, action, garde | autre chose | `500` |

## Partez de n'importe où

`redirect`, `permanentRedirect`, `notFound`, `forbidden` et `unauthorized` déclenchent une exception HTTP, donc le même appel fonctionne dans une page `.nexy`, un gestionnaire d'API, un contrôleur modulaire, un garde, un `dependencies.py` et une action.

```python filename="src/routes/posts/[slug].py"
from nexy import notFound, redirect

from src.posts import find


async def GET(slug: str):
    post = find(slug)
    if post is None:
        notFound("No such post")
    if post.moved_to:
        redirect(post.moved_to)
    return post
```

| Appeler | Répondre | Lorsque |
|---|---|---|
| `notFound(detail=None)` | `404` | la ressource n'existe pas |
| `unauthorized(detail=None, scheme=None)` | `401` | le visiteur doit d'abord se connecter |
| `forbidden(detail=None)` | `403` | le visiteur est connu mais ne peut pas le voir |
| `redirect(url, status=307)` | `307` | les envoyer ailleurs en gardant la méthode |
| `redirect(url, status=303)` | `303` | après un formulaire : la requête suivante est un `GET` |
| `permanentRedirect(url)` | `308` | une page déplacée dont les moteurs de recherche devraient se souvenir |

Construisez la destination à partir de valeurs auxquelles vous faites confiance. `redirect(request.query_params["next"])` envoie les visiteurs là où le lien l'indique ; c'est une redirection ouverte. Une destination qui contient un saut de ligne est refusée.

## Validation : 422 ou 404

Les paramètres du gestionnaire sont validés par FastAPI par rapport à leurs annotations.

```python filename="src/routes/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| Problème | Statut | Pourquoi |
|---|---|---|
| requête, en-tête, cookie ou champ de corps manquant ou invalide | `422` | la requête a atteint le gestionnaire, les données sont erronées |
| segment de chemin invalide (`/api/users/abc` pour `id: int`) | `404` | le dossier n'a pas de route pour un non-numéro, donc l'URL n'existe pas |

Le corps de `422` est la forme standard de FastAPI, donc les clients et les SDK générés continuent de fonctionner :

```json
{"detail": [{"loc": ["query", "q"], "msg": "Field required", "type": "missing"}]}
```

Pour un formulaire ou une action, le client reçoit un `ActionError` avec `status` et `detail` ; un `422` remplit également `error.fields` avec un message par champ. Voir [Actions](../guides/actions.md#errors-and-failures).

> [!TIP]
> Validez dans la signature lorsque la règle porte sur un champ (`limit: int = 10`). Validez dans le corps lorsque la règle a besoin de la base de données ou d'un autre champ ("cet email est déjà utilisé") : relancez `HTTPException(409)` et conservez le message pour le client.

## Pages d'erreur personnalisées

```nexy filename="src/routes/notfound.nexy"
<h1>Page not found</h1>
<p>The link may be old. <a href="/">Start from the home page</a>.</p>
```

```nexy filename="src/routes/erreurs.nexy"
<h1>Something went wrong</h1>
<p>Try again in a moment.</p>
```

| Fichier | Statut | Portée |
|---|---|---|
| `src/routes/notfound.nexy` | `404` | chaque tracé du projet |
| `src/routes/errors.nexy` | `500` | chaque tracé du projet |
| `src/routes/forbidden.nexy` | `403` | chaque tracé du projet |
| `src/routes/unauthorized.nexy` | `401` | chaque tracé du projet |
| `src/routes/blog/notfound.nexy` | `404` | `/blog` et inférieurs |
| `src/routes/blog/errors.nexy` | `500` | `/blog` et inférieurs |
| `src/routes/loading.nexy` | - | réservé, aucun effet d'exécution pour le moment |

Un fichier quelque part dans les routes installe la réponse à son statut : une copie à la racine répond à l'ensemble du projet, une copie dans un dossier répond à ce dossier et le fichier le plus profond qui correspond à l'URL l'emporte. Une URL en dehors de chaque copie et un statut sans aucun fichier obtiennent les pages stylisées intégrées. Voir [Pages d'erreur par dossier](../routing/fbr/errors/folder-pages.md).

> [!IMPORTANT]
> Une page `errors.nexy` remplace la page `500` ; il n'intercepte pas l'exception et ne modifie pas la ligne de journal. Si le gestionnaire qui a généré est la page elle-même, la page ne peut pas afficher ses propres détails d'erreur : gardez `errors.nexy` simple et indépendant.

## Exceptions non gérées

Une exception qui n'a rien détecté est enregistrée une seule fois, avec sa référence, son origine et le code qui l'entoure. Le statut est `500`, et le corps dépend de l'environnement.

| | `nexy dev` | `nexy build` puis `nexy start` |
|---|---|---|
| Navigateur | l'erreur, les lignes de votre code et le traceback | `errors.nexy`, sinon la page intégrée, avec une référence |
| Client API | `{"detail", "reference", "error"}` | `{"detail", "reference"}` |
| Terminal | l'exception et les lignes de votre code | l'exception, tout le traçage et la référence |

```text
  x ZeroDivisionError: division by zero  GET /boom  ref fe6a5217
    at src/routes/boom.py:2 in GET
       1 | def GET():
       2 |     return {"a": 1 / 0}
```

La référence est de huit caractères, nouveaux à chaque échec. Un visiteur peut le citer et vous trouvez le traçage en le recherchant dans le journal. Ni l'exception ni le code n'atteignent le visiteur en production.

> [!CAUTION]
> Ne renvoyez pas le traçage à un visiteur en production, et ne mettez pas de secrets dans un message d'erreur : le `detail` d'un `HTTPException` est envoyé au client, échappé en HTML. Mettez le secret dans le journal, pas dans la réponse.

## Actions et formulaires

Une action est un point de terminaison `POST` avec un chemin généré. Ses échecs suivent les mêmes règles :

| Situation | Statut | Client |
|---|---|---|
| un champ est manquant ou invalide | `422` | `ActionError` avec `fields` |
| `HTTPException(403)` soulevée dans le cadre de l'action | `403` | `ActionError` avec `status` et `detail` |
| une exception non gérée | `500` | `ActionError` ; la référence est dans le journal du serveur |
| l'en-tête `Origin` est un autre site | `403` | refusé avant l'exécution de l'action |

Un formulaire sans JavaScript est publié dans le chemin d'action ; un succès renvoie `303` à la page, un échec affiche la page d'erreur. Voir [Actions](../guides/actions.md#forms-without-javascript).

## Une liste de contrôle lorsqu'une page répond à la mauvaise chose

1. **Regardez le statut**, pas la page. Un `notfound.nexy` personnalisé répond toujours à `404`.
2. **Lisez le terminal.** Une page dont l'importation échoue n'est pas enregistrée, donc son URL répond `404` tant que le fichier existe. L'erreur d'importation est dans le journal.
3. **Vérifiez l'extension.** Avec `useCSR = True`, les pages `.nexy` appartiennent au mode serveur ; une page dans le mauvais mode n'est pas un itinéraire.
4. **Vérifiez la profondeur.** Un `notfound.nexy` ou `errors.nexy` ne fonctionne que lorsque la copie racine existe.
5. **Demandez JSON** avec `Accept: application/json` pour voir la forme que reçoit votre client API.
6. **Citez la référence** d'un `500` lorsque vous ouvrez un problème ou effectuez une recherche dans le journal.

## Prochaines étapes

- [Pages d'erreur](../routing/fbr/errors/README.md) : le comportement de la page entière, avec des exemples
- [Validation et erreurs](../routing/fbr/handlers/validation-and-errors.md) : gestionnaires d'API
- [Dépannage](../guides/troubleshooting.md) : les erreurs que les gens rencontrent réellement
- [Testing](../guides/testing.md) : affirmer un statut et un corps
