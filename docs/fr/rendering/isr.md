# ISR (périmé pendant la revalidation)

## Définition

ISR met en cache le code HTML d'une page, par URL, et le sert jusqu'à l'expiration de sa fenêtre. La copie expirée est toujours servie tandis qu'une nouvelle est rendue en arrière-plan : c'est-à-dire *périmée pendant la revalidation*.

## Comment ça marche

`revalidate = N` au début d'une page `.nexy` l'active. `N` est un nombre de secondes ; une valeur manquante, nulle ou négative signifie aucun cache du tout.

La clé de cache est le **chemin de requête uniquement** - `request.scope["path"]`. La chaîne de requête n'en fait pas partie.

| Quoi | Valeur |
|---|---|
| Clé | le chemin de l'URL (`/blog/hello`) |
| Stockage | sélectionné par `useISRCache` : mémoire par défaut, fichier, Redis ou un magasin personnalisé |
| Lié | 256 entrées pour la mémoire stockée, la moins récemment utilisée et expulsées ; fichier et Redis conservent les entrées jusqu'à leur invalidation |
| En-tête de réponse | `cache-control: public, s-maxage=N, stale-while-revalidate=N` |

Chaque réponse ISR comporte cet en-tête, y compris le premier rendu et un rendu de secours lorsque le magasin est en panne. Un CDN peut l'utiliser pour conserver sa propre copie de la même URL publique.

## Cycle de vie du rendu

1. Une requête arrive pour une page qui déclare `revalidate`.
2. Aucune entrée pour l'instant : la page est rendue, stockée et renvoyée.
3. Entrée inférieure à `N` secondes : renvoyée telle quelle, la page n'est pas rendue.
4. Entrée datant de plus de `N` secondes : l'entrée **périmée** est renvoyée immédiatement et une tâche en arrière-plan en restitue une nouvelle.
5. Si ce rendu en arrière-plan échoue, l'entrée obsolète reste et la prochaine demande obsolète réessaye.
6. Si le magasin échoue, la page est rendue et renvoyée sans entrée en cache. La demande aboutit toujours.

## Quand utiliser

- Le même HTML pour chaque visiteur : un article de blog, une page produit, une page de documentation.
- La page est lue souvent et change rarement.
- Les données peuvent dater de quelques secondes sans que personne ne s’en aperçoive.

## Configuration

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

`N` est un entier simple. Il n'y a pas de remplacement par route ailleurs, et les gestionnaires `.py` ne sont pas des pages : ils n'entrent jamais dans ce cache.

## Choisissez un magasin

Définissez `useISRCache` dans `nexyconfig.py` :

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useISRCache = "file"
```

| Valeur | Magasin | Partagé par |
|---|---|---|
| non défini, `None` ou `"memory"` | mémoire de processus, limitée à 256 entrées | un travailleur |
| `"file"` | Fichiers JSON dans `.nexy/isr` | travailleurs sur un hôte |
| `{"type": "file", "directory": ".cache/isr"}` | Fichiers JSON dans le répertoire donné | travailleurs sur un hôte |
| `"redis"` | Redis chez `redis://localhost:6379/0` | tout travailleur qui atteint le serveur |
| `{"type": "redis", "url": "redis://cache:6379/0"}` | Redis à cette URL | tout travailleur qui atteint le serveur |
| `{"type": "redis", "client": client}` | le client Redis que vous passez | tout travailleur qui atteint le serveur |
| un objet avec `get`, `set` et `invalidate` | votre propre magasin | tout ce qu'il partage |

Le magasin Redis a besoin du package client : `uv add redis`. Il n'est pas installé avec Nexy. Un magasin personnalisé implémente le protocole `ISRCache` de `nexy.modules.runtime.cache` ; son `get` renvoie un `CacheEntry` ou `None`.

Les entrées de fichiers sont écrites de manière atomique, de sorte qu'un travailleur ne lit jamais une page à moitié écrite. Les travailleurs qui utilisent le même répertoire ou le même serveur Redis lisent la même entrée. Un store en panne ne coûte qu'un rendu : il ne répond jamais à la requête par une erreur.

## Exemple

Un article de blog qui lit une base de données :

```nexy filename="src/routes/blog/[slug].nexy"
---
revalidate = 300
slug: prop[str] = "untitled"
posts = {"hello": {"title": "Hello"}, "other": {"title": "Other"}}
post = posts.get(slug, {"title": "Untitled"})
---
<h1>{{ post.title }}</h1>
```

La première requête adressée à `/blog/hello` rend et stocke. Les 300 secondes suivantes sont diffusées depuis le magasin sélectionné. `/blog/other` est une entrée distincte, rendue et stockée seule. Dans un projet réel, `posts` provient d'une base de données ou d'un service, appelé une fois par régénération.

## Ce qu'un CDN peut et ne peut pas partager

Un CDN qui honore `cache-control` peut conserver une copie de `/blog/hello` pendant `s-maxage` secondes et la servir pendant sa revalidation. Il partage cette copie entre les visiteurs et les travailleurs car la réponse indique `public`.

Un CDN ne connaît pas la boutique Nexy. `revalidate()` dans une [Action](../guides/actions.md) supprime l'entrée du magasin Nexy configuré, mais il ne purge pas un CDN. Le CDN conserve sa copie jusqu'à la fin de sa propre fenêtre, ou jusqu'à ce que vous configuriez sa purge.

Ne donnez pas à un CDN une page dont le HTML dépend d'un visiteur. La réponse indique `public`, et la clé de Nexy est le chemin seul : deux chaînes de requête sur un chemin partagent une entrée. Une session, un cookie ou un identifiant utilisateur dans le HTML peut être servi à un autre visiteur.

## Limites

**Nexy garantit** que la clé de cache est le chemin, que la copie obsolète est servie pendant la régénération et qu'un échec de stockage revient à un rendu.

**Par convention**, une page qui déclare `revalidate` est un contenu public. Écrivez-le comme si chaque visiteur voyait le même code HTML.

**Votre application est responsable de** tout le reste :

| Limite | Ce que cela signifie |
|---|---|
| Chaîne de requête ignorée | `/search?q=a` et `/search?q=b` partagent une entrée. Ne mettez pas en cache une page de recherche. |
| Séance non isolée | La réponse indique `public`, et le code HTML du premier visiteur est diffusé à tous. Ne lisez jamais la session dans une page avec `revalidate`. |
| CDN non purgé | `revalidate()` purge la boutique Nexy, pas un CDN ou un autre proxy devant lui. |
| Pas de TTL dans les magasins de fichiers et Redis | Les entrées restent jusqu'à ce que `revalidate()` ou que votre propre nettoyage les supprime. Le magasin de mémoire supprime l'entrée la moins récemment utilisée après 256. |
| Régénérations simultanées | Rien ne les déduplique : dix requêtes obsolètes peuvent lancer dix rendus. |
| Les erreurs sont silencieuses | Une opération de régénération ou de stockage défaillante continue de diffuser la page ; l'échec n'est pas retourné. |

## Prochaines étapes

- [SSR](ssr.md) : comment la page est rendue avant d'être mise en cache
- [Actions](../guides/actions.md) : l'en-tête `revalidate` et l'invalidation du magasin
- [Configuration](../reference/config.md#server) : `useISRCache`
- [Performances](../deployment/performance.md)
- [Pages](../routing/fbr/pages/README.md) : mises en page et segments dynamiques
