# Cree una aplicación de notas con Nexy, parte 2: páginas y diseños

La parte 2 agrega la página que enumera las notas y muestra cómo el diseño las envuelve en el documento HTML.

**Antes de comenzar:** el proyecto de la [parte 1](create-the-project.md), con `nexy dev` ejecutándose.

## Agregar la página de notas

<!-- router:fbr,custom -->
Una página es un archivo en `src/routes/` y su ruta es su URL. Crea la página de notas:

```nexy filename="src/rutas/notas/index.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

`notes/index.nexy` responde `/notes`.
<!-- /router -->

<!-- router:modular -->
Un controlador responde a una URL y devuelve una vista. Dale a las notas su propia carpeta, con vista:

```nexy filename="src/apps/notes/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

y el controlador que lo representa en `/notes`:

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/notes/notes_view.nexy")})
```

Un controlador responde sólo una vez que un módulo lo enumera. Agréguelo al módulo raíz:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController]
```
<!-- /router -->

Abra <http://localhost:3000/notes>: debería ver dos viñetas. La parte entre las dos líneas `---` es Python, ejecutada en el servidor; el resto es HTML con etiquetas Jinja2 como `{% for %}` y `{{ note }}`.

## cambiar el diseño

<!-- router:fbr,custom -->
`src/routes/layout.nexy` es propietario del documento HTML: `<html>`, `<head>` y `<body>`. Nexy envuelve cada página, donde escribe `{{children | safe}}`.
<!-- /router -->
<!-- router:modular -->
`src/apps/layout.nexy` es propietario del documento HTML: `<html>`, `<head>` y `<body>`. El controlador envuelve su vista en él pasando la vista como `children`.
<!-- /router -->

Abra el diseño y cambie la línea `<title>Nexy App</title>` a:

```html
<title>Notes</title>
```

Guardar: la pestaña del navegador ahora dice *Notas*, en cada página.

## Dale espacio a las páginas debajo del encabezado.

El encabezado del diseño es fijo: permanece en la parte superior de la ventana, encima de la página. Las páginas del inicio establecen su propio espacio debajo; las páginas de la aplicación de notas comparten una clase para eso, `app-page`, que cada página del tutorial incluye su contenido. Agréguelo al final de `src/globale.css`, la hoja de estilo ya se carga en cada página:

```css
/* The pages of the notes app: one readable column below the fixed header. */
.app-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 42rem;
  margin: 0 auto;
  padding: 8rem 1.5rem 5rem;
}

.app-page h1 {
  font-size: 2rem;
}

.app-page form {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 0.5rem;
}

.app-page label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.app-page input:not([type="hidden"]) {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-second);
  border-radius: 0.375rem;
  background: var(--background);
}

.app-page button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  background: var(--foreground);
  color: var(--background);
  cursor: pointer;
}

.app-page a {
  text-decoration: underline;
}
```

Tailwind, que utiliza el iniciador, elimina los bordes de los campos del formulario: estas reglas los devuelven, para que se puedan ver los formularios de las siguientes partes.

## lo que aprendiste

<!-- router:fbr,custom -->
- Un archivo `.nexy` bajo `src/routes/` es una página; su carpeta y nombre son su URL.
- La raíz `layout.nexy` envuelve cada página del documento HTML.
<!-- /router -->
<!-- router:modular -->
- Un controlador responde a una URL y muestra una vista `.nexy` con `useViews`; un módulo lo enumera.
- El diseño también es una vista: el controlador le pasa la vista de página como `children`.
<!-- /router -->
- Un archivo `.nexy` está Python entre `---`, luego HTML con Jinja2.
- `src/globale.css` contiene los estilos que comparte cada página, como `app-page`.

## Próximos pasos

- [Parte 3: rutas dinámicas y una API](dynamic-routes.md)
- [Archivos .nexy](../views/nexy/README.md): accesorios, componentes y estilos
