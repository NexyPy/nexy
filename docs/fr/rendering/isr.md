# ISR (périmé pendant la revalidation)

## Définition

ISR met en cache le code HTML d'une page, par URL, et le sert jusqu'à l'expiration de sa fenêtre. La copie expirée
est toujours servi tandis qu'un nouveau est rendu en arrière-plan : c'est-à-dire *stale-while-revalidate*.

## Comment ça marche

`revalidate = N` au début d'une page `.nexy` l'active. `N` est un nombre de secondes ; un
une valeur manquante, nulle ou négative signifie aucun cache du tout.

La clé de cache est le **chemin de requête uniquement** - `request.scope["path"]`. La chaîne de requête ne fait pas partie
de celui-ci.

| Quelle | Valeur |
|---|---|
| Saisissez | le chemin de l'URL (`/blog/hello`) |
| Stockage | en mémoire, dans le processus qui rend la page |
| Lié | 256 entrées par processus, les moins récemment utilisées expulsées |
| En-tête de réponse | `cache-control: public, s-maxage=N, stale-while-revalidate=N` |

## Cycle de vie du rendu

1. Une requête arrive pour une page qui déclare `revalidate`.
2. Aucune entrée pour l'instant : la page est rendue, stockée et renvoyée.
3. Entrée inférieure à `N` secondes : renvoyée telle quelle, la page n'est pas rendue.
4. Entrée datant de plus de `N` secondes : l'entrée **périmée** est renvoyée immédiatement et une tâche en arrière-plan
   en rend un nouveau.
5. Si ce rendu en arrière-plan se déclenche, l'entrée obsolète reste et la prochaine requête obsolète réessaye.

## Quand utiliser

- Le même HTML pour chaque visiteur : un article de blog, une page produit, une page de documentation.
- La page est lue souvent et change rarement.
- Les données peuvent dater de quelques secondes sans que personne ne s'en aperçoive.

## Configuration

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

`N` est un entier simple. Il n'y a pas de remplacement par route ailleurs, et les gestionnaires `.py` ne sont pas des pages :
ils n'entrent jamais dans cette cache.

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

La première requête à `/blog/hello` rend et stocke. Les 300 secondes suivantes sont servies de mémoire.
`/blog/other` est une entrée distincte, rendue et stockée seule. Dans un vrai projet `posts` vient
à partir d'une base de données ou d'un service, appelé une fois par régénération.

## Contraintes

**Nexy garantit** que la clé de cache est le chemin, que la copie obsolète est servie lors de la régénération et que le
le magasin est limité et thread-safe.

**Par convention**, une page qui déclare `revalidate` est un contenu public. Écrivez-le comme si chaque visiteur
voit le même code HTML.

**Votre candidature est responsable de** tout le reste :

| Limite | Ce que cela signifie |
|---|---|
| Chaîne de requête ignorée | `/search?q=a` et `/search?q=b` partagent une entrée. Ne mettez pas en cache une page de recherche. |
| Session non isolée | La réponse indique `public`, et le HTML du premier visiteur est servi à tous. Ne lisez jamais la session dans une page avec `revalidate`. |
| Aucune invalidation côté serveur. | Nothing purge une entrée avant la fin de sa fenêtre. `revalidate(...)` à l'intérieur d'une [Action](../guides/actions.md) indique uniquement au **navigateur** de recharger un chemin ; cela ne touche pas à ce cache. |
| Un cache par processus | Plusieurs Workers conservent plusieurs caches, avec des contenus différents. |
| Régénérations simultanées | Rien ne les déduplique : dix requêtes périmées peuvent lancer dix rendus. |
| Les erreurs sont silencieuses. | Une régénération défaillante continue de servir l'ancienne page ; l'échec est enregistré et non renvoyé. |

## Prochaines étapes

- [SSR](ssr.md) : comment la page est rendue avant d'être mise en cache
- [Actions](../guides/actions.md) : l'en-tête `revalidate` et ce qu'il ne fait pas
- [Performances](../deployment/performance.md)
- [Pages](../routing/fbr/pages/README.md) : mises en page et segments dynamiques