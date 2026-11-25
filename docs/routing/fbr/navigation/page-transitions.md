# How do page transitions work?

Nexy uses the browser's View Transitions API for client navigations, so a supported browser animates the page swap unless the visitor prefers reduced motion.

## When a transition runs

The first document is a normal server response and has no transition. From then on, each navigation handled by the client router swaps the page inside `document.startViewTransition()`: a link to a client route, `router.push()` or `router.replace()`, and the back and forward buttons. The router renders the next page and its layouts first, then moves the URL, so the new page is ready before it is shown.

React, Preact, Solid, Vue and Svelte share the same router, so the behaviour is the same in all five adapters. There is no setting to enable transitions.

## When it falls back

- A browser without `startViewTransition()` renders the page directly.
- With `prefers-reduced-motion: reduce`, the router renders the page directly.
- A transition skipped by a newer navigation does not log an error: the page is still correct.

The URL, history, scroll position and `nexy:navigated` event behave the same way with or without a transition.

## Style the transition

Nexy ships no animation CSS. The browser applies its default cross-fade, which you can replace in your own stylesheet:

```css
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 250ms;
}
```

## Next steps

- [Linking and navigating](linking-and-navigating.md)
- [Hooks](hooks.md)
