# DOC-23 - Exemple fil conducteur exécuté

| | |
|---|---|
| **Phase** | P5 - Exemple |
| **Statut** | `prêt` |
| **Dépend de** | DOC-18 (Actions) idéalement |
| **Débloque** | - |

## Objectif

Remplacer les exemples isolés par **une seule application** suivie de bout en bout, dont le code est exécuté par la CI - pas illustré.

## Contexte utile - l'atout du dépôt

`docs/guides/recipes.md` contient des blocs ```` ```py filename="…" ```` que `test_recipes.py` (F6) scaffolde dans un vrai projet, construit, puis interroge via `TestClient` : login, CRUD, upload, codes d'erreur. C'est exactement le mécanisme à réutiliser : la page devient une **preuve**, pas un tutoriel.

## Le fil (10 étapes)

| # | Étape | Ce que le lecteur ajoute |
|---|---|---|
| 1 | une page `.nexy` | un fichier = une URL |
| 2 | un layout | un cadre partagé |
| 3 | une route dynamique | `[id]` |
| 4 | un endpoint `.py` | données côté serveur |
| 5 | une base de données | persistance |
| 6 | une Action | formulaire typé, sans client HTTP |
| 7 | un composant React | îlot dans une page serveur |
| 8 | une architecture modulaire | contrôleur + service |
| 9 | une authentification | session + vérification des droits |
| 10 | un déploiement | build + conteneur |

Chaque étape est un **incrément vérifiable** : on doit pouvoir s'arrêter à l'étape 4 et avoir une application qui tourne.

## Contrainte forte

L'étape 9 doit montrer que **le chemin d'une Action n'est pas une autorisation** (DOC-18) : la vérification des droits est écrite dans le code de l'exemple, pas seulement mentionnée.

## Fichiers

| Fichier | Action |
|---|---|
| `docs/getting-started/tutorial.md` | Réécrire en fil conducteur, avec blocs `filename=` |
| `tests/unit/nexy/docs/test_recipes.py` | Ajouter le scénario du tutoriel (même mécanisme) |
| `llms.txt` | Mettre à jour la ligne Tutorial |

## Critère de fin

- [ ] Le test scaffolde et exécute le code du tutoriel
- [ ] Chaque étape est un incrément qui tourne
- [ ] L'étape 9 contient une vraie vérification de droits
- [ ] Aucun bloc de code non testé dans la page
- [ ] F11 reste vert (activation du venv, ordre des commandes)

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Mécanisme `filename=` + `test_recipes.py` identifié comme modèle. |
| 2026-11-01 | Une réécriture « Rosetta Stone: One App, Five Frameworks » avait remplacé `tutorial.md` : hors périmètre (pas de bloc `filename=`, pas de fil en 10 étapes, activation du venv supprimée, donc F11 rouge). Le tutoriel d'origine est restauré depuis HEAD et `test_setup_guidance.py` repasse. Le brouillon est conservé dans `TASKS/drafts/rosetta-five-frameworks.md`. La tâche reste `prêt`. |
