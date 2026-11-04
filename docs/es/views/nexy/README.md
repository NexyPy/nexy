# .archivos nexy

Un archivo `.nexy` es un componente: Python en la parte superior, HTML en el medio, CSS en la parte inferior.

**Antes de comenzar:** un proyecto creado por el [Inicio rápido](../../getting-started/quick-start.md).
Un archivo `.nexy` no necesita configuración de compilación: `nx dev` lo compila al guardarlo.

```nexy filename="src/rutas/blog/[slug].nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```

## Primera cuestión

Todo lo que hay entre las dos líneas `---` es Python. Las importaciones se resuelven cuando el componente es
compilado; el resto se ejecuta para cada solicitud, por lo que puede leer el estado de la solicitud.

| Qué | Ejemplo |
|---|---|
| Importar un módulo | `import json`, `from datetime import datetime` |
| Importar un componente | `from "@/components/card.nexy" import Card` |
| Declarar una propiedad | `title: prop[str] = "Default"` |
| Calcular un valor | `year = datetime.now().year` |
| Leer la solicitud | `pathname = usePathname()` |
| Caché de la página (ISR) | `revalidate = 60` |

## Propiedades

Las propiedades son la API del componente. `prop[type]` declara el tipo, `= value` proporciona un valor predeterminado. un
La propiedad sin valor predeterminado debe ser pasada por el padre.

Las importaciones que comienzan con un alias se resuelven mediante `useAliases`. La configuración `nx new` escribe mapas
`@` a `src`, lo que hace que `@/components/card.nexy` signifique `src/components/card.nexy`.

## Plantilla

Debajo del frontmatter está HTML con Jinja2. Las variables del frontmatter y las propiedades están en
alcance.

```html
{% for item in items %}
  <li>{{ item.name }}</li>
{% endfor %}

{% if user %}
  <p>Welcome, {{ user.name }}</p>
{% endif %}
```

El escape automático está **desactivado**: las plantillas son el propio HTML del proyecto, por lo que `{{ value }}` se inserta como
escrito. Escape usted mismo de los valores que no son de confianza con `{{ value | e }}`. `| safe` por lo tanto no cambia nada.

> [!NOTA]
> envuelve JavaScript que contiene `{{` o `{%` en `{% raw %}...{% endraw %}`.
> Frameworks como Vue y Svelte usan las mismas llaves.

## Componentes

Cualquier invocable importado cuyo nombre comience con una letra mayúscula se puede utilizar como etiqueta. el compilador
lo reescribe en una llamada de Jinja: los atributos se convierten en argumentos de palabras clave.

```nexy filename="src/rutas/index.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```

La última línea es exactamente `{{ Audio("/theme.mp3", controls=True) }}`. Ambas sintaxis son válidas para el
ayudantes integrados `Image`, `Link`, `Audio` y `Video` - consulte
[componentes](components.md#two-syntaxes-one-function).

Los niños se representan a través de `<Slot />` (S mayúscula) dentro del componente secundario y a través de `{{ children }}`
dentro de un diseño.

Pase un valor calculado con Jinja dentro del atributo: `<Icon path="{{ icon }}" size="{{ size }}" />`.
Un nombre simple como `path=icon` es el texto `icon`, no la variable. Para darle a un componente un CSS
clase, declare una propiedad `class_name`: `class` es una palabra clave de Python.

> [!NOTA]
> una etiqueta auxiliar siempre se cierra automáticamente. Pasar contenido a `Link` pasa por su
> `children` argumento (`<Link href="/about" children="About" />`), no a través del contenido del elemento.

## Estilos

`<style>` los bloques se emiten con la página que los declara. No tienen alcance: un nombre de clase
utilizado en dos componentes es una clase. Prefija o crea un espacio de nombres para tus clases.

## Reglas que ahorran tiempo

- Un componente por archivo. El nombre del archivo es el nombre del componente, en PascalCase (`CopyChip.nexy`). un
  El componente `.nexy` se importa como un módulo de Python: un guión en el nombre (`copy-chip.nexy`) no
  compilar.
- Declare accesorios antes de usarlos: una variable no declarada se representa como una cadena vacía, porque
  El indefinido de Jinja2 guarda silencio aquí.
- Mantenga los efectos secundarios dentro de las funciones: el frontmatter se ejecuta nuevamente en cada solicitud.

## Próximos pasos

- [Markdown y MDX](markdown.md): páginas de contenido
- [ISR](../../rendering/isr.md): almacena en caché una página por ruta
- [CSR](../../rendering/csr.md): renderizado del lado del cliente