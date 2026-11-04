# Validación y errores

Cómo un controlador de API informa una solicitud incorrecta.

## Validación

FastAPI valida los parámetros del controlador con sus anotaciones.

```python filename="src/rutas/api/search.py"
from nexy.http import Header


async def GET(q: str, limit: int = 10, x_token: str = Header(...)):
    return {"q": q, "limit": limit}
```

| Problema | Estado | Cuerpo |
|---|---|---|
| consulta, encabezado, cookie o campo de cuerpo faltantes o no válidos | `422` | `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}` |
| segmento **ruta** no válido (`/api/users/abc` para `id: int`) | `404` | la página no encontrada, o JSON para `Accept: application/json` |

Un segmento de ruta que no se puede convertir es un `404` en lugar de un `422`: una ruta dinámica captura cualquier
URL y no existe una URL que no se pueda convertir.

El cuerpo `422` es la forma estándar de FastAPI, por lo que los clientes existentes y los SDK generados siguen funcionando.

##  Generando errores

```python filename="src/rutas/api/items/[id].py"
from nexy.http import HTTPException


async def GET(id: int):
    item = find(id)
    if item is None:
        raise HTTPException(status_code=404, detail="No such item")
    return item
```

| Cliente envía | Respuesta |
|---|---|
| `Accept: application/json` | `{"detail": "No such item"}` con estado `404` |
| `Accept: text/html` | la [página de error](../errors/README.md) |
| `Accept: */*` | la página de error |

Establezca `Accept: application/json` en clientes API. Los navegadores siguen recibiendo páginas.

## Excepciones no controladas

Una excepción es que su controlador no detecta las respuestas `500`, con la misma opción HTML o JSON.

## Respuestas personalizadas

Devuelve un objeto de respuesta cuando controlas el cuerpo:

```python
from nexy.http import JSONResponse


async def POST():
    return JSONResponse({"error": "conflict"}, status_code=409)
```

## Próximos pasos

- [Rutas API](README.md)
- [Páginas de error](../errors/README.md)
- [Pruebas](../../../guides/testing.md)