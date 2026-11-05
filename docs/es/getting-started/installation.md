# Instalación

## Requisitos

| Requisito | Por qué |
|---|---|
| Python 3.12+ | `requires-python` en `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | crea el proyecto, instala sus paquetes y ejecuta Nexy |
| Node.js 18+ | solo para un marco de cliente (React, Vue, Svelte, Solid, Preact) |

Un proyecto sin un marco de cliente no necesita Node.js en absoluto.

## Instale uv primero

`uvx` no es una herramienta independiente: viene con uv, así que instala uv antes que nada.

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

`uvx` ejecuta Nexy en un entorno temporal y no deja nada atrás. Eso es suficiente para **crear** un proyecto (`new`, `init`) y nada más: el entorno temporal contiene Nexy y ningún otro paquete. `nexy new` crea el propio entorno virtual del proyecto, `.venv`, e instala sus paquetes allí.

`nexy new my-app` plantea cuatro preguntas: enrutador (basado en archivos o modular), tipo de proyecto (web o API), marco de cliente, ORM. La instalación de Python y las dependencias de Node luego se ejecuta con una línea por paso y su duración. Consulte [CLI](../reference/cli.md).

Omita las indicaciones con una plantilla registrada:

```bash
uvx nexy new my-app --template <name>
```

## Trabajar dentro del entorno virtual del proyecto.

Cualquier otro comando (`nexy dev`, `nexy build`, `nexy migrate`...) debe ejecutarse **dentro del entorno virtual del proyecto**. Ahí es donde viven sus propios paquetes: su ORM, sus bibliotecas y el Nexy con el que se creó el proyecto. Fuera de él, un proyecto que necesita `sqlmodel` falla con `ModuleNotFoundError: No module named 'sqlmodel'`.

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
> `nexy` y `nx` son el mismo binario. Una copia instalada con `uv tool install nexy` vive en su propio entorno, como `uvx`, así que úsela para crear proyectos y ejecutar todo lo demás desde el entorno del proyecto.

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
