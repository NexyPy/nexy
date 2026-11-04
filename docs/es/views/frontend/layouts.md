# Diseños de interfaz

Un **Layout** es un contenedor que define la estructura compartida alrededor de una o más páginas. Los diseños permiten una experiencia "similar a una aplicación" al preservar el estado y evitar recargas de página completa durante la navegación.

## Lógica de anidamiento

Los diseños siguen una estructura jerárquica basada en el árbol de directorios en `src/routes/`.

1.  **Diseño raíz**: Cada proyecto tiene un diseño raíz (por ejemplo, `src/routes/layout.nexy`). Este es el único diseño responsable de definir el shell del documento: `<html>`, `<head>` y `<body>`.
2.  **Diseños anidados**: cualquier carpeta puede contener su propio archivo `layout.*`. Este diseño envuelve todas las páginas y subdiseños dentro de esa carpeta.
3.  **Herencia**: Una página está empaquetada por todos los diseños desde la raíz hasta su propia carpeta.

## Estado compartido y composición

Los diseños están diseñados para ser estables. Al navegar entre dos páginas que comparten el mismo diseño, el diseño **no** se vuelve a representar; sólo cambia el contenido secundario.

- **Ranuras**: Los diseños proporcionan una "ranura" (generalmente `children` en JSX o `{{ content }}` en Jinja2) donde se inyecta la página anidada.
- **Preservación del estado**: debido a que el diseño permanece montado, cualquier estado que contenga (por ejemplo, una consulta de búsqueda en un encabezado) se conserva durante la navegación.

## Restricciones estáticas

Para las rutas preprocesadas (SSG), el diseño raíz no puede depender de datos en el momento de la solicitud, como cookies o encabezados. Debe ser representable como un caparazón estático que luego el cliente hidrata.

## Implementación del marco

La implementación de ranuras y anidamientos varía ligeramente según el marco. Consulte la guía **Diferencias** para la tecnología elegida:

- [Reaccionar diferencias](../react/differences.md)
- [Diferencias de Vue](../vue/differences.md)
- [Diferencias esbeltas](../svelte/differences.md)
- [Diferencias sólidas](../solid/differences.md)
- [Diferencias previas](../preact/differences.md)