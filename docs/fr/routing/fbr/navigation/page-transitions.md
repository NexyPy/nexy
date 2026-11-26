# Comment fonctionnent les transitions de pages ?

Nexy utilise l'API View Transitions du navigateur pour les navigations des clients, de sorte qu'un navigateur pris en charge anime l'échange de page à moins que le visiteur ne préfère un mouvement réduit.

## Quand une transition s'effectue

Le premier document est une réponse normale du serveur et ne comporte aucune transition. Dès lors, chaque navigation gérée par le routeur client permute la page à l'intérieur de `document.startViewTransition()` : un lien vers une route client, `router.push()` ou `router.replace()`, et les boutons Précédent et Suivant. Le routeur affiche d'abord la page suivante et ses mises en page, puis déplace l'URL afin que la nouvelle page soit prête avant d'être affichée.

React, Preact, Solid, Vue et Svelte partagent le même routeur, le comportement est donc le même sur les cinq adaptateurs. Il n'y a aucun paramètre pour activer les transitions.

## Quand il retombe

- Un navigateur sans `startViewTransition()` affiche directement la page.
- Avec `prefers-reduced-motion: reduce`, le routeur restitue directement la page.
- Une transition ignorée par une navigation plus récente n'enregistre pas d'erreur : la page est toujours correcte.

L'URL, l'historique, la position de défilement et l'événement `nexy:navigated` se comportent de la même manière avec ou sans transition.

## Styliser la transition

Nexy ne fournit aucun CSS d'animation. Le navigateur applique son fondu enchaîné par défaut, que vous pouvez remplacer dans votre propre feuille de style :

```css
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 250ms;
}
```

## Prochaines étapes

- [Liens et navigation](linking-and-navigating.md)
- [Crochets](hooks.md)
