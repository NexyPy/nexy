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

| Archivo | Regla |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | cada diseño desde la raíz hasta la página lo envuelve, **el más externo primero** |
| `middleware.py` | cada archivo desde la raíz hasta la ruta envuelve la solicitud, **el más externo primero**, antes de las dependencias |
| `dependencies.py` | cada archivo desde la raíz hasta la ruta se ejecuta, **el más externo primero**, luego los propios guardias del controlador |
| `notfound.nexy`, `errors.nexy` | el **más cercano** gana, según el código de estado |

Para la página anterior, los diseños se anidan como `root layout > (shop) layout > cart layout > page` y las dependencias se ejecutan como `root > (shop) > cart > handler guards`.

## ¿Por qué lo más externo primero?

Un diseño exterior dibuja el marco y una dependencia exterior decide quién puede entrar. Ponerlos en primer lugar significa que los internos pueden confiar en ellos: un directorio que requiere autenticación se ejecuta antes que un controlador que lee al usuario.

## Diseños

Todos los archivos de diseño de una pila de familia de carpetas: consulte [Diseños](layouts/README.md). Las diferentes familias no se mezclan: un `layout.vue` nunca envuelve una página `.tsx`, y un proyecto tiene `layout.nexy` o diseños de cliente, nunca ambos ([modos](modes.md)).

## Archivos de software intermedio

Ver [Archivos middleware](middleware/README.md): se ejecutan antes de las dependencias y pueden responder sin llegar a la ruta.

## Dependencias

Consulte [Dependencias](dependencies/README.md) para conocer el orden en un archivo de controlador, incluidos `@UseGuard` y `@Middleware`.

## Páginas de error

`notfound.nexy` y `errors.nexy` se instalan una vez en la raíz de las rutas; una copia en un subdirectorio refina la página para ese prefijo. Consulte [Páginas de error](errors/README.md).

## Próximos pasos

- [Diseños](layouts/README.md)
- [Dependencias](dependencies/README.md)
- [Páginas de error](errors/README.md)
