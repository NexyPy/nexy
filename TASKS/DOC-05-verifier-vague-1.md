# DOC-05 — Vérifier la vague 1

| | |
|---|---|
| **Phase** | P1 — Fondations |
| **Statut** | `bloqué` |
| **Dépend de** | DOC-01, DOC-02, DOC-03, DOC-04 |
| **Débloque** | P2 |

## Objectif

S'assurer que les quatre pages de fondation forment un ensemble cohérent **avant** d'ouvrir le chantier navigation, et que rien n'a été cassé dans la nav ou les index.

## Contrôles

### 1. Automatiques

```bash
python -m pytest tests/unit/nexy/docs tests/unit/sites -q
python scripts/verify.py
```

### 2. Cohérence croisée (manuel, 15 min)

| Contrôle | Attendu |
|---|---|
| README → Core Concepts → Architecture → How Nexy Works | chaque page renvoie à la suivante, aucun retour en arrière nécessaire |
| Le diagramme de DOC-03 | identique à celui décrit dans DOC-04 §1 (pas deux schémas divergents) |
| Les définitions de DOC-02 | identiques, mot pour mot, à celles de `views/README.md` (DOC-12) |
| La promesse de DOC-01 | chaque puce est démontrable par une page existante |
| Le vocabulaire | aucun synonyme flottant : « routeur » ne désigne jamais un fichier, « vue » jamais un endpoint |

### 3. Index

- [ ] Les 3 nouvelles pages figurent dans les tableaux de `docs/README.md` (F5)
- [ ] Les 3 nouvelles pages figurent dans `llms.txt` (F4)
- [ ] `llms.txt` ne renvoie plus à `ARCHITECTURE.md` pour l'architecture (DOC-03)

## Critère de fin

- [ ] Les deux commandes sont vertes
- [ ] Les 3 tableaux de contrôle ci-dessus sont remplis sans écart
- [ ] Le journal de chaque tâche P1 est à jour

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Sert de porte de sortie à P1. |
