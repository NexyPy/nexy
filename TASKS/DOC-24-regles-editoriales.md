# DOC-24 - Règles éditoriales (hors `docs/`)

| | |
|---|---|
| **Phase** | P6 - Règles |
| **Statut** | `prêt` |
| **Dépend de** | - |
| **Débloque** | - |

## Objectif

Rendre le contrat de page **opposable** : un contributeur doit pouvoir écrire une page conforme sans lire les 86 autres.

## Contexte utile - où ne pas le mettre

- `docs/` est interdit : tout `.md` de `docs/` doit figurer dans la navigation, sinon `test_routers.py:70` échoue (F5).
- Emplacements possibles : `skills/` (lu par les agents, liens validés par `test_links.py`) ou `CONTRIBUTING.md` (entrée racine, liens validés aussi).
- Recommandation : **`CONTRIBUTING.md`** pour la règle humaine, et une ligne de renvoi dans `skills/` pour les agents. Une seule source de vérité, deux lecteurs.

## Contenu à écrire

### 1. Deux contrats de page (A1)

- **Conceptuelle** : Definition · How it works · Lifecycle · When to use · Configuration · Example · Limitations · Related.
- **Référence** : tableau strict (nom, type, défaut, description, exemple, contraintes, options liées) - aucun paragraphe narratif.

### 2. Trois niveaux de garantie (A2)

Une phrase ne mélange jamais :

| Forme | Sens |
|---|---|
| *Nexy guarantees…* | comportement testé du framework |
| *By convention…* | ce que la structure attend de vous |
| *Your application is responsible for…* | authz, données, i18n, secrets |

### 3. Vocabulaire imposé

Route, page, view, component, layout, handler, endpoint, action, island, mode. Chaque mot a **une** définition (DOC-02 / DOC-12) et aucun synonyme.

### 4. Règles mécaniques

- Une page = une question.
- Tout exemple de code exécutable porte `filename=` (F6).
- Tout nouveau `.md` de `docs/` entre dans la nav et dans `llms.txt` (F4, F5).
- Aucune promesse de performance sans renvoi à `deployment/performance.md`.

### 5. Test de conformité (optionnel mais recommandé)

Un test qui vérifie qu'une page conceptuelle contient les 8 titres, et qu'une page de référence ne contient pas de paragraphe hors tableau. À n'écrire que si le coût est faible - sinon, revue humaine.

## Fichiers

| Fichier | Action |
|---|---|
| `CONTRIBUTING.md` | Nouvelle section « Writing documentation » |
| `skills/*/SKILL.md` | Une ligne de renvoi |

## Critère de fin

- [ ] Les 5 sections existent
- [ ] Le contrat de page est cité par `TASKS/README.md` (A1/A2) sans divergence
- [ ] `test_links.py` vert (les liens ajoutés résolvent)
- [ ] Un contributeur peut écrire une page sans lire les autres

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Emplacement choisi après vérification de F5. |
