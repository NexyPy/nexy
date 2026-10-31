# DOC-02 — Core Concepts

| | |
|---|---|
| **Phase** | P1 — Fondations |
| **Statut** | `bloqué` (D3) |
| **Dépend de** | D3 |
| **Débloque** | DOC-05 |

## Objectif

Donner le modèle mental de Nexy **avant** les API : quatre niveaux de lecture, puis les notions qui reviennent partout, chacune en 3 à 5 lignes avec un lien vers sa page.

## Contexte utile

- Aucune page ne joue ce rôle aujourd'hui : `reference/glossary.md` (580 mots) définit les mots, mais ne les hiérarchise pas.
- Le brief impose de distinguer **page / vue / composant / route handler / endpoint** — c'est la source de confusion n°1 d'un lecteur qui arrive de Next.js.
- Si D3 = séparation : cette page porte le **modèle**, le glossaire porte l'**index alphabétique**. Aucune phrase de définition ne doit être copiée entre les deux (une définition, un endroit).

## Structure proposée

```md
# Core concepts

## How to read these docs
Les 4 niveaux : architecture applicative → structure → présentation/rendu → interaction.

## Application architecture
File-based routing · Modular router · Custom router integration — une phrase + lien.

## Application structure
Route, page, endpoint, module, service, dependency — une phrase + lien.

## Presentation and rendering
View, component, layout, SSR/ISR/CSR/islands — une phrase + lien.

## Application interaction
Action, form, navigation, data fetching — une phrase + lien.

## What Nexy does not do
Authz, database, i18n : à la charge de l'application (A2).
```

## Fichiers

| Fichier | Action |
|---|---|
| `docs/getting-started/core-concepts.md` | Créer |
| `docs/README.md` | Ajouter la page au groupe « Understand the model » (obligatoire, F5) |
| `llms.txt` | Ajouter une ligne |
| `docs/reference/glossary.md` | Retirer les définitions dupliquées, garder l'index + liens |

## Critère de fin

- [ ] Chaque notion : une définition d'une phrase + un lien vers une page existante
- [ ] Les 5 notions page/vue/composant/route handler/endpoint sont définies ici (DOC-12 s'y réfère)
- [ ] La section « What Nexy does not do » existe et nomme authz, base de données, i18n
- [ ] Zéro paragraphe dupliqué avec le glossaire
- [ ] Page listée dans la nav et dans `llms.txt`

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Structure arrêtée ; écriture suspendue à D3. |
