# Performances

Ce que fait `nx start` par défaut, ce qu'il faut activer et ce qui a été mesuré.

## Par défaut

| Préoccupation | Par défaut | Modifiez-le |
|---|---|---|
| Traite | un travailleur Uvicorn par CPU sous Linux et macOS, un sous Windows | `nx start` exécute l'application via Uvicorn |
| Compression | désactivée | `useGZip = {"minimum_size": 1000}` dans [Config](../reference/config.md), ou compresser au niveau du proxy inverse |
| Fichiers statiques | servis avec `ETag` et `Last-Modified`, non `Cache-Control` | définissant une mise en cache de longue durée au niveau du proxy inverse ou du CDN pour les bundles hachés |
| Pages HTML | rendues par requête, pas de cache | [ISR](../rendering/isr.md) avec `revalidate = N` |
| Documents API | sur | `useDocs = False` en production |
| Nœud au moment de l'exécution | aucun | `nx build` pré-rend les composants client |

## Mesuré

Une exécution locale, un travailleur Uvicorn, Windows, Python 3.13, des connexions persistantes à partir d'une charge Python
générateur sur la même machine. Considérez les chiffres comme une référence pour comparer les changements, et non comme une
comparer avec d’autres cadres.

| Route | Concurrence | Requêtes par seconde | p50 | p99 |
|---|---|---|---|---|
| Route JSON FastAPI nue | 16 | ~4 500 | 3,4 ms | 5,1 ms |
| Route Nexy JSON (`src/routes/api/ping.py`) | 16 | ~2 900 | 5,2 ms | 9,8 ms |
| Page Nexy SSR (16 Ko, 16 éléments) | 1 | ~500 | 1,9 ms | 3,0 ms |
| Page Nexy SSR (16 Ko, 16 éléments) | 64 | ~670 | 94 ms | 126 ms |

Lecture du tableau :

- Les propres couches de Nexy (contexte de chemin, middleware) coûtent environ un tiers du débit d'un simple
  Itinéraire FastAPI.
- Une page rendue par le serveur coûte environ 2 ms de CPU, réparties sur environ 16 rendus de modèles (un par
  composant). Les pages avec moins de composants sont proportionnellement moins chères.
- Le débit évolue avec les travailleurs. Sous Linux, `nx start` en démarre déjà un par CPU.

## Conseils pratiques

1. Placez Nginx, Caddy ou la périphérie de votre plateforme : TLS, HTTP/2, Brotli et mise en cache longue durée pour
   `/__nexy__/client/` les atouts sont leurs points forts. Voir [Déployer](README.md).
2. Utilisez [ISR](../rendering/isr.md) pour les pages qui changent moins d'une fois par minute.
3. Hydrate paresseusement avec [islands](../rendering/islands.md) pour que le premier chargement envoie moins de JavaScript.
4. Gardez un nombre raisonnable de `.nexy` composants par page : chacun est un modèle distinct
   rendre.
5. Mesurez vos propres itinéraires. Un générateur de charge local qui maintient les connexions actives suffit pour comparer
   deux versions d'une page.

## Prochaines étapes

- [Déployer](README.md)
- [Rendu](../rendering/README.md)
- [Configuration](../reference/config.md)