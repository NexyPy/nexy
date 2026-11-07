# Cree una aplicación de notas con Nexy, parte 4: componentes

La parte 4 convierte cada nota en un componente reutilizable, un archivo `.nexy` que se importa como un nombre Python y se usa como una etiqueta HTML.

**Antes de comenzar:** la aplicación de la [parte 3](dynamic-routes.md).

## Escribe el componente

Un componente es un archivo `.nexy` fuera de las rutas. Sus accesorios se declaran con `prop[...]` y la persona que llama los pasa como atributos:

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

El bloque `<style>` se envía con cada página que utiliza la tarjeta. No tiene alcance: `.note` es una clase para toda la página, así que proporcione a las clases de un componente los nombres que solo ella usa.

## Úselo en la lista

<!-- router:fbr,custom -->
```nexy filename="src/rutas/notas/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`@/` es el alias de importación de la parte 1: apunta a `src/`. El nombre del archivo es el nombre del componente, en PascalCase: `NoteCard.nexy` exporta `NoteCard`.

Abrir <http://localhost:3000/notes>: cada nota es ahora una tarjeta.

## lo que aprendiste

- Un archivo `.nexy` fuera de las rutas es un componente; sus `prop[...]` son ​​sus atributos.
- `from "@/components/x.nexy" import X` lo importa; `<X />` lo renderiza.
- Un bloque `<style>` no tiene alcance: nombre las clases de un componente después de él.

## Próximos pasos

- [Parte 5: almacenar las notas en SQLite](store-the-notes.md)
- [Componentes](../views/nexy/components.md): `Image`, `Link` y los ayudantes integrados
