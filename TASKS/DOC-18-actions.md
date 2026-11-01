# DOC-18 - Actions : cycle complet

| | |
|---|---|
| **Phase** | P3 - Interaction |
| **Statut** | `en cours` |
| **Dépend de** | - |
| **Débloque** | - |

## Objectif

Faire comprendre que les Actions sont un **mécanisme de communication** entre frontend et backend, pas une syntaxe décorative. C'est l'argument produit le plus fort de Nexy : il doit être expliqué, pas seulement montré.

## Cycle à documenter

| Étape | Ce que le lecteur doit comprendre |
|---|---|
| 1. Define | une fonction Python devient un endpoint POST |
| 2. Validate | les paramètres sont validés selon la signature |
| 3. Execute | la logique métier s'exécute côté serveur |
| 4. Serialize | le résultat devient une réponse exploitable |
| 5. Consume | le frontend récupère le résultat **avec ses types** |

## Questions à traiter

- **Pourquoi une Action plutôt qu'un endpoint classique ?** - pas de duplication endpoint + type TS + client HTTP.
- **Différence entre un appel direct et `useAction`** - quand utiliser l'un ou l'autre.
- **Erreurs** : distinguer validation, HTTP, métier, réseau, serveur. Un lecteur doit savoir laquelle remonte et sous quelle forme.
- **Revalidation** : une Action peut invalider des pages ISR (`revalidate(...)`) - renvoyer à DOC-15.
- **Authentification / permissions** : **le chemin généré n'est pas une autorisation**. C'est à l'application de vérifier les droits. À écrire noir sur blanc, en gras, et à classer comme « à la charge du développeur » (A2).
- **Origine** : Nexy refuse les requêtes d'une autre origine - c'est une protection CSRF de navigateur, pas une authentification.

## Fichiers

| Fichier | Action |
|---|---|
| `docs/guides/actions.md` | Réécrire autour du cycle |
| `docs/guides/recipes.md` | Vérifier qu'un exemple d'Action y figure et reste exécuté par `test_recipes.py` (F6) |

## Critère de fin

- [ ] Les 5 étapes du cycle ont chacune un exemple
- [ ] La phrase « the generated path is not an authorization mechanism » est présente
- [ ] Les 5 familles d'erreurs sont distinguées
- [ ] `useAction` vs appel direct : la différence est dite en une phrase
- [ ] Aucun exemple qui suggère que l'origine protège les données

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Vérifié : `origin.py` compare l'origine, il n'authentifie pas. |
| 2026-11-01 | `guides/actions.md` réécrit autour des 5 étapes. Ajouté : la phrase « the generated path is not an authorization mechanism », les 5 familles d'erreurs séparées (dont 401/403 par votre code), la note explicite que le contrôle d'origine est une protection CSRF et pas une autorisation, le mapping des types Python → TypeScript, `NEXY_ACTION_SECRET` / `__nexy__/action.key`. Les deux tests d'ancre suivent le nouveau titre (`#the-action-cycle`). Reste : un exemple par étape, le renvoi DOC-15 pour `revalidate`, la vérification de `recipes.md`. |
