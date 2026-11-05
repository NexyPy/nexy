# Metadatos de la página

Una página nombra su título y sus etiquetas de encabezado, y el diseño raíz las escribe una vez.

## Dilo en la pagina

Para una página que nunca cambia, escribe un literal en la parte superior de la portada:

```nexy filename="src/rutas/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

Cuando el título depende de los datos, llame a `setMetadata` en su lugar:

```nexy filename="src/rutas/publicaciones/[slug].nexy"
---
from nexy import notFound, setMetadata

from src.posts import find

slug: prop[str]
post = find(slug) or notFound()
setMetadata(title=post.title, description=post.summary, og={"image": post.cover})
---
<h1>{{ post.title }}</h1>
```

Un controlador modular llama a `setMetadata(...)` antes de devolver `useViews(...)`.

## Escríbelo en el diseño.

El diseño raíz posee el `<head>`. Una línea escribe lo que decía la página, escapada:

```nexy filename="src/rutas/layout.nexy"
---
from nexy import setMetadata, useMetadata

children: prop[NexyElement]
setMetadata(title_template="%s | My site")
---
<!DOCTYPE html>
<html>
  <head>
    {{ useMetadata().html() }}
  </head>
  <body>{{ children }}</body>
</html>
```

Una página se ejecuta antes que sus diseños, por lo que el diseño encuentra lo que la página solicitó. Una página que no dice nada obtiene el `useTitle` de su `nexyconfig.py` y ninguna otra etiqueta.

## los campos

| Campo | Escrito como |
|---|---|
| `title` | `<title>`; con `title_template="%s \| My site"` el título se pone en el `%s` |
| `description` | `<meta name="description">` |
| `canonical` | `<link rel="canonical">` |
| `robots` | `<meta name="robots">`, por ejemplo `"noindex"` |
| `icon` | `<link rel="icon">` |
| `og` | uno `<meta property="og:...">` por clave: `{"image": "/cover.png"}` da `og:image` |
| `twitter` | uno `<meta name="twitter:...">` por clave |
| `extra` | una lista de dictados de atributos, uno `<meta>` cada uno: `[{"name": "theme-color", "content": "#fff"}]` |

Una llamada posterior reemplaza un valor; `og`, `twitter` y `extra` se suman a lo que hay allí. Un campo que no existe genera `TypeError`, por lo que un error tipográfico no hace nada en silencio.

## Seguro por defecto

Cada valor tiene un formato de escape HTML, por lo que un título creado a partir de una URL o de la base de datos no puede cerrar la etiqueta e inyectar un script. Un valor se escapa una vez, cuando el diseño llama a `html()`: no escape usted mismo.

## Próximos pasos

- [Páginas](README.md)
- [Diseños](../layouts/README.md)
- [Páginas de error](../errors/README.md)
