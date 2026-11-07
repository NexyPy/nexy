# Rendu

Le rendu répond à une question : **qui produit le HTML et quand**. Nexy a quatre réponses et une par défaut.

**Pas sûr? Conservez SSR.** Modifiez une page uniquement lorsque vous pouvez en nommer la raison : un contenu qui change rarement (ISR), un widget qui nécessite le navigateur (île) ou une navigation de type application (CSR).

<!-- router:modular -->
> [!NOTE]
> Le routeur modulaire restitue chaque vue sur le serveur, avec des îlots où une vue les contient. ISR et CSR sont des modes de pages de fichiers : ils nécessitent le routeur basé sur les fichiers.
<!-- /router -->

## Comment ça marche

```diagram filename="Qui produit le HTML et quand"
SSR       request ──► server renders ────────────────► HTML ──► browser
ISR       request ──► cached HTML? ──► browser, regenerated in the background
CSR       request ──► document rendered by the server ──► browser takes over navigation
Islands   request ──► server renders the page ──► one widget hydrates on demand
```

## Les quatre modes

| | RSS | ISR | RSE | Îles |
|---|---|---|---|---|
| Les données sont lues | à chaque demande | à chaque régénération | dans le navigateur | à chaque demande |
| Le HTML vient de | le serveur | le serveur, puis un cache | le serveur pour le premier document, le navigateur ensuite | le serveur |
| JavaScript | uniquement pour les îles | uniquement pour les îles | le bundle de cadres | seulement l'île |
| Hydratation | aucun | aucun | tout le document | l'île |
| Cache | aucun | par URL, en mémoire | aucun | aucun |
| Décidé par | par défaut | `revalidate = N` dans la page | `useCSR = True` dans le projet | `directive` sur le composant |
| Céréales | page | page | **projet** | composant |

## Cycle de vie du rendu

Deux faits expliquent la plupart des surprises.

1. **Un projet est dans un seul mode.** `useCSR` choisit entre le mode serveur (SSR, ISR, îles, routes `.nexy`, `.md`, `.mdx`) et le mode client (routes framework et un routeur client). Les deux ne peuvent pas être mélangés : voir [mode serveur et mode client](../routing/fbr/modes.md).
2. **En mode serveur, le mode est par page.** Une page peut être mise en cache avec `revalidate`, une autre peut contenir une île, une troisième ne peut faire ni l'un ni l'autre.

Le mode client envoie toujours un vrai document : Nexy le restitue dans Node pour la première réponse, puis le navigateur reprend la navigation. Une page RSE n’est pas une page blanche en attente d’un bundle.

## Quand utiliser

- **Contenu, marketing, documentation** : SSR, plus ISR lorsque le contenu change rarement.
- **Une page essentiellement statique avec un widget interactif** : SSR avec une île.
- **Tableaux de bord, éditeurs, navigation de type application** : RSE.
- **Une page lue constamment et rarement modifiée** : ISR.

## Configuration

| Mode | Où |
|---|---|
| RSS | nulle part : c'est la valeur par défaut |
| ISR | `revalidate = 60` au début d'une page `.nexy` |
| RSE | `useCSR = True` dans `nexyconfig.py`, avec `useFF` défini |
| Îles | `directive="client:visible"` sur la balise du composant |

## Exemple

<!-- router:fbr,custom -->
```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

La même page sans la ligne d'introduction est SSR.
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/sales_view.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Rendered on every request</h1>
<Chart directive="client:visible" />
```

La vue est SSR et la carte est une île qui s'hydrate lorsqu'elle défile.
<!-- /router -->

## Limites

- **Il n'y a pas de mode SSG.** Nexy pré-rend le HTML au moment de la construction (composant HTML, documents client), mais le relit toujours via le serveur : pas de commande d'exportation, pas de dossier autonome à héberger de manière statique. Pour le contenu gelé, utilisez ISR avec une longue fenêtre.
- **ISR n'est pas un CDN.** Le cache réside dans le processus qui restitue la page ; plusieurs travailleurs gardent plusieurs caches. Voir [ISR](isr.md).
- **La RSE est une décision de projet.** Vous ne pouvez pas créer une page de RSE et conserver le reste de la RSE.
- **Les îles hydratent l'île, pas la page.** Une page dont les îles dépendent toutes les unes des autres est une page RSE déguisée.

## Prochaines étapes

- [SSR](ssr.md) : la valeur par défaut
- [ISR](isr.md) : mettre en cache une page par URL
- [CSR](csr.md) : navigation manuelle vers le navigateur
- [Îles](islands.md) : hydrater un widget
- [Performances](../deployment/performance.md)
