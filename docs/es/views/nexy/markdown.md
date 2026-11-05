# Markdown y MDX

Dos formatos para páginas de contenido: `.md` cuando solo necesitas Markdown, `.mdx` cuando necesitas componentes.

## `.md`: puro Markdown

Un archivo `.md` es puro contenido. Nexy lo presenta como Markdown con sabor a GitHub (tablas, listas de tareas, tachados, enlaces), agrega ID de encabezado, deriva una tabla de contenido y la envuelve en el `layout.*` más cercano.

```md filename="src/rutas/about.md"
# About

Nexy is a fullstack Python meta-framework.
```

- El frontmatter en `.md` no se utiliza como lógica Python. Si necesita lógica de servidor, utilice `.nexy`.
- El HTML sin formato en una página `.md` se muestra como texto, nunca se ejecuta. Si necesita HTML, utilice `.nexy`.
- El ajuste de diseño, las páginas de error y los segmentos dinámicos funcionan de la misma manera que otras páginas.

## `.mdx`: Markdown con componentes

Los archivos `.mdx` son compilados por **Vite**, a través de la canalización de ruta del marco (React o Preact). Python solo escribe el contenedor delgado que sirve a la ruta; nunca se compila ni renderiza MDX a sí mismo. Los componentes se procesan mediante el marco, se procesan en el servidor como otras rutas de componentes y se procesan previamente en HTML mediante `nx build`.

- Requiere que `useFF` sea React o Preact.
- Requiere los paquetes opcionales `@mdx-js/rollup`, `remark-gfm` y `@mdx-js/react` (y `@mdx-js/esbuild` para la compilación). Vite te dice cuál falta.
- El marco se detecta automáticamente a partir de importaciones: Preact cuando el archivo importa `preact`, React en caso contrario.

> [!NOTE]
> use `.nexy` si necesita Python lógica al frente.

## Próximos pasos

- [Archivos .nexy](README.md): el formato de página nativo
- [Vistas](../README.md): elige un formato
- [i18n](../../guides/i18n.md): internacionalización
