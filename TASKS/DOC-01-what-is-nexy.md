# DOC-01 — What is Nexy?

| | |
|---|---|
| **Phase** | P1 — Fondations |
| **Statut** | `fait` |
| **Dépend de** | — |
| **Débloque** | DOC-05 |

## Objectif

Répondre en moins de 200 mots, avant toute technologie, à : *qu'est-ce que Nexy, quel problème résout-il, comment, et pourquoi lui plutôt qu'un assemblage classique ?*

## Contexte utile

- Le texte actuel (`docs/README.md:3-4`) commence par l'implémentation : « FastAPI and Starlette serve the app, Vite builds the client. » Le lecteur apprend la plomberie avant la promesse.
- Cette tête de fichier est **aussi** ce que lit un visiteur qui arrive sur `/docs` : c'est la page d'accueil.
- `llms.txt:3-4` porte la même phrase en blockquote : les deux doivent rester alignés (F4).

## Fichiers

| Fichier | Action |
|---|---|
| `docs/README.md` | Réécrire **uniquement** les lignes 1-4 (titre + paragraphe). Ne pas toucher aux `##`/`###`/tableaux. |
| `llms.txt` | Aligner la blockquote (lignes 3-4). |

## Brouillon à valider

```md
# Nexy documentation

**The Python-first fullstack framework.**

Nexy is a modern Python framework for building fullstack web applications with a unified
development experience. Built on FastAPI and Starlette, it keeps Python at the centre while
letting you add React, Vue, Svelte, Solid or Preact when a page needs them.

- **Python-first** — backend and server-rendered pages in Python.
- **Flexible architecture** — file-based routing, modular architecture, or an existing FastAPI router.
- **Frontend freedom** — no frontend framework required; add one when needed.
- **Unified rendering** — SSR, ISR, CSR and islands, chosen per page.
- **Developer experience** — integrated tooling and typed server actions.

Start with a single Python file and introduce structure as the project grows.
```

## Critère de fin

- [x] Les quatre questions ont une réponse explicite avant la première mention de Vite ou de Jinja2
- [x] Aucune ligne de tableau, aucun `##`/`###` modifié (F1, F2)
- [x] `llms.txt` porte la même promesse
- [x] `python -m pytest tests/unit/nexy/docs tests/unit/sites -q` vert
- [x] Aucune affirmation qui ne soit pas tenue par le reste de la doc (pas de « zero config », pas de « production ready »)

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Brouillon rédigé à partir de la proposition du brief, à valider avant écriture. |
| 2026-10-31 | **Fait.** Tête réécrite : promesse (une origine au lieu de deux serveurs, deux builds et deux tables de routes), puis cinq points tenus par la doc. Deux corrections au brouillon : (1) « SSR, ISR, CSR and islands, chosen per page » est faux pour CSR, qui est un commutateur de projet (`useCSR`) — le point dit maintenant « decided per page ; client routing is a project switch » (F15, DOC-16) ; (2) « Start with a single Python file » n'est pas ce que fait `nx new`, qui scaffolde `nexyconfig.py` et `src/routes/` — remplacé par « Start with one file under `src/routes/` », ce que `how-nexy-works.md` démontre. La blockquote de `llms.txt` porte la même promesse. Reste une occurrence de « meta-framework » dans `views/nexy/markdown.md:13`, hors périmètre de cette tâche : à traiter avec la terminologie en DOC-24. 438 tests verts. |
