# Controladores de ruta

Un archivo `.py` en `src/routes/` es un controlador de API. La ruta del archivo es la URL y cada función que lleva el nombre de un método HTTP se convierte en un punto final.

## Crear un punto final

```python filename="src/rutas/api/items.py"
from nexy.http import Request
from pydantic import BaseModel


class Item(BaseModel):
    name: str


async def GET(request: Request):
    return {"items": []}


async def POST(request: Request, body: Item):
    return {"created": body.name}
```

Este archivo responde a `GET /api/items` y `POST /api/items`.

Nombres de funciones admitidas: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS`, `HEAD`. `SOCKET` abre un WebSocket en la misma ruta; consulte [WebSocket](../realtime/websocket.md).

## El vocabulario HTTP

Importe lo que necesita un controlador de `nexy.http`:

```python
from nexy.http import Depends, Header, HTTPException, JSONResponse, Request, status
```

Expone las clases de solicitud y respuesta (`Request`, `Response`, `JSONResponse`, `HTMLResponse`, `PlainTextResponse`, `RedirectResponse`, `StreamingResponse`, `FileResponse`), las fuentes de parámetros (`Header`, `Query`, `Cookie`, `Path`, `Body`), `Depends`, `BackgroundTasks`, `HTTPException` y `status`. Los controladores escritos en este módulo dependen del contrato de Nexy, no del motor que les sirve. Pydantic los modelos describen cuerpos y respuestas como de costumbre.

## Parámetros

| Fuente | Cómo llega |
|---|---|
| Segmento de ruta `[id]` | argumento de función `id`, convertido a su anotación |
| Cadena de consulta | `page: int = 1` |
| Cuerpo JSON | Pydantic argumento del modelo |
| FastAPI primitivas | `Depends`, `Header`, `Cookie`, `Form`, `UploadFile` - sin cambios |

```python filename="src/rutas/api/usuarios/[id].py"
async def GET(id: int):
    return {"id": id}
```

El segmento de ruta es `{id}`, por lo que FastAPI valida `id: int`. Un valor que no es un número entero responde `404`, porque una ruta dinámica captura cualquier URL y una URL que no se puede convertir no existe. Ver [Validación y errores](validation-and-errors.md).

## Respuestas

| Devolver | Respuesta |
|---|---|
| `dict`, `list`, `BaseModel` | JSON |
| `JSONResponse`, `HTMLResponse`, cualquier `Response` | exactamente como se declara |
| `None` | respuesta vacía: devuelve un `Response` en su lugar cuando el estado importa |

Para un código de estado personalizado o tipo de contenido, devuelva un objeto de respuesta:

```python filename="src/rutas/api/items.py"
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"created": True}, status_code=201)
```

## Errores

Plantear FastAPI excepciones para clientes. Un cliente que envía `Accept: application/json` recibe `{"detail": "..."}` con el estado que usted planteó; un navegador recibe la página de error. `notfound.nexy` representa `404` y `errors.nexy` representa `500`, cada uno con el ámbito de su directorio. Consulte [Validación y errores](validation-and-errors.md) y [Páginas de error](../errors/README.md).

## OpenAPI

Cada ruta API aparece en el esquema generado, porque las rutas son rutas FastAPI simples. El esquema se entrega en `/openapi.json` y Scalar lo representa en `/docs`. Deshabilite ambos con `useDocs = False` en `nexyconfig.py`.

## Próximos pasos

- [Dependencias](../dependencies/README.md): autenticación compartida y configuración por controlador o por directorio
- [Validación y errores](validation-and-errors.md): `422`, `404` y errores JSON
- [Enrutamiento](../../README.md): ruta del archivo a la URL
- [Acciones](../../../guides/actions.md): puntos finales con rutas generadas
- [Configuración](../../../reference/config.md): middleware, CORS, sesiones
