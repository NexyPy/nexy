# Rutas dinámicas

Un segmento de ruta escrito entre corchetes coincide con cualquier valor y se lo entrega a la página o al controlador.

## Segmentos dinámicos

`blog/[slug].nexy` sirve a `/blog/{slug}`. En una página, declara el segmento como una propiedad; en un controlador Python, tómalo como argumento.

```nexy filename="src/rutas/blog/[slug].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/rutas/api/usuarios/[id].py"
async def GET(id: int):
    return {"id": id}
```

## Segmentos escritos

La anotación decide el tipo.

| Donde | Conversión |
|---|---|
| `.py` controlador | cualquier FastAPI tipo de anotación (`int`, `UUID`, `Enum`...) |
| `.nexy` página | `int` y `float` se convierten; todo lo demás sigue siendo una cuerda |

Un valor que no coincide con la anotación es **no encontrado**: `/api/users/abc` responde `404`, porque una ruta dinámica captura cualquier URL y una URL que no se puede convertir simplemente no existe. Ver [Validación y errores](../handlers/validation-and-errors.md).

## Segmentos generales

`docs/[...path].nexy` sirve a `/docs/{path:path}`. Los segmentos restantes llegan como una sola cadena, incluidas las barras.

```nexy filename="src/rutas/docs/[...ruta].nexy"
---
path: prop[str]
---
<pre>{{ path }}</pre>
```

`/docs/a/b/c` da `path == "a/b/c"`.

## Grupos de rutas

Un directorio entre paréntesis organiza archivos sin aparecer en la URL. Todavía participa en [la herencia](../inheritance.md): sus `layout.*` y `dependencies.py` se aplican a lo que está dentro.

```text
src/routes/
├─ (marketing)/
│  ├─ layout.nexy        applies to the pages in the group
│  ├─ pricing.nexy       /pricing
│  └─ about.nexy         /about
└─ (app)/
   └─ dashboard.nexy     /dashboard
```

Utilice grupos para dar diferentes diseños a diferentes secciones sin cambiar sus URL.

## Prioridad

Las rutas estáticas ganan a las dinámicas y las dinámicas a las generales: `/blog/new` coincide con `blog/new.nexy` antes de `blog/[slug].nexy`.

## Un archivo por URL

Se registran dos archivos que se resuelven en la misma URL. No coloque `blog.nexy` al lado de `blog/index.nexy`, ni mezcle `index.nexy` y `index.py` para la misma ruta.

## Próximos pasos

- [Páginas](README.md)
- [Páginas de error](../errors/README.md)
- [Convenciones de archivos](../../../reference/file-conventions.md)
