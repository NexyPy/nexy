# Pages d'erreur par dossier

Un dossier peut répondre à ses propres erreurs : un blog avec un 404 dans ses propres mots, un espace privé qui propose le formulaire de connexion au lieu d'un simple `401`. Le reste du site conserve la page qu'il possédait déjà.

Cette page ajoute un de ces fichiers et affiche la réponse.

## La règle

**Le fichier le plus profond qui correspond aux réponses de l'URL.** Tout le reste reste tel quel : les mêmes codes d'état, JSON pour un client API et la page intégrée une fois qu'aucun dossier de la chaîne ne contient de fichier.

![Les portées d'une page d'erreur](../../../assets/error-page-scopes.svg)

Car `/blog/2024/hello` Nexy monte dans l'arbre : `/blog/2024`, puis `/blog`, puis `/`. Le premier dossier contenant un fichier répond. Un dossier correspond dans son intégralité : `/blogger/hello` n'est pas sous `/blog`, donc une copie dans `blog/` n'y répond jamais.

## Les quatre fichiers

| Fichier | Réponses | Ce qui l'atteint |
|---|---|---|
| `notfound.nexy` | `404` | une URL à laquelle aucune route ne correspond, `notFound()` |
| `errors.nexy` | `500` | une exception rien n'est géré |
| `forbidden.nexy` | `403` | `forbidden()`, `raise HTTPException(403)` |
| `unauthorized.nexy` | `401` | `unauthorized()`, `raise HTTPException(401)` |

`loading.nexy` reste réservé : il n'a pas encore d'effet d'exécution.

Un fichier quelque part dans `src/routes/` suffit à Nexy pour répondre à ce statut : une copie à la racine répond à l'ensemble du projet, une copie dans un dossier répond à ce dossier et une URL en dehors de chaque copie obtient la page intégrée. Réservez une autre extension pour ces noms dans `nexyconfig.py` avec `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions` et `useUnauthorizedExtensions`.

## Votre première page de dossier

```nexy filename="src/routes/blog/notfound.nexy"
---
title: Nothing here yet
---
<h1>That post is gone</h1>
<p>The <a href="/blog">blog</a> still has the others.</p>
```

Lancez le projet et demandez un post qui n'existe pas :

```bash
curl -i -H "Accept: text/html" http://localhost:3000/blog/old
# HTTP/1.1 404 Not Found
```

Une URL en dehors du dossier conserve la page que vous aviez déjà :

```bash
curl -i -H "Accept: text/html" http://localhost:3000/about
# HTTP/1.1 404 Not Found    (the root page, or the built-in one)
```

## Une 401 qui mène quelque part

Le dossier d'une zone protégée répond `401` avec la page qui propose le chemin d'accès :

```nexy filename="src/routes/private/unauthorized.nexy"
---
title: Sign in to continue
---
<h1>Sign in to see your notes</h1>
<a href="/sign-in" class="button">Sign in</a>
```

```python filename="src/routes/private/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```

Chaque appel et chaque statut garde ses deux réponses :

| Qui demande | `401` avec un fichier | `401` sans un |
|---|---|---|
| Navigateur (`Accept: text/html`) | la page du dossier | la page intégrée |
| Client (`Accept: application/json`) | `{"detail": "..."}` | `{"detail": "..."}` |

`unauthorized(scheme="Bearer")` ajoute `WWW-Authenticate: Bearer` aux deux réponses. Un détail construit à partir de la saisie de l'utilisateur est échappé en HTML dans la page.

> [!TIP]
> `Accept: */*`, la valeur par défaut de `curl` et de nombreuses bibliothèques HTTP, ne demande ni l'une ni l'autre et reçoit la page HTML. Ajoutez `-H "Accept: application/json"` lorsque vous voulez la réponse JSON.

## Vérifiez-le

```python filename="tests/test_private.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_a_private_url_asks_for_sign_in():
    answer = TestClient(app).get("/private/notes")
    assert answer.status_code == 401
    assert "Sign in" in answer.text


def test_an_api_client_gets_json():
    answer = TestClient(app).get(
        "/private/notes", headers={"accept": "application/json"}
    )
    assert answer.json() == {"detail": "Unauthorized"}
```

## Prochaines étapes

- [Pages d'erreur](README.md) : ce qui déclenche chaque statut, HTML ou JSON
- [Dépendances et gardes](../dependencies/README.md) : protéger un dossier entier
- [Test](../../../guides/testing.md) : `TestClient` du premier test
