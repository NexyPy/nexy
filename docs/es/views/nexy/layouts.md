# diseño.nexy

El archivo de diseño del modo servidor (`useCSR = False`). El raíz posee el documento HTML.

## Diseño raíz

```nexy filename="src/rutas/layout.nexy"
---
from nexy import Vite

children: prop[NexyElement]
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My app</title>
  <Vite />
</head>
<body>
  <main>{{ children | safe }}</main>
</body>
</html>
```

- `<!DOCTYPE html>`, `<html>`, `<head>` y `<body>` viven aquí y en ningún otro lugar.
- `<Vite />` inyecta los scripts y estilos del cliente una vez, en `<head>`.
- `{{ children | safe }}` es donde se representa la página o el siguiente diseño anidado.

## Diseños anidados

Un `layout.nexy` en un subdirectorio envuelve ese subárbol y lo representa dentro de su padre. no se repite
las etiquetas del documento:

```nexy filename="src/rutas/blog/layout.nexy"
---
children: prop[NexyElement]
---
<nav>...</nav>
<article>{{ children | safe }}</article>
```

`blog/[slug].nexy` se representa como `layout.nexy > blog/layout.nexy > page`.

## Componentes e islas

Un diseño puede importar `.nexy` componentes (un encabezado, un pie de página) y componentes del cliente. un cliente
El componente en un diseño es una [isla](../../rendering/islands.md) como cualquier otra:

```nexy
---
from "@/components/Header.nexy" import Header
from "@/components/theme/theme.tsx" import Theme
---
<Header />
<Theme directive="client:idle" />
```

## Sin diseño

Un proyecto sin `layout.nexy` aún responde con un documento válido: Nexy vuelve al mínimo
shell con `<!DOCTYPE html>`, el meta de la ventana gráfica y las etiquetas Vite. Añade un diseño tan pronto como lo necesites
un título, fuentes o navegación.

## En el enrutador modular

Los controladores eligen sus vistas, por lo que ellos mismos componen el diseño:

```python
return useViews("src/apps/layout.nexy", context={"children": useViews("src/apps/app_view.nexy")})
```

## Lo que no puede hacer

- No puede coexistir con `layout.tsx`, `layout.vue` o `layout.svelte`: un proyecto en modo servidor tiene
  sin rutas de cliente ([modos](../../routing/fbr/modes.md)).
- No se ejecuta en el cliente: utiliza una isla para interactividad.

## Próximos pasos

- [Diseños](../../routing/fbr/layouts/README.md)
- [Herencia](../../routing/fbr/inheritance.md)
- [archivos .nexy](README.md)