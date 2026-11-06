# Héritage

Plusieurs fichiers dans `src/routes/` s'appliquent à tout ce qui se trouve sous leur répertoire. Ils se résolvent tous de la même manière : Nexy commence par le répertoire de l'itinéraire et se dirige vers `src/routes/`.

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| Fichier | Règle |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | chaque mise en page, de la racine à la page, l'enveloppe, **le plus à l'extérieur en premier** |
| `middleware.py` | chaque fichier, de la racine à la route, encapsule la requête, **le plus externe en premier**, avant les dépendances |
| `dependencies.py` | chaque fichier, de la racine à la route, s'exécute, **le plus à l'extérieur en premier**, puis les propres gardes du gestionnaire |
| `notfound.nexy`, `errors.nexy` | le **le plus proche** gagne, par code de statut |

Pour la page ci-dessus, les mises en page s'imbriquent sous la forme `root layout > (shop) layout > cart layout > page` et les dépendances s'exécutent sous la forme `root > (shop) > cart > handler guards`.

## Pourquoi le plus extérieur en premier

Une disposition externe dessine le cadre et une dépendance externe décide qui peut entrer. Les placer en premier signifie que les internes peuvent s'appuyer sur eux : un répertoire qui nécessite une authentification s'exécute avant un gestionnaire qui lit l'utilisateur.

La dépendance `(shop)` de l'arborescence vérifie le cookie du panier, de sorte que la dépendance du panier en dessous peut lire le panier sans vérifier à nouveau :

```python filename="src/routes/(boutique)/dependencies.py"
from nexy.http import HTTPException, Request


def require_cart(request: Request) -> None:
    if "cart" not in request.cookies:
        raise HTTPException(status_code=400, detail="No cart")


dependencies = [require_cart]
```

## Mises en page

Tous les fichiers de mise en page d'une pile de familles de dossiers : voir [Mises en page](layouts/README.md). Les différentes familles ne se mélangent pas : un `layout.vue` ne enveloppe jamais une page `.tsx`, et un projet a soit des mises en page `layout.nexy`, soit des mises en page client, jamais les deux ([modes](modes.md)).

La disposition la plus interne de l'arborescence ajoute uniquement son propre cadre : la disposition racine qui l'entoure dessine toujours le document.

```nexy filename="src/routes/(boutique)/cart/layout.nexy"
---
children: prop[NexyElement]
---
<section class="cart">
  <h2>Your cart</h2>
  {{ children | safe }}
</section>
```

## Fichiers middleware

Voir [Fichiers Middleware](middleware/README.md) : ils s'exécutent avant les dépendances et peuvent répondre sans atteindre la route.

Une racine `middleware.py` enveloppe chaque itinéraire de l'arbre, le chariot inclus :

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## Dépendances

Voir [Dépendances](dependencies/README.md) pour l'ordre dans un fichier de gestionnaire, y compris `@UseGuard` et `@Middleware`.

## Pages d'erreur

`notfound.nexy` et `errors.nexy` sont installés une fois à la racine des routes ; une copie dans un sous-répertoire affine la page pour ce préfixe. Voir [Pages d'erreur](errors/README.md).

Une copie dans `cart/` répond aux 404 sous `/cart`, et la racine garde le reste :

```nexy filename="src/routes/(boutique)/cart/notfound.nexy"
<h1>This product is gone</h1>
<p><a href="/cart">Back to your cart</a></p>
```

## Prochaines étapes

- [Mises en page](layouts/README.md)
- [Dépendances](dependencies/README.md)
- [Pages d'erreur](errors/README.md)
