# Diseños de interfaz

Un **Layout** es un contenedor que define la estructura compartida alrededor de una o más páginas. Los diseños permiten una experiencia "similar a una aplicación" al preservar el estado y evitar recargas de página completa durante la navegación.

## Lógica de anidamiento

Los diseños siguen una estructura jerárquica basada en el árbol de directorios en `src/routes/`.

1.  **Diseño raíz**: Cada proyecto tiene un diseño raíz (por ejemplo, `src/routes/layout.nexy`). Este es el único diseño responsable de definir el shell del documento: `<html>`, `<head>` y `<body>`.
2.  **Diseños anidados**: cualquier carpeta puede contener su propio archivo `layout.*`. Este diseño envuelve todas las páginas y subdiseños dentro de esa carpeta.
3.  **Herencia**: una página está empaquetada por todos los diseños desde la raíz hasta su propia carpeta.

```text
src/routes/
├─ layout.tsx            root: <html>, <head>, <body>
├─ index.tsx             root > page
└─ dashboard/
   ├─ layout.tsx         nested: the dashboard menu
   └─ settings.tsx       root > dashboard > page
```

Un diseño anidado dibuja solo su parte de la interfaz de usuario y coloca la página donde va `children`:

```tsx filename="src/rutas/dashboard/layout.tsx"
import type { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="dashboard">
      <nav>Dashboard</nav>
      <main>{children}</main>
    </div>
  );
}
```

## Estado compartido y composición

Los diseños están diseñados para ser estables. En el modo cliente, al navegar entre dos páginas que comparten el mismo diseño, el diseño **no** se vuelve a representar; sólo cambia el contenido secundario. En modo servidor cada navegación es un documento nuevo.

- **Ranuras**: los diseños proporcionan una ranura donde se inyecta la página anidada: `children` en JSX y el accesorio `children` en un diseño `.nexy`.
- **Preservación del estado**: debido a que el diseño permanece montado, cualquier estado que contenga (por ejemplo, una consulta de búsqueda en un encabezado) se conserva durante la navegación.

La misma ranura en un diseño `.nexy`:

```nexy filename="src/rutas/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children }}</body>
</html>
```

El campo de búsqueda a continuación mantiene lo que el usuario escribió mientras se mueve entre las páginas del panel, porque el diseño que lo contiene nunca se desmonta:

```tsx filename="src/rutas/dashboard/layout.tsx"
import { useState, type ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState("");
  return (
    <>
      <input value={query} onChange={(event) => setQuery(event.target.value)} />
      {children}
    </>
  );
}
```

## Restricciones estáticas

Para las rutas preprocesadas (SSG), el diseño raíz no puede depender de datos en el momento de la solicitud, como cookies o encabezados. Debe ser representable como un caparazón estático que luego el cliente hidrata.

En su lugar, lea el tema desde el navegador, en un script del shell estático:

```tsx filename="src/rutas/layout.tsx"
import type { ReactNode } from "react";

const theme = `document.documentElement.dataset.theme =
  localStorage.getItem("theme") ?? "light";`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <head>
        <script dangerouslySetInnerHTML={{ __html: theme }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## Implementación del marco

La implementación de ranuras y anidamientos varía ligeramente según el marco. Consulte la guía **Diferencias** para la tecnología elegida:

- [React Diferencias](../react/differences.md)
- [Vue Diferencias](../vue/differences.md)
- [Svelte Diferencias](../svelte/differences.md)
- [Solid Diferencias](../solid/differences.md)
- [Preact Diferencias](../preact/differences.md)
