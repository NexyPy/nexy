# DOC-20 — Quatre contrats frontend partagés

| | |
|---|---|
| **Phase** | P4 — Frontend |
| **Statut** | `prêt` |
| **Dépend de** | — |
| **Débloque** | DOC-21, DOC-22 |

## Objectif

Écrire une fois ce qui est vrai pour les cinq frameworks : pages, layouts, islands, actions et navigation. Les pages par framework ne garderont que les différences (DOC-21).

## Contexte utile

- `docs/views/{react,vue,svelte,solid,preact}/` = 25 pages, 4 sections identiques par framework (F8). C'est 29 % de la documentation pour un contenu à 80 % commun.
- Le socle existe déjà côté code : `sites`/`frontend` partagent `runtime.ts`, `vite.ts`, un SSG unifié. La doc doit refléter ce socle, pas cinq variantes.
- Contrainte : chaque contrat doit être **vérifié vrai pour les 5** avant publication. Un contrat faux pour un framework est pire que cinq pages dupliquées.

## Les 4 pages

| Page | Contrat |
|---|---|
| `views/frontend/pages.md` | un fichier = une route ; props reçues ; quand le rendu a lieu (serveur vs client) |
| `views/frontend/layouts.md` | le layout possède `<html>` ; imbrication ; ce qu'un layout ne peut pas faire |
| `views/frontend/islands.md` | hydratation, props sérialisables, déclencheurs (renvoi DOC-17) |
| `views/frontend/actions-and-navigation.md` | appeler une Action typée, naviguer, lire l'URL |

## Méthode

1. Lire les 5 versions existantes d'une section.
2. Écrire le contrat commun.
3. Vérifier ligne à ligne que les 5 le respectent ; ce qui diffère part en DOC-21.
4. Ne garder dans la page partagée **aucun** exemple spécifique à un framework.

## Fichiers

| Fichier | Action |
|---|---|
| `docs/views/frontend/*.md` (4) | Créer |
| `docs/README.md` | Nouveau groupe « Frontend » avec les 4 pages + un lien par framework |
| `llms.txt` | 4 lignes + mise à jour des lignes par framework |

## Critère de fin

- [ ] Chaque contrat est vrai pour les 5 frameworks (vérifié, pas supposé)
- [ ] Zéro exemple spécifique dans les pages partagées
- [ ] Chaque page par framework renvoie au contrat au lieu de le répéter
- [ ] Les 4 pages sont dans la nav et dans `llms.txt`

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Périmètre des 4 contrats arrêté. |
