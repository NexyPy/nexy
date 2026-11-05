# Solución de problemas

Los problemas a los que la gente se enfrenta primero, con lo que ves y qué hacer. Cada uno proviene de una carrera real.

## Una página responde 404 pero su archivo existe

Mire la terminal que ejecuta `nx dev` o `nx start`. Cuando no se puede importar una página, Nexy informa el error con su archivo y línea, y la ruta no se registra:

```text
nexy » error __nexy__/src/routes/index.py:18  ImportError: cannot import name 'FrameworkLogo' ...
```

Corrija la importación nombrada allí. Las causas habituales son un componente cuyo nombre de función no coincide con lo que importa (consulte el siguiente elemento) y un error tipográfico en la ruta.

## Una página `.nexy` no se compila: "Error de análisis lógico"

```text
src/components/live-panel.nexy - Logic Parse Error: invalid syntax
```

Un componente `.nexy` se importa como un módulo Python, por lo que su nombre de archivo debe ser un nombre válido. Un guión no lo es. Nómbrelo en PascalCase, `LivePanel.nexy` e impórtelo con el mismo nombre:

```nexy
from "@/components/LivePanel.nexy" import LivePanel
```

## Un componente representa a sus hijos como el texto `<slot />`

Un componente `.nexy` coloca a sus hijos con `<Slot />`, con una S mayúscula. Una `<slot />` minúscula se deja en la página tal como está. Vue, que tiene su propio `<slot />`, no se ve afectado.

## Un accesorio muestra el nombre de la variable.

```nexy
<Icon path=icon />          renders: icon
<Icon path="{{ icon }}" />  renders: the value of icon
```

Un atributo sin llaves es texto. Coloque la expresión Jinja en el atributo para pasar un valor calculado.

## Un valor en `{{ ... }}` se vuelve vacío

Jinja2 oculta una variable indefinida. Declare todas las propiedades que utilice al principio (`title: prop[str] = ""`) y revise la ortografía.

## Las clases de utilidad no tienen efecto en una página `.nexy` (UnoCSS)

UnoCSS lee un archivo solo cuando su extensión está en su canal de contenido. Un proyecto de servidor creado por `nx new` con UnoCSS ya incluye `.nexy`; uno mayor lo necesita en `uno.config.ts`:

```ts
content: {
  filesystem: ['src/**/*.nexy'],
  pipeline: { include: [/\.(vue|svelte|[jt]sx|mdx?|astro|html|nexy)($|\?)/] },
},
```

Tailwind encuentra `.nexy` archivos por sí solo.

## Una página `.mdx` solicita paquetes

```text
[nexy] MDX support requires optional packages that are not installed.
```

Instálelos en el proyecto: `@mdx-js/rollup`, `remark-gfm` y `@mdx-js/react` (más `@mdx-js/esbuild` para `nx build`). MDX necesita React o Preact en `useFF`. Sin un marco de cliente, escriba la página como `.md`. Ver [Markdown y MDX](../views/nexy/markdown.md).

## `No module named 'sqlmodel'` (o cualquier paquete) cuando se inicia un comando

```text
nexy » nexyconfig.py cannot be loaded: No module named 'sqlmodel'. If it is a package, install it
in this Python (...) or activate the project's virtual environment.
```

El comando se ejecutó en el Python incorrecto. Los paquetes de tu proyecto (tu ORM, tus librerías) están en su `.venv`, y `uvx nexy` o un `nexy` global se ejecuta en un entorno propio que no tiene ninguno de ellos.

Active el entorno virtual del proyecto, desde la carpeta del proyecto, luego ejecute el comando nuevamente:

```bash
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

El mensaje comienza con `(.venv)` cuando está activo. O omita la activación con `uv run nexy dev`. Si el paquete realmente falta en el proyecto, agréguelo con `uv add sqlmodel`.

## `nx dev` muestra un error y espera

Cuando su aplicación no puede iniciarse, `nx dev` informa el motivo y espera el siguiente cambio de archivo; no sale. Arregle el archivo y guárdelo. Sólo Ctrl+C lo detiene.

## El puerto esta ocupado

`nx dev` toma el siguiente puerto libre y lo imprime. Para elegir uno, use `--port` o configure `usePort` en `nexyconfig.py`.

## El tema parpadea en blanco en una página oscura.

El tema guardado debe aplicarse antes de la primera pintura. Mantenga el pequeño script del iniciador en el `<head>` del diseño raíz y coloque `suppressHydrationWarning` en `<html>` en React.

## Todavía estancado

- Lea la página de la característica en [el índice de documentación](../README.md).
- Si los documentos y el código no están de acuerdo, el código es correcto: abra un [problema](https://github.com/NexyPy/nexy/issues) nombrando la página.
