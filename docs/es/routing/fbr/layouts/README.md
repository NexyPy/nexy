# Diseños

Un diseño envuelve cada página debajo de su directorio. Anidación de diseños: la página se representa dentro del diseño de su directorio, que se representa dentro del diseño del directorio principal, hasta el diseño raíz.

Hay una página por tipo de archivo de diseño:

| Archivo | Modo | Posee el documento HTML | Página |
|---|---|---|---|
| `layout.nexy` | servidor (`useCSR = False`) | sí, en la raíz | [layout.nexy](../../../views/nexy/layouts.md) |
| `layout.tsx` | cliente (`useCSR = True`) | sí, en la raíz (React, Solid, Preact) | [React](../../../views/react/differences.md), [Solid](../../../views/solid/differences.md), [Preact](../../../views/preact/differences.md) |
| `layout.vue` | cliente | sí, en la raíz | [layout.vue](../../../views/vue/differences.md) |
| `layout.svelte` | cliente | sí, en la raíz | [layout.svelte](../../../views/svelte/differences.md) |

Un proyecto utiliza una familia. `layout.nexy` y `layout.tsx` no pueden vivir en el mismo proyecto: el modo servidor tiene diseños `.nexy` y el modo cliente tiene diseños de marco. Consulte [Modo servidor y modo cliente](../modes.md).

## Cómo el navegador se hace cargo del documento

En modo cliente, Nexy representa el diseño raíz en Node, por lo que la primera respuesta es un documento completo. Luego, el navegador se hace cargo de una de dos maneras:

| Marco | Adquisición | Qué significa |
|---|---|---|
| React, Solid | **hidratación** de todo el documento | el HTML del servidor se reutiliza tal cual |
| Preact, Vue, Svelte | **adquisición del cuerpo** | el marco construye el cuerpo de la página y lo intercambia por el que envió el servidor |

Preact, Vue y Svelte no pueden hidratar un documento completo: Preact `hydrate` construye un segundo elemento `<html>`, el compilador de Vue descarta un `<script>` de una plantilla de cliente, y Svelte no puede crear `<html>`, `<head>` o `<body>` en el navegador. Entonces, para ellos los atributos `<html>`, `<head>` y `<body>` son ​​los que envió el servidor, y el navegador solo construye el cuerpo. En la práctica:

- Coloque el título, las metaetiquetas, las fuentes y el script del tema en el diseño raíz: el servidor los representa y permanecen como están.
- El servidor aplica un enlace en `<html>`, `<head>` o `<body>` (por ejemplo, una clase reactiva), pero no se actualiza en el navegador. Cámbialos desde un guión, como lo hace el guión del tema.
- El navegador renderiza el cuerpo desde cero en lugar de reutilizar el marcado del servidor, por lo que el cuerpo se reemplaza una vez, en la misma tarea que el primer renderizado.

## El diseño raíz

El diseño raíz es `src/routes/layout.<ext>`. Es creado por `nx new` y es el único lugar donde escribe `<!DOCTYPE html>`, `<html>`, `<head>` y `<body>` (cada framework y `.nexy`). Las páginas y los diseños anidados nunca los repiten.

```text
src/routes/
├─ layout.*              root: the document
├─ index.*
└─ dashboard/
   ├─ layout.*           nested: UI only
   ├─ index.*
   └─ settings.*
```

`dashboard/index` se representa como `root layout > dashboard layout > page`.

## Grupos de rutas

Un directorio entre paréntesis puede tener su propio diseño sin cambiar las URL:

```text
src/routes/
├─ layout.nexy
├─ (marketing)/
│  ├─ layout.nexy        wraps /pricing and /about only
│  ├─ pricing.nexy
│  └─ about.nexy
└─ (app)/
   └─ dashboard.nexy     only the root layout
```

## persistencia

En modo cliente, un diseño permanece montado mientras el usuario navega entre las páginas que lo comparten: se mantienen su DOM, estado y posición de desplazamiento. En modo servidor cada navegación es un documento nuevo.

## Próximos pasos

- [diseño.nexy](../../../views/nexy/layouts.md)
- [diseño.tsx](../../../views/react/differences.md)
- [Herencia](../inheritance.md)
