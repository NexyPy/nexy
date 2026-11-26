# ¿Cómo funcionan las transiciones de página?

Nexy utiliza la API View Transitions del navegador para la navegación del cliente, por lo que un navegador compatible anima el intercambio de páginas a menos que el visitante prefiera un movimiento reducido.

## Cuando se ejecuta una transición

El primer documento es una respuesta normal del servidor y no tiene transición. A partir de entonces, cada navegación manejada por el enrutador cliente intercambia la página dentro de `document.startViewTransition()`: un enlace a una ruta del cliente, `router.push()` o `router.replace()`, y los botones de avance y retroceso. El enrutador muestra primero la página siguiente y sus diseños, luego mueve la URL, de modo que la nueva página esté lista antes de mostrarse.

React, Preact, Solid, Vue y Svelte comparten el mismo enrutador, por lo que el comportamiento es el mismo en los cinco adaptadores. No hay ninguna configuración para habilitar las transiciones.

## cuando vuelve a caer

- Un navegador sin `startViewTransition()` muestra la página directamente.
- Con `prefers-reduced-motion: reduce`, el enrutador representa la página directamente.
- Una transición omitida por una navegación más reciente no registra un error: la página sigue siendo correcta.

La URL, el historial, la posición de desplazamiento y el evento `nexy:navigated` se comportan de la misma manera con o sin transición.

## Dale estilo a la transición

Nexy no incluye CSS de animación. El navegador aplica su fundido cruzado predeterminado, que puedes reemplazar en tu propia hoja de estilo:

```css
::view-transition-old(root),
::view-transition-new(root) {
  animation-duration: 250ms;
}
```

## Próximos pasos

- [Vincular y navegar](linking-and-navigating.md)
- [Ganchos](hooks.md)
