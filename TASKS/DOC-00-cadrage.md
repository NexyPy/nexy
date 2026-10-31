# DOC-00 — Cadrage : trancher D1–D4

| | |
|---|---|
| **Phase** | P0 |
| **Statut** | `fait` |
| **Dépend de** | — |
| **Débloque** | DOC-02, DOC-03, DOC-06 → DOC-11, DOC-20 → DOC-22 |

## Objectif

Obtenir les quatre décisions qui bloquent 13 tâches. Aucune écriture de contenu tant qu'elles ne sont pas prises : chaque option change des fichiers différents.

## Les quatre décisions

### D1 — Périmètre

| Option | Conséquence |
|---|---|
| **A. `docs/` seul** | On améliore le contenu, mais le sélecteur reste un filtre cosmétique (F3). P2 et P4 sont impossibles. |
| **B. `docs/` + `sites/` + `tests/unit/sites/`** *(recommandé)* | Le sélecteur devient un vrai parcours ; coût : `docs_source.py`, `build.py`, `Sidebar.nexy`, `SearchDialog.nexy`, `site.js`, `style.css`, 2 fichiers de tests. |

### D2 — Architecture

| Option | Conséquence |
|---|---|
| **A. Nouvelle page `docs/architecture.md`** *(recommandé)* | Lecteurs et contributeurs ont chacun leur page ; deux renvois croisés à maintenir. |
| **B. Fusion** | Une seule source, mais la page doit alors parler à la fois du modèle conceptuel et du VFS/importlib/watcher — deux publics dans un document. |

### D3 — Core Concepts vs Glossary

| Option | Conséquence |
|---|---|
| **A. Séparation** *(recommandé)* | `core-concepts.md` = modèle mental à 4 niveaux + liens ; `glossary.md` = index A→Z d'une ligne. Risque : deux endroits où une définition peut diverger. |
| **B. Fusion** | Zéro divergence, mais une page qui sert à la fois d'introduction et de dictionnaire. |

### D4 — Consolidation frontend

| Option | Conséquence |
|---|---|
| **A. Redirections** *(recommandé)* | 25 → ~11 pages ; nécessite une table de redirections dans les deux sites et une mise à jour de `llms.txt`. URL publiées cassées sans redirection. |
| **B. Statu quo structurel** | Aucune URL cassée, mais 29 % de la doc reste en duplication (F8) et la charge cognitive ne baisse pas. |

## Critère de fin

- [x] D1, D2, D3, D4 inscrites dans `TASKS/README.md` §Décisions ouvertes → actées
- [x] Les statuts des tâches débloquées passent de `bloqué` à `prêt`
- [x] Aucune tâche ne cite encore une décision ouverte

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Les 4 questions ont été posées en conversation, sans réponse à ce stade. |
| 2026-10-31 | **Fait.** Réponses : D1 = `docs/` + `sites/` + `tests/unit/sites/` ; D2 = deux fichiers avec renvois croisés ; D3 = séparation modèle / index ; D4 = consolidation avec redirections. Consignées en A7–A10 dans `TASKS/README.md`. Débloquées : DOC-02, DOC-03, DOC-06, DOC-10, DOC-11, DOC-20. DOC-21 et DOC-22 restent bloquées par DOC-20, pas par une décision. |
