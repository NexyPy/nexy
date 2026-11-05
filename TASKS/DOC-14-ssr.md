# DOC-14 - SSR

| | |
|---|---|
| **Phase** | P3 - Rendu |
| **Statut** | `fait` |
| **Dépend de** | DOC-13 |
| **Débloque** | - |

## Objectif

Expliquer le mode par défaut avec assez de précision pour qu'un lecteur sache quand il s'applique, ce qui est envoyé au navigateur, et ce qu'il coûte.

## Squelette imposé (A1)

1. **Definition** - le serveur produit le HTML à chaque requête.
2. **How it works** - où les données sont lues, où la vue est évaluée.
3. **Rendering lifecycle** - requête → handler → données → rendu → HTML → navigateur.
4. **When to use** - contenu personnalisé, données fraîches, SEO.
5. **Configuration** - le défaut ne se configure pas ; dire comment on en sort.
6. **Example** - une page `.nexy` minimale.
7. **Limitations** - coût par requête, pas de cache, dépendance à la latence des données.
8. **Related** - ISR, CSR, islands.

## Contexte utile

- C'est le défaut : la page doit le dire dès la première phrase, et dire aussi que **rien n'est à faire** pour l'obtenir.
- Ne pas confondre SSR et « pas de JavaScript » : une page SSR peut embarquer des îlots (DOC-17).
- Ne pas introduire de SSG séparé : Nexy n'en a pas (DOC-13).

## Fichiers

| Fichier | Action |
|---|---|
| `docs/rendering/ssr.md` | Réécrire sur le squelette |

## Critère de fin

- [x] Les 8 sections existent, dans l'ordre, avec ces titres
- [x] La première phrase dit que c'est le défaut et qu'il ne demande aucune configuration
- [x] La section Limitations nomme le coût par requête et l'absence de cache
- [x] Aucune promesse de performance chiffrée sans renvoi à `deployment/performance.md`

## Journal

| Date | Note |
|---|---|
| 2026-10-31 | Tâche créée. |
| 2026-10-31 | **Fait.** Réécrite sur le squelette A1. Deux corrections de fond par rapport à l'ancienne page : (a) une route composant n'est pas « rendue à chaque requête » - en production, sans layout, c'est le HTML du build qui est servi puis hydraté, sinon le composant monte côté navigateur ; (b) le streaming n'est pas conditionnel, toute réponse est un `StreamingResponse`, mais il ne sert que si le composant yield (F17). |
