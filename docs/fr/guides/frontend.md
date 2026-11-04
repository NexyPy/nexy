# Front-end

Nexy ne livre pas son propre système de composants au client. Il s'appuie sur Vite : React, Vue, Svelte,
Solid et Preact sont tous pris en charge et les pages Vanilla fonctionnent sans aucun framework client.

## Activer un framework

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()   # vue(), svelte(), solid(), preact()
```

`useVite` est par défaut `True` ; conservez-le lorsqu’un framework est configuré.

## Fichiers d'itinéraire

| Extension | Rendu |
|---|---|
| `.nexy`, `.md` | par Nexy au moment de la demande |
| `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte` | par le framework client ; pré-rendu au format HTML au moment de la construction, puis repris par le bundle client |

Une route framework est une page normale, pas un îlot réservé au client : le code HTML existe avant l'exécution du bundle,
donc la première peinture n'attend pas JavaScript.

Configuration par framework : [React](../views/react/differences.md), [Vue](../views/vue/differences.md),
[Svelte](../views/svelte/differences.md), [Solide](../views/solid/differences.md),
[Préact](../views/preact/differences.md).

## Développement

`nx dev` démarre un serveur sur un port :

1. l'application recompile les routes que vous modifiez, serveur et client ;
2. Vite fonctionne sur un port interne et sert des modules de framework ;
3. Nexy proxy les points de terminaison de Vite via sa propre origine.

Le navigateur ne parle qu'au port `3000`. Il n'y a pas de deuxième URL à ouvrir ni de CORS à configurer.

## Construire

`nx build` produit :

- HTML pré-rendu pour les routes du framework ;
- le pack client, avec des actifs sous `__nexy__/client/` ;
- les routes Python compilées.

Vite gère le bundle client ; Le HTML SSR est produit par fichier par esbuild.

> [!REMARQUE]
> une route dont le rendu du serveur échoue est signalée comme une route réservée au client au lieu de
> échec de toute la construction.

## Style

`nexy new` demande un mode de style et le configure pour le framework client que vous choisissez : Tailwind,
UnoCSS ou CSS simple. Les jetons de design (couleurs, polices, thème sombre) sont des variables CSS dans
`src/globale.css`, le fichier créé par l'échafaudage.

| Mode | Les pages de démarrage sont écrites avec |
|---|---|
| Tailwind, UnoCSS | classes utilitaires dans le balisage, avec les jetons mappés aux noms de classe |
| CSS simple | noms de classes sémantiques et CSS dans `src/globale.css` |

Suivez le mode de votre projet lorsque vous ajoutez une page : classes utilitaires dans un projet utilitaire, CSS dans un
un en CSS simple. Conservez le CSS du composant que les utilitaires ne peuvent pas exprimer dans le bloc `<style>` du composant.
Dans un projet serveur (`.nexy` pages) UnoCSS lit les fichiers `.nexy` des classes ; Tailwind les trouve
tout seul.

## Polices, images, scripts

Placez les fichiers statiques dans `public/` - ils sont servis à partir de `/` à la fois en développement et en production.

## Prochaines étapes

- [Vues](../views/README.md) : choisissez un format de page
- [Config](../reference/config.md) : `useFF`, `useVite`, alias
- [Deploy](../deployment/README.md) : ce que produit le build