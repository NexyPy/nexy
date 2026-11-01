# DOC-12 - Views : page / vue / composant / route handler

| | |
|---|---|
| **Phase** | P3 - Terminologie |
| **Statut** | `prêt` |
| **Dépend de** | - (réutilise DOC-02 si D3 = séparation) |
| **Débloque** | - |

## Objectif

Définir les cinq notions **avant** de lister les formats de fichiers. Un lecteur venant de Next.js doit savoir ce qui est une page, une vue, un composant, un handler et un endpoint.

## Contexte utile

- La page actuelle (`docs/views/README.md`) liste `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte`, `.py` sans définir les notions : c'est un catalogue.
- Ces définitions seront reprises mot pour mot dans `core-concepts.md` (DOC-02) : **une seule rédaction**, deux points d'entrée.
- `docs/views/` représente 30 pages sur 86 ; cette page est la porte d'entrée de toutes.

## Définitions à poser

| Terme | Définition (à affiner) |
|---|---|
| Page | a URL-addressable resource of the application |
| View | how the content of a page is produced and rendered |
| Component | a reusable UI building block used to compose a view |
| Route handler | a Python function that handles an HTTP request |
| Endpoint | the URL + method a route handler answers |

## Structure cible

1. The five words - tableau ci-dessus.
2. Which format for which page - tableau format / rendu / quand l'utiliser / page dédiée.
3. Can I mix them? - oui, et comment (un `.nexy` avec un island React, par exemple).
4. What Nexy does not do - pas de framework frontend imposé.

## Fichiers

| Fichier | Action |
|---|---|
| `docs/views/README.md` | Réécrire |
| `docs/reference/glossary.md` | Faire pointer les cinq termes vers cette page plutôt que les redéfinir |

## Critère de fin

- [ ] Les cinq termes sont définis avant tout format de fichier
- [ ] Chaque format du tableau renvoie à sa page
- [ ] Aucune définition dupliquée avec `core-concepts.md` ou le glossaire
- [ ] Un lecteur sait, après la page, quel format choisir pour son cas

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Définitions reprises du brief, à valider contre le comportement réel. |
