# Wie funktionieren Seitenübergänge?

Nexy verwendet die View Transitions API des Browsers für die Client-Navigation, sodass ein unterstützter Browser den Seitenwechsel animiert, es sei denn, der Besucher bevorzugt eine reduzierte Bewegung.

## Wenn ein Übergang ausgeführt wird

Das erste Dokument ist eine normale Serverantwort und hat keinen Übergang. Von da an vertauscht jede vom Client-Router verarbeitete Navigation die Seite innerhalb von `document.startViewTransition()`: einen Link zu einer Client-Route, `router.push()` oder `router.replace()` und die Schaltflächen „Zurück“ und „Vorwärts“. Der Router rendert zuerst die nächste Seite und ihre Layouts und verschiebt dann die URL, sodass die neue Seite bereit ist, bevor sie angezeigt wird.

React, Preact, Solid, Vue und Svelte teilen sich denselben Router, sodass das Verhalten bei allen fünf Adaptern gleich ist. Es gibt keine Einstellung zum Aktivieren von Übergängen.

## Wenn es zurückfällt

- Ein Browser ohne `startViewTransition()` rendert die Seite direkt.
- Mit `prefers-reduced-motion: reduce` rendert der Router die Seite direkt.
- Ein von einer neueren Navigation übersprungener Übergang protokolliert keinen Fehler: Die Seite ist immer noch korrekt.

Die URL, der Verlauf, die Bildlaufposition und das Ereignis `nexy:navigated` verhalten sich mit oder ohne Übergang gleich.

## Gestalten Sie den Übergang

Nexy liefert kein Animations-CSS. Der Browser wendet seine standardmäßige Überblendung an, die Sie in Ihrem eigenen Stylesheet ersetzen können:

```css
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 250ms;
}
```

## Nächste Schritte

- [Verknüpfen und Navigieren](linking-and-navigating.md)
- [Haken](hooks.md)
