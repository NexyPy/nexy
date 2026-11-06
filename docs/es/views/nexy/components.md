# Componentes

Nexy exporta un pequeño conjunto de ayudas que devuelven cadenas HTML. Cada uno se usa de dos maneras en una plantilla `.nexy`: como una llamada Jinja o como una etiqueta de estilo HTML.

## Dos sintaxis, una función

<!-- router:fbr,custom -->
```nexy filename="src/rutas/index.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```
<!-- /router -->

Ambas líneas producen el mismo marcado:

```html
<audio preload="metadata" controls><source src="/theme.mp3" type="audio/mp3" /></audio>
```

El compilador reescribe `<Audio ... />` a `{{ Audio(...) }}`, por lo que el formulario de etiqueta no es una segunda API: los atributos son los argumentos de palabras clave de la función.

## Reglas del formulario de etiqueta.

| en la etiqueta | se convierte |
|---|---|
| `<Audio src="/a.mp3" />` | `Audio(src="/a.mp3")` |
| `controls=True` | `controls=True`, un verdadero booleano |
| `width=640` | `width=640`, un número |
| `src="{{ url }}"` | `src=(url)`, evaluado en Jinja |
| cualquier otro `value` | `"value"`, una cadena |

- La etiqueta debe comenzar con una letra mayúscula y importarse en el frontmatter; de lo contrario, el compilador genera `Missing Import: <Name> used but not declared.`
- El formato de la etiqueta es **de cierre automático**. `<Audio src="/a.mp3" />` y `{{ Audio("/a.mp3") }}` son ​​equivalentes; No se admite escribir niños dentro de una etiqueta auxiliar.
- Un atributo HTML simple no es booleano aquí: `controls` se convierte en `controls=""`, lo cual es falso. Escribe `controls=True`.

> [!NOTE]
> `class_name` es la palabra clave documentada para las clases CSS. Los argumentos de palabras clave adicionales se convierten en atributos HTML, por lo que `class="nav"` también llega al resultado.

## Imagen

```nexy
---
from nexy import Image
---
{{ Image("/logo.png", alt="Logo", width=128, height=32) }}

<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

`Image(src, alt="", width=None, height=None, loading="lazy", class_name=None, **attrs)` representa un `<img>` con carga diferida de forma predeterminada.

## Enlace

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` representa un `<a data-nexy-link>` manejado por el enrutador del cliente. Con `prefetch=True`, pasar el cursor o tocar el enlace calienta el objetivo a través de `window.__nexy_prefetch`.

> [!NOTE]
> el formulario de etiqueta toma la etiqueta como `children`, no como contenido del elemento: `<Link href="/about" children="About" />`. Para colocar marcas dentro de un enlace, use el formulario de llamada con `children=` o un componente `.nexy` que represente un `<Slot />`.

## Audio y Vídeo

```nexy
---
from nexy import Audio, Video
---
{{ Audio("/theme.mp3", controls=True) }}
{{ Video("/demo.mp4", width=640, height=360, muted=True, sources=["/demo.webm", "/demo.mp4"]) }}

<Audio src="/theme.mp3" controls=True />
<Video src="/demo.mp4" width=640 height=360 muted=True />
```

`Audio(src, controls=True, autoplay=False, loop=False, muted=False, preload="metadata", class_name=None, sources=None, **attrs)` y `Video(src, width=None, height=None, ...)` renderizan reproductores nativos. `sources` agrega etiquetas `<source>` con el tipo MIME derivado de cada extensión.

## Un componente que escribes tú mismo.

Un componente `.nexy` reutilizable es un archivo debajo de `src/components/`: Python accesorios en la parte superior, HTML debajo. Se importa como cualquier otro módulo Python.

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

<!-- router:fbr,custom -->
```nexy filename="src/rutas/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest notes" tone="warm">
  <p>Everything published this week.</p>
</Card>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest notes" tone="warm">
  <p>Everything published this week.</p>
</Card>
```
<!-- /router -->

`title` no tiene ningún valor predeterminado, por lo que la página debe pasarlo; `tone` vuelve a `"neutral"`. El marcado entre las etiquetas llega dentro de `<Slot />` (S mayúscula). Consulte los [archivos .nexy](README.md#components) para conocer los accesorios, los espacios y las reglas del formulario de etiqueta.

## Importar un componente de cliente

Desde un archivo `.nexy`, importe un componente del marco por ruta; el compilador lo monta en el cliente y pasa los atributos como accesorios:

```nexy
---
from "@/components/Counter.tsx" import Counter
---
<Counter start="0" />
```

`Import(path, framework, symbol)` hace lo mismo en Python:

```python
from nexy import Import

counter = Import("@/components/Counter.tsx", "react", "Counter")
html = counter(start=0)
```

La misma sintaxis de importación resuelve `.json`, `.css` y archivos de imagen en sus URL.

## Plantilla y Vite

`Template().render(path, context)` renderiza un archivo de plantilla (Jinja2, o Markdown renderiza en HTML para `.md` rutas). `Template().invalidate(path)` lo elimina del caché.

`Vite()` devuelve las etiquetas del cliente para el modo actual: el script HMR en desarrollo, el paquete de cliente creado en producción. Nexy lo llama para cada página; rara vez lo necesitas directamente.

## Aún no implementado

`Form` y `Script` son marcadores de posición exportados sin comportamiento. No confíes en ellos.

## Próximos pasos

- [Archivos .nexy](README.md): donde se utilizan estos ayudantes
- [React](../react/differences.md): importando `.tsx` componentes
- [Frontend](../../guides/frontend.md): cómo se agrupan los componentes del cliente
