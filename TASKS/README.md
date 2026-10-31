# TASKS — Chantier 1 : Documentation Nexy

Suivi de projet et mémoire de travail. **Ce dossier n'est pas de la documentation publiée** : rien ici n'entre dans `docs/`, la navigation, `llms.txt` ou le site. Aucun test ne le lit (vérifié : `test_links.py` ne scanne que les entrées racine + `docs/` + `skills/`).

## Protocole

1. **Une tâche = un fichier** `DOC-XX-<slug>.md`. Le numéro ne change jamais.
2. **Un statut, une vérité** : `prêt` · `bloqué` · `en cours` · `fait`. Mis à jour dans le fichier *et* dans le tableau ci-dessous.
3. **Chaque session ajoute une ligne au journal** de la tâche concernée : date, ce qui a été fait, ce qui reste.
4. **Une tâche bloquée nomme sa décision** (`D1`–`D4`, §Décisions). On ne commence pas une tâche bloquée.
5. **Aucune tâche ne touche `nexy/`** — c'est le Chantier 2.

## Index

| ID | Tâche | Phase | Statut | Dépend de |
|---|---|---|---|---|
| [DOC-00](DOC-00-cadrage.md) | Cadrage : trancher D1–D4 | P0 | `bloqué` | — |
| [DOC-01](DOC-01-what-is-nexy.md) | What is Nexy? (tête du README) | P1 | `prêt` | — |
| [DOC-02](DOC-02-core-concepts.md) | Core Concepts | P1 | `bloqué` | D3 |
| [DOC-03](DOC-03-architecture-overview.md) | Architecture Overview | P1 | `bloqué` | D2 |
| [DOC-04](DOC-04-how-nexy-works.md) | How Nexy Works (réécriture) | P1 | `prêt` | — |
| [DOC-05](DOC-05-verifier-vague-1.md) | Vérifier la vague 1 | P1 | `bloqué` | DOC-01→04 |
| [DOC-06](DOC-06-marqueurs-de-groupe.md) | Marqueurs de groupe dans la nav | P2 | `bloqué` | D1 |
| [DOC-07](DOC-07-appliquer-les-marqueurs.md) | Appliquer les marqueurs aux groupes | P2 | `bloqué` | DOC-06 |
| [DOC-08](DOC-08-bucket-advanced.md) | Bucket Advanced + « All documentation » | P2 | `bloqué` | DOC-06 |
| [DOC-09](DOC-09-recherche-contextuelle.md) | Recherche contextuelle | P2 | `bloqué` | DOC-06 |
| [DOC-10](DOC-10-sync-llms-txt.md) | Synchroniser `llms.txt` | P2 | `bloqué` | D1 |
| [DOC-11](DOC-11-routing-terminologie.md) | Routing : deux routeurs, une intégration | P3 | `bloqué` | D1 |
| [DOC-12](DOC-12-views-definitions.md) | Views : page / vue / composant / handler | P3 | `prêt` | — |
| [DOC-13](DOC-13-rendering-overview.md) | Rendering : matrice de comparaison | P3 | `fait` | — |
| [DOC-14](DOC-14-ssr.md) | SSR | P3 | `fait` | DOC-13 |
| [DOC-15](DOC-15-isr.md) | ISR | P3 | `fait` | DOC-13 |
| [DOC-16](DOC-16-csr.md) | CSR | P3 | `fait` | DOC-13 |
| [DOC-17](DOC-17-islands.md) | Islands | P3 | `fait` | DOC-13 |
| [DOC-18](DOC-18-actions.md) | Actions : cycle complet | P3 | `prêt` | — |
| [DOC-19](DOC-19-getting-started.md) | Getting Started : prérequis et résultat | P3 | `prêt` | — |
| [DOC-20](DOC-20-frontend-contrats.md) | 4 contrats frontend partagés | P4 | `bloqué` | D4 |
| [DOC-21](DOC-21-frontend-differences.md) | 1 page « differences » par framework | P4 | `bloqué` | D4 |
| [DOC-22](DOC-22-redirections.md) | Redirections des anciennes URL | P4 | `bloqué` | D4 |
| [DOC-23](DOC-23-exemple-fil-conducteur.md) | Exemple fil conducteur exécuté | P5 | `prêt` | — |
| [DOC-24](DOC-24-regles-editoriales.md) | Règles éditoriales (hors `docs/`) | P6 | `prêt` | — |

## Phases

| Phase | Objet | Sortie |
|---|---|---|
| P0 | Cadrage | D1–D4 tranchées |
| P1 | Fondations | 4 pages qui donnent le modèle mental |
| P2 | Navigation | le sélecteur devient un parcours, pas un filtre cosmétique |
| P3 | Terminologie et rendu | plus aucune ambiguïté sur les mots et les modes |
| P4 | Consolidation frontend | 25 pages → ~11, sans perte de contenu |
| P5 | Exemple fil conducteur | une application suivie de bout en bout, code testé |
| P6 | Règles éditoriales | le contrat de page, opposable aux contributions |

## Décisions

### Actées

| ID | Décision |
|---|---|
| A1 | Deux contrats de page : **conceptuelle** (8 points) vs **référence** (tableau strict). |
| A2 | Trois niveaux de garantie jamais mélangés : *garanti par Nexy* / *convention* / *à la charge du développeur*. |
| A3 | Deux axes séparés : sélecteur de routeur (global) ≠ choix frontend (dans `views/*`). |
| A4 | Le grain du filtrage est **le groupe**, pas la page. |
| A5 | Ordre : fondations → navigation → terminologie → frontend → exemple. |
| A6 | Le titre publié de la section 8 du contrat conceptuel est **« Next steps »**, pas « Related » : 81 pages l'utilisent déjà. « Related » reste le nom du point dans `TASKS/`. Un renommage global, s'il a lieu, se décide en DOC-24. |

### Ouvertes

| ID | Question | Bloque |
|---|---|---|
| **D1** | Périmètre : `docs/` seul, ou `docs/` + `sites/` + `tests/unit/sites/` ? Le sélecteur exige la 2ᵉ option. | DOC-06→11, DOC-20→22 |
| **D2** | `docs/architecture.md` (lecteurs) + `ARCHITECTURE.md` (contributeurs) avec renvois, ou fusion ? | DOC-03 |
| **D3** | `core-concepts.md` (modèle mental) vs `glossary.md` (index A→Z) : séparation ou fusion ? | DOC-02 |
| **D4** | Consolidation frontend : redirections acceptées, ou garder les 25 pages ? | DOC-20→22 |

## Garde-fous

```bash
python -m pytest tests/unit/nexy/docs tests/unit/sites -q
python scripts/verify.py
```

Faits et contraintes du dépôt : [CONTEXT.md](CONTEXT.md).
