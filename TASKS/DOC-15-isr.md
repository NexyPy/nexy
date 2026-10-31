# DOC-15 — ISR

| | |
|---|---|
| **Phase** | P3 — Rendu |
| **Statut** | `prêt` |
| **Dépend de** | DOC-13 |
| **Débloque** | — |

## Objectif

Faire de l'ISR une fonctionnalité **spécifiée**, pas un cache magique. Le brief est explicite : l'ISR est un système de cohérence des données, et ses limites doivent être écrites.

## Squelette imposé (A1)

1. Definition · 2. How it works · 3. Rendering lifecycle · 4. When to use · 5. Configuration · 6. Example · 7. Limitations · 8. Related.

## Ce que la page doit dire (vérifié dans le code)

| Question du brief | Réponse à documenter |
|---|---|
| Quelle est la clé de cache ? | **L'URL seule** (`request.scope["path"]`) — pas de query string, pas de host |
| Paramètres dynamiques ? | chaque URL est mise en cache séparément |
| Fuite entre utilisateurs ? | **risque réel** : une page `revalidate` qui lit la session sert le HTML du premier visiteur à tous ; la réponse part en `cache-control: public` |
| Invalidation après mutation ? | explicite, depuis une Action (`revalidate(...)`) |
| Régénérations simultanées ? | aucune déduplication : plusieurs requêtes simultanées peuvent déclencher plusieurs rendus |
| Erreur pendant la revalidation ? | l'entrée reste servie périmée, la régénération est retentée à la requête suivante |
| Portée du cache | mémoire, par process, borné (LRU) : plusieurs workers = plusieurs caches indépendants |

Ces constats viennent de `nexy/modules/runtime/cache.py` et `nexy/modules/routers/fbrouter/handlers.py`. **Les corriger est le Chantier 2** ; ici on les documente honnêtement, avec la règle A2 : ce qui est garanti, ce qui est convention, ce qui reste à la charge du développeur.

## Règle de rédaction

Chaque limite doit être formulée dans une des trois formes, et une seule :

- *Nexy guarantees…*
- *By convention…*
- *Your application is responsible for…*

## Fichiers

| Fichier | Action |
|---|---|
| `docs/rendering/isr.md` | Réécrire sur le squelette + tableau des limites |

## Critère de fin

- [ ] Les 7 questions ci-dessus ont une réponse explicite
- [ ] La page dit clairement qu'une page ISR ne doit pas dépendre de la session utilisateur (ou explique exactement dans quel cas c'est sûr)
- [ ] Aucune limite formulée comme une garantie
- [ ] La section Related renvoie à Actions (invalidation) et à `deployment/performance.md`

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Limites vérifiées dans `runtime/cache.py` et `fbrouter/handlers.py`. |
