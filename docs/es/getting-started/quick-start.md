# Inicio rápido

Creará un proyecto Nexy, lo ejecutará y verá un cambio de página a medida que lo edite. Tarda tres minutos. El [Tutorial](tutorial.md) luego agrega un punto final y una compilación de producción.

## Antes de empezar

| Necesitas | Por qué |
|---|---|
| Python 3.12+ | `requires-python` en `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | proporciona `uvx`, crea el proyecto e instala sus paquetes |
| Node.js 18+ | solo si usas un framework cliente (React, Vue, Svelte, Solid, Preact) |

¿No hay uv todavía? Consulte [Instalación](installation.md).

## 1. Crea el proyecto

```bash
uvx nexy new my-app
```

`uvx` viene con uv, así que instala uv primero. Ejecuta Nexy en un entorno temporal, suficiente para **crear** el proyecto. `nexy new` luego crea el propio `.venv` del proyecto e instala sus paquetes allí. Cuatro indicaciones deciden el cableado:

| Mensaje | Efecto |
|---|---|
| ¿Enrutador basado en archivos? | `Yes` escanea `src/routes/`; `No` armamenta el enrutador modular en `src/apps/` |
| El tipo de proyecto | `Web` agrega un diseño y recursos del cliente, `API` comienza sin vistas |
| ¿Componente del cliente? | agrega un marco y su Vite configuración |
| ORM/base de datos | agrega una capa de modelo, o nada |

¿No estás seguro? Responda `Yes`, `Web` y ningún componente de cliente. Puedes agregar cada uno más tarde.

## 2. Ejecútelo

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Abra <http://localhost:3000>. Deberías ver la página de inicio. El puerto proviene de `usePort` (predeterminado `3000`); `--port` y `--host` lo anulan por ejecución.

> [!NOTE]
> Ejecute todos los comandos excepto `new` y `init` dentro del entorno virtual del proyecto, o prefije `uv run`, como en `uv run nexy dev`. Fuera de él, un proyecto que necesita `sqlmodel` falla con `No module named 'sqlmodel'`.

## 3. Cambiar una página

<!-- router:fbr,custom -->
Un archivo bajo `src/routes/` es una ruta. Crear `src/routes/hello.nexy`:

```nexy filename="src/rutas/hola.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```
<!-- /router -->

<!-- router:modular -->
Un controlador devuelve una vista. Crear `src/apps/hello_view.nexy`:

```nexy filename="src/apps/hola_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

Luego declara la página en `src/apps/app_controller.py` y agrégala al módulo:

```python filename="src/apps/app_controller.py"
@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/hello_view.nexy")})
```

```python filename="src/apps/app_module.py"
from .app_controller import AboutController, AppController, HelloController

controllers = [AppController, AboutController, HelloController]
```
<!-- /router -->

Abrir <http://localhost:3000/hello>. Cambie `"Hello"` a `"Bonjour"` y guarde: la página se actualiza sin recarga manual. Si el código es incorrecto, el navegador muestra el error en lugar de una página en blanco.

`prop[str]` declara una propiedad escrita. El marcado debajo del frontmatter es Jinja2; consulte [archivos .nexy](../views/nexy/README.md).

## donde sigue

| Quieres | Leer |
|---|---|
| Agregue un punto final Python y envíe una compilación | [Tutorial](tutorial.md) |
| Sepa dónde pertenece cada archivo | [Estructura del proyecto](project-structure.md) |
| Entender quién construye qué | [Cómo funciona Nexy](how-nexy-works.md) |
| Utilice React, Vue, Svelte, Solid o Preact | [Vistas](../views/README.md) |
