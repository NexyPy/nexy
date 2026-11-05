# Tutorial: crea una página de notas en 10 minutos

Creará un proyecto, agregará una página, agregará un punto final Python, compartirá datos entre ellos y compilará para producción. Termina con una lista de notas presentadas como página y como JSON.

¿Nuevo en Nexy? Realice primero el [Inicio rápido](quick-start.md): tarda tres minutos.

```diagram filename="Todo el tutorial en una sola línea."
uvx nexy new notes ──► edit layout ──► add page ──► add endpoint ──► share data ──► nx build ──► nx start
```

## 1. Crea el proyecto

```bash
uvx nexy new notes
cd notes
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

`uvx` viene con [uv](https://docs.astral.sh/uv/) y solo crea el proyecto. Cada comando posterior se ejecuta dentro del entorno virtual del proyecto (o como `uv run nexy dev`).

Elija el enrutador basado en archivos, un proyecto web y cualquier marco de cliente (o ninguno). Abierto
<http://localhost:3000>. Los pasos largos imprimen una línea cada uno con su duración, como lo hace `uv`.

<!-- router:modular -->
Responda `No` al mensaje del enrutador basado en archivos: `nx new` estructura el enrutador modular en `src/apps/` en lugar de `src/routes/`.
<!-- /router -->

<!-- router:custom -->
Responda `Yes` al mensaje del enrutador basado en archivos para las páginas, luego monte su `APIRouter` existente en `nexyconfig.py`: los dos enrutadores coexisten.
<!-- /router -->

## 2. Edite el diseño

<!-- router:fbr,custom -->
`src/routes/layout.nexy` posee el documento HTML (con el enrutamiento del cliente React es `layout.tsx`). Cambie el `<title>`:

```nexy
<title>Notes</title>
```

Guardar: el navegador se recarga. Consulte [Diseños](../routing/fbr/layouts/README.md).
<!-- /router -->

<!-- router:modular -->
El controlador representa `src/apps/layout.nexy` alrededor de la vista y ese archivo es propietario del documento HTML. Cambie el `<title>`:

```nexy
<title>Notes</title>
```

Guardar: el navegador se recarga. Consulte [Vistas desde un controlador](../routing/modular/README.md#views-from-a-controller).
<!-- /router -->

## 3. Agrega una página

<!-- router:fbr,custom -->
```nexy filename="src/rutas/notas.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Abra <http://localhost:3000/notes>: debería ver dos viñetas. Se sirve en `/notes`. La parte entre `---` es Python, el resto es Jinja2.
<!-- /router -->

<!-- router:modular -->
Un controlador devuelve una vista. Crear `src/apps/notes_view.nexy`:

```nexy filename="src/apps/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Declare la ruta en `src/apps/app_controller.py` y agregue el controlador al módulo:

```python filename="src/apps/app_controller.py"
@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/notes_view.nexy"),
        })
```

```python filename="src/apps/app_module.py"
from .app_controller import AppController, NotesController

controllers = [AppController, NotesController]
```

Abra <http://localhost:3000/notes>: debería ver dos viñetas. La parte entre `---` es Python, el resto es Jinja2.
<!-- /router -->

## 4. Agregue un punto final

<!-- router:fbr,custom -->
```python filename="src/rutas/api/notes.py"
async def GET():
    return [{"id": 1, "text": "Buy milk"}]
```

```bash
curl http://localhost:3000/api/notes
```

Deberías obtener `[{"id":1,"text":"Buy milk"}]`. El nombre de la función es el método HTTP. Los documentos de la API interactiva se encuentran en `/docs`.
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/app_controller.py"
@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": 1, "text": "Buy milk"}]
```

Agregue `NotesApiController` a `controllers` en `src/apps/app_module.py`, luego ejecute:

```bash
curl http://localhost:3000/api/notes
```

Deberías obtener `[{"id":1,"text":"Buy milk"}]`. El nombre del método es el método HTTP. Los documentos de la API interactiva se encuentran en `/docs`.
<!-- /router -->

## 5. Comparte los datos

Mueva la lista a un módulo Python y úsela en ambos archivos:

```python filename="src/notas.py"
NOTES = ["Buy milk", "Ship Nexy"]
```

<!-- router:fbr,custom -->
```nexy filename="src/rutas/notas.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/rutas/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes_view.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/apps/app_controller.py"
from src.notes import NOTES


@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

## 6. Construir y servir

```bash
nx build
nx start
```

`nx build` imprime cada fase con su duración. `nx start` sirve la salida compilada con Uvicorn: ningún proceso de Nodo en tiempo de ejecución.

## donde sigue

- [Enrutamiento](../routing/README.md): segmentos y grupos dinámicos
- [Acciones](../guides/actions.md): llamar a Python desde un formulario o desde el cliente
- [Pruebas](../guides/testing.md): páginas de prueba y puntos finales
- [Implementar](../deployment/README.md): contenedores y proxies inversos
