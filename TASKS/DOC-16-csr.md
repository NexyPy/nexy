# DOC-16 - CSR

| | |
|---|---|
| **Phase** | P3 - Rendu |
| **Statut** | `fait` |
| **Dépend de** | DOC-13 |
| **Débloque** | - |

## Objectif

Expliquer le rendu côté client sans le confondre avec « une page qui contient du JavaScript », et sans
laisser croire qu'il se choisit page par page.

## Squelette imposé (A1)

1. Definition · 2. How it works · 3. Rendering lifecycle · 4. When to use · 5. Configuration · 6. Example · 7. Limitations · 8. Related.

## Points obligatoires

- **CSR est un choix de projet, pas de page.** `useCSR` engage toute l'application : les deux modes
  ne se mélangent pas. La phrase « CSR does not require a SPA » du brief est **fausse dans Nexy** et
  ne doit pas être écrite : ce qui est vrai, c'est que la première réponse est un document rendu par
  le serveur, pas une coquille vide.
- **Ce que le serveur envoie** : le document complet rendu en Node (au build en production, à la
  demande via Vite en développement), plus les assets et la description de page.
- **Ce qui est perdu** : une route dynamique sans paramètre statique déclaré démarre d'une coquille
  (layouts autour d'une page vide) ; la page n'apparaît qu'après exécution du navigateur.
- **Configuration** : renvoie à `routing/fbr/modes.md` (`useCSR`) plutôt que de la redécrire.

## Fichiers

| Fichier | Action |
|---|---|
| `docs/rendering/csr.md` | Réécrire sur le squelette |
| `docs/routing/fbr/modes.md` | Vérifier qu'il ne contredit pas cette page (une seule description de `useCSR`) |

## Critère de fin

- [x] La page dit que CSR engage le projet entier, et n'affirme pas l'inverse
- [x] La page ne redécrit pas `useCSR` : elle renvoie à `modes.md`
- [x] Aucune contradiction entre les deux pages sur ce que `useCSR` autorise
- [x] Les 8 sections existent, dans l'ordre

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Risque de duplication avec `routing/fbr/modes.md` identifié. |
| 2026-10-31 | **Fait.** La prémisse du brief (« CSR se choisit page par page ») contredisait `modes.md` et `Config.useCSR` : corrigée ici et dans la page. Ajout de `getStaticParams()` - API réelle, jamais documentée (F14) - comme seule façon d'obtenir un document par valeur sur une route dynamique. `modes.md` relu : aucune contradiction, il garde le tableau des fichiers rejetés. |
