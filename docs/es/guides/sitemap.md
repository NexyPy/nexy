# ¿Cómo agrego un sitemap.xml y robots.txt a un sitio Nexy?

Establezca `useSiteUrl` en `nexyconfig.py`: Nexy luego sirve `/sitemap.xml`, que enumera todas las páginas estáticas del proyecto, y un `/robots.txt` que apunta a los motores de búsqueda.

## Enciéndelo con `useSiteUrl`

`useSiteUrl` es el origen público del sitio, el que ven los motores de búsqueda:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSiteUrl = "https://example.com"
```

`nx dev` y `nx start` luego responden ambos archivos. Sin `useSiteUrl` ninguno existe, por lo que un proyecto nunca publica la URL de su servidor de desarrollo por error.

## Lo que enumera el mapa del sitio

El mapa del sitio proporciona cada página como una URL absoluta en `useSiteUrl`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/</loc></url><url><loc>https://example.com/about</loc></url></urlset>
```

Una ruta aparece cuando responde HTML a un `GET` en una ruta fija:

<!-- router:fbr,custom -->
- se enumera una página (`.nexy`, `.md`, `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte`);
- una página dinámica, como `src/routes/users/[id].nexy`, queda fuera: Nexy no puede conocer sus valores;
- un controlador de ruta Python responde a JSON, por lo que se omite.
<!-- /router -->

<!-- router:modular -->
- se enumera una ruta de controlador que responde a HTML, con `@UseResponse(response_class=HTMLResponse)`;
- una ruta con un parámetro de ruta, como `/users/{id}`, queda fuera: Nexy no puede conocer sus valores;
- se omite una ruta que responde a JSON.
<!-- /router -->

También se omite una ruta oculta del esquema API (`include_in_schema=False`).

## El `robots.txt` al que sirve

```text
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

## Escribe el tuyo propio en su lugar

Su propio archivo siempre gana y Nexy nunca lo sobrescribe:

- `public/robots.txt` o `public/sitemap.xml` se sirve tal como está, de la misma manera que cada archivo de `public/`;
- una ruta del proyecto en `/robots.txt` o `/sitemap.xml` mantiene su camino.

Escriba su propio mapa del sitio para enumerar páginas dinámicas, como una URL por publicación de blog.

## Próximos pasos

- [Metadatos de la página](../routing/fbr/pages/metadata.md): el título y la descripción que muestran los motores de búsqueda
- [Configuración](../reference/config.md): cada configuración de `nexyconfig.py`
- [Implementar](../deployment/README.md): servir el proyecto en producción
