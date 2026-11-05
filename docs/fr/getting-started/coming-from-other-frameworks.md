# Venant d'un autre cadre

Nexy, c'est FastAPI plus un routage basé sur des fichiers, des pages rendues par le serveur et des îles optionnelles React, Vue, Svelte, Solid ou Preact. Cette page cartographie ce que vous savez déjà.

## De FastAPI

| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` dans un module que vous importez | Fonction `GET` dans `src/routes/users.py` |
| `app.include_router(router)` | le chemin du fichier est l'URL ; rien à inscrire |
| Paramètres de chemin `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | toujours `Depends(...)` : les gestionnaires sont des FastAPI gestionnaires |
| Jinja2 `TemplateResponse` | une page `.nexy` à côté du point de terminaison |
| Courir avec `uvicorn main:app` | `nx dev`, puis `nx build && nx start` |

Tout sous `src/routes/*.py` est ordinaire FastAPI : les dépendances, les modèles Pydantic, le middleware et `/docs` continuent de fonctionner.

## De Next.js

| Next.js | Nexy |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` ou `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (possède `<html>`) | `src/routes/layout.tsx` avec `useCSR = True` (React), ou `src/routes/layout.nexy` en mode serveur |
| imbriqué `layout.tsx` | `layout.tsx` / `layout.vue` / `layout.svelte` imbriqués en mode client, `layout.nexy` imbriqués en mode serveur |
| `use client` composants dans une page de serveur | [îles](../rendering/islands.md) en mode serveur |
| Gestionnaires de routes `route.ts` | `src/routes/api/x.py`, écrit en Python |
| `(group)` dossiers | idem : `(group)/` |
| Actions du serveur | [`@Action`](../guides/actions.md) fonctions appelées depuis un formulaire ou sous forme de fonctions client saisies |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

Le backend est Python, donc votre API partage le code avec vos données et votre travail de ML. Les composants clients s'hydratent sous forme d'îlots au lieu d'une page entière React arbre.

## Depuis les backends Express ou Node

| Exprimer | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` avec `async def GET(id)` |
| `app.use(middleware)` | FastAPI middleware, enregistré depuis `nexyconfig.py` |
| `res.json(obj)` | renvoyer un dict ou un modèle Pydantic |
| Vues EJS / Carlin | `.nexy` (Jinja2) pages |
| `npm run dev` | `nx dev` |

## Choisir un routeur

| Utiliser | Quand |
|---|---|
| Routeur basé sur des fichiers | pages et points de terminaison mappés à partir de fichiers ; la valeur par défaut |
| Routeur modulaire | contrôleurs, modules et injection de dépendances, style NestJS |

Les deux sont échafaudés par `nx new` et couverts par les mêmes tests de bout en bout. Voir [Routage](../routing/README.md) et [Routage modulaire](../routing/modular/README.md).

## Où ensuite

- [Démarrage rapide](quick-start.md) : créez un projet et exécutez-le
- [Structure du projet](project-structure.md) : où appartient chaque fichier
- [Routage](../routing/README.md) : choisissez le routeur
