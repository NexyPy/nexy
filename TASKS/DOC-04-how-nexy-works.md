# DOC-04 — How Nexy Works (réécriture)

| | |
|---|---|
| **Phase** | P1 — Fondations |
| **Statut** | `fait` |
| **Dépend de** | — |
| **Débloque** | DOC-05 |

## Objectif

Faire de cette page la référence conceptuelle : un fichier devient une route, une requête traverse le serveur, une page est rendue. Le lecteur doit pouvoir prédire le comportement de Nexy après l'avoir lue.

## Contexte utile

- Page actuelle : ~600 mots, correcte mais descriptive (« voici les composants ») plus qu'explicative (« voici pourquoi dans cet ordre »).
- Elle est déjà liée depuis `llms.txt:13` et depuis « Understand the model » : pas de nouvelle URL, pas de redirection.
- Elle doit renvoyer vers DOC-03 pour l'architecture et ne pas la dupliquer.

## Structure cible (7 sections)

| # | Section | Question à laquelle elle répond |
|---|---|---|
| 1 | The Nexy architecture | qui est là, et qui n'est pas là (renvoi DOC-03) |
| 2 | The application lifecycle | que se passe-t-il entre `nexy dev` et la première requête ? |
| 3 | The routing system | comment un chemin de fichier devient une URL, et qui gagne en cas de collision |
| 4 | The view system | `.nexy`, `.md`, `.tsx`… : ce qui décide du format |
| 5 | The rendering lifecycle | quand les données sont lues, quand le HTML est produit, quand JS arrive |
| 6 | The frontend integration | pourquoi Vite ne remplace pas Nexy, pourquoi Nexy ne remplace pas React |
| 7 | Development and production | deux colonnes : ce qui change, ce qui ne change pas |

## Fichiers

| Fichier | Action |
|---|---|
| `docs/getting-started/how-nexy-works.md` | Réécrire intégralement |

## Critère de fin

- [x] Les 7 sections existent, dans cet ordre
- [x] La section 3 dit explicitement ce qui se passe quand deux routeurs produisent la même URL (au minimum : l'ordre d'enregistrement décide — vérifié dans `router_resolver.py`)
- [x] La section 6 contient les deux phrases « Vite ne remplace pas Nexy » et « Nexy ne remplace pas React », avec la raison
- [x] Aucun mécanisme interne de contributeur (VFS, watcher) hors d'une phrase de renvoi
- [x] Chaque section tient en moins de 150 mots ou renvoie à sa page dédiée

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Structure en 7 sections arrêtée. |
| 2026-10-31 | **Fait.** Page réécrite sur les 7 sections. L'ordre de précédence de la section 3 a été relevé dans le code : endpoint Actions → fichiers statiques → `APIRouter` modulaire → routes fichier triées par spécificité (`path_sort_key`), les ex æquo en ordre alphabétique parce que `RouteDiscovery.scan()` renvoie `sorted(valid)` et que le tri du registrar est stable. L'ancienne page disait seulement « the router finds the file ». Section 2 écrite depuis `cli/commands/dev.py` (`_initialise`, `_Reloader`). `.jsx` n'est pas listé dans le tableau des vues : découvert comme route mais non compilable (F18), donc Chantier 2. Reste à faire : le renvoi vers `docs/architecture.md` de la section 1, qui ne peut pas exister avant DOC-03 — c'est DOC-03 qui l'ajoutera (son critère de fin le prévoit déjà). |
