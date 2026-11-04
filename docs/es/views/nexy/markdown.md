# Rebaja y MDX

Dos formatos para páginas de contenido: `.md` cuando solo necesitas Markdown, `.mdx` cuando necesitas componentes.

## `.md`: Markdown puro

Un archivo `.md` es contenido puro. Nexy lo representa con `cmarkgfm` (GFM), agrega ID de encabezado, deriva un
tabla de contenidos y la envuelve en el `layout.*` más cercano.

```md filename=""
# About

Nexy is a fullstack Python meta-framework.
```

- La materia frontal en `.md` no se utiliza como lógica de Python. Si necesita lógica de servidor, utilice `.nexy`.
- El ajuste de diseño, las páginas de error y los segmentos dinámicos funcionan de la misma manera que otras páginas.

## `.mdx`: Markdown con componentes

Los archivos `.mdx` son compilados por **Vite**, a través del proceso de ruta del marco (React o Preact). pitón
sólo escribe el envoltorio fino que sirve a la ruta; nunca compila ni renderiza MDX.
Los componentes son renderizados por el marco, renderizados por el servidor como otras rutas de componentes, y
prerenderizado a HTML por `nx build`.

- Requiere que `useFF` sea React o Preact.
- Requiere los paquetes opcionales `@mdx-js/rollup`, `remark-gfm` y `@mdx-js/react` (y
  `@mdx-js/esbuild` para la construcción). Vite te dice cuál falta.
- El marco se detecta automáticamente a partir de las importaciones: Preact cuando el archivo se importa `preact`, React
  de lo contrario.

> [!NOTA]
> use `.nexy` si necesita lógica de Python al frente.

## Próximos pasos

- [archivos .nexy](README.md): el formato de página nativo
- [Vistas](../README.md): elige un formato
- [i18n](../../guides/i18n.md): internacionalización