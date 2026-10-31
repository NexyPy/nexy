# DOC-16 — CSR

| | |
|---|---|
| **Phase** | P3 — Rendu |
| **Statut** | `prêt` |
| **Dépend de** | DOC-13 |
| **Débloque** | — |

## Objectif

Expliquer le rendu côté client sans laisser croire qu'il impose une SPA, et sans le confondre avec « une page qui contient du JavaScript ».

## Squelette imposé (A1)

1. Definition · 2. How it works · 3. Rendering lifecycle · 4. When to use · 5. Configuration · 6. Example · 7. Limitations · 8. Related.

## Points obligatoires

- **CSR n'implique pas SPA.** Le mode se choisit page par page ; une page CSR dans une application par ailleurs SSR est un cas normal.
- **Ce que le serveur envoie** : un document minimal, puis le bundle client prend le relais.
- **Ce qui est perdu** : le HTML initial n'existe pas pour les crawlers qui n'exécutent pas JavaScript, et le premier affichage dépend du téléchargement du bundle.
- **Configuration** : renvoie à `routing/fbr/modes.md` (`useCSR`) plutôt que de la redécrire.

## Fichiers

| Fichier | Action |
|---|---|
| `docs/rendering/csr.md` | Réécrire sur le squelette |
| `docs/routing/fbr/modes.md` | Vérifier qu'il ne contredit pas cette page (une seule description de `useCSR`) |

## Critère de fin

- [ ] La phrase « CSR does not require a SPA » est présente et expliquée
- [ ] La page ne redécrit pas `useCSR` : elle renvoie à `modes.md`
- [ ] Aucune contradiction entre les deux pages sur ce que `useCSR` autorise
- [ ] Les 8 sections existent, dans l'ordre

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. Risque de duplication avec `routing/fbr/modes.md` identifié. |
