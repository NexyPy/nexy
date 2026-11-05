# herencia

Varios archivos en `src/routes/` se aplican a todo lo que se encuentra debajo de su directorio. Todos se resuelven de la misma manera: Nexy comienza en el directorio de la ruta y camina hasta `src/routes/`.

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| Archivo | regla |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | cada diseño desde la raíz hasta la página lo envuelve, **el más externo primero** |
| `middleware.py` | cada archivo desde la raíz hasta la ruta envuelve la solicitud, **más externa primero**, antes de las dependencias |
| `dependencies.py` | se ejecuta cada archivo desde la raíz hasta la ruta, **el más externo primero**, luego los propios guardias del controlador |
| `notfound.nexy`, `errors.nexy` | el **más cercano** gana, según el código de estado |

Para la página anterior, los diseños se anidan como `root layout > (shop) layout > cart layout > page` y las dependencias se ejecutan como `root > (shop) > cart > handler guards`.

## ¿Por qué lo más externo primero?

Un diseño exterior dibuja el marco y una dependencia exterior decide quién puede entrar. Ponerlos en primer lugar significa que los internos pueden confiar en ellos: un directorio que requiere autenticación se ejecuta antes que un controlador que lee al usuario.

La dependencia `(shop)` del árbol verifica la cookie del carrito, por lo que la dependencia del carrito debajo puede leer el carrito sin volver a verificar:

```python filename="src/rutas/(tienda)/dependencias.py"
from nexy.http import HTTPException, Request


def require_cart(request: Request) -> None:
    if "cart" not in request.cookies:
        raise HTTPException(status_code=400, detail="No cart")


dependencies = [require_cart]
```

## Diseños

Todos los archivos de diseño de una pila de familia de carpetas: consulte [Diseños](layouts/README.md). Las diferentes familias no se mezclan: una `layout.vue` nunca envuelve una página `.tsx`, y un proyecto tiene `layout.nexy` o diseños de cliente, nunca ambos ([modos](modes.md)).

El diseño más interno del árbol solo agrega su propio marco: el diseño raíz a su alrededor todavía dibuja el documento.

```nexy filename="src/routes/(tienda)/cart/layout.nexy"
---
children: prop[NexyElement]
---
<section class="cart">
  <h2>Your cart</h2>
  {{ children | safe }}
</section>
```

## Archivos de software intermedio

Ver [Archivos middleware](middleware/README.md): se ejecutan antes de las dependencias y pueden responder sin llegar a la ruta.

Una raíz `middleware.py` envuelve cada ruta del árbol, incluido el carro:

```python filename="src/rutas/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## Dependencias

Consulte [Dependencias](dependencies/README.md) para conocer el orden en un archivo de controlador, incluidos `@UseGuard` y `@Middleware`.

## Páginas de error

`notfound.nexy` y `errors.nexy` se instalan una vez en la raíz de las rutas; una copia en un subdirectorio refina la página para ese prefijo. Consulte [Páginas de error](errors/README.md).

Una copia en `cart/` responde a los 404 en `/cart`, y la raíz se queda con el resto:

```nexy filename="src/routes/(tienda)/cart/notfound.nexy"
---
title: Product not found
---
<h1>This product is gone</h1>
<p><a href="/cart">Back to your cart</a></p>
```

## Próximos pasos

- [Diseños](layouts/README.md)
- [Dependencias](dependencies/README.md)
- [Páginas de error](errors/README.md)
