# Instalación

## Requisitos

| Requisito | Por qué |
|---|---|
| Python 3.12+ | `requires-python` en `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | crea el proyecto, instala sus paquetes y ejecuta Nexy |
| Node.js 18+ | solo para un marco de cliente (React, Vue, Svelte, Solid, Preact) |

Un proyecto sin un marco de cliente no necesita ningún Node.js.

## Instale uv primero

`uvx` no es una herramienta independiente: viene con uv, así que instálalo antes que nada.

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Compruébalo con `uv --version` y `uvx --version`.

## Crear un proyecto

```bash
uvx nexy new my-app
```

`uvx` ejecuta Nexy en un entorno temporal y no deja nada atrás. Eso es suficiente para **crear** un
proyecto (`new`, `init`) y nada más: el entorno temporal contiene Nexy y ningún otro
paquete. `nexy new` crea el propio entorno virtual del proyecto, `.venv`, e instala sus paquetes
allí.

`nexy new my-app` plantea cuatro preguntas: enrutador (basado en archivos o modular), tipo de proyecto (web o API),
marco de cliente, ORM. La instalación de las dependencias de Python y Node se ejecuta con una línea por
paso y su duración. Consulte [CLI](../reference/cli.md).

Omita las indicaciones con una plantilla registrada:

```bash
uvx nexy new my-app --template <name>
```

## Trabajar dentro del entorno virtual del proyecto.

Cualquier otro comando (`nexy dev`, `nexy build`, `nexy migrate`...) debe ejecutarse **dentro del proyecto
entorno virtual**. Ahí es donde viven tus propios paquetes: tu ORM, tus bibliotecas y Nexy.
con el que se construyó el proyecto. Fuera de él, un proyecto que necesita `sqlmodel` fracasa con
`ModuleNotFoundError: No module named 'sqlmodel'`.

Actívalo una vez por terminal, desde la carpeta del proyecto:

| Shell | Comando |
|---|---|
| PowerShell, cmd (Windows) | `.venv\Scripts\activate` |
| macOS, Linux | `source .venv/bin/activate` |

El mensaje comienza con `(.venv)`. Desde allí:

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Abra <http://localhost:3000>.

Para omitir la activación, deje que uv lo haga con un comando: `uv run nexy dev`.

> [!NOTA]
> `nexy` y `nx` son el mismo binario. Una copia instalada con `uv tool install
> nexy` lives in its own environment, like `uvx`, así que úsalo para crear proyectos y ejecutar todo
> el resto del entorno del proyecto.

## Agregar Nexy a un proyecto existente

Ejecútelo desde el entorno virtual del proyecto, con Nexy entre sus paquetes (`uv add nexy`):

```bash
nexy init
```

## Próximos pasos

- [Inicio rápido](quick-start.md)
- [Tutorial](tutorial.md)
- [Estructura del proyecto](project-structure.md)
- [Solución de problemas](../guides/troubleshooting.md)