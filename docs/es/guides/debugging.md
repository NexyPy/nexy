# ¿Cómo depuro el código del servidor en Nexy?

Depure el código del servidor de `nx dev` con `breakpoint()` en la terminal, o con VS Code y `debugpy`: el servidor de desarrollo ejecuta su Python en su propio proceso, por lo que un depurador adjunto se detiene en sus páginas, controladores de API y acciones.

## Cómo `nx dev` ejecuta su código

`nx dev` inicia uvicorn en su propio proceso, sin un trabajador separado. Cuando un archivo Python o una página `.nexy` cambia, se olvida de los módulos de tu proyecto y los vuelve a importar en ese mismo proceso. Por lo tanto, un depurador adjunto a `nx dev` permanece adjunto durante una recarga, y un punto de interrupción establecido en un archivo mantiene su lugar en el nuevo código.

Un archivo `.nexy` se compila en un módulo Python en `__nexy__/`, en la misma ruta, que es lo que se ejecuta:

<!-- router:fbr,custom -->
| tu escribes | Nexy corre |
|---|---|
| `src/routes/about.nexy` | `__nexy__/src/routes/about.py`, función `About()` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/routes/api/users.py` | el archivo en sí |
<!-- /router -->

<!-- router:modular -->
| tu escribes | Nexy corre |
|---|---|
| `src/apps/users/user_view.nexy` | `__nexy__/src/apps/users/user_view.py` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/apps/users/user_controller.py` | el archivo en sí |
<!-- /router -->

El texto frontal de un archivo `.nexy` (el Python entre las dos `---` líneas) se convierte en el cuerpo de una función de ese módulo. `__nexy__/` se escribe nuevamente en cada cambio: nunca lo edites.

## Para en la terminal con `breakpoint()`

Coloque `breakpoint()` donde desee detenerse, en un archivo `.py` o al principio de un archivo `.nexy`:

<!-- router:fbr,custom -->
```nexy filename="src/rutas/about.nexy"
---
from nexy import useSearchParams

page = useSearchParams().get("page", "1")
breakpoint()
---
<p>Page {{ page }}</p>
```

Abre la página. La solicitud espera y la terminal de `nx dev` muestra pdb, en el módulo compilado:

```text
> /path/to/app/__nexy__/src/routes/about.py(21)About()
-> breakpoint()
(Pdb)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users")
class UserController:
    async def get(self):
        page = "1"
        breakpoint()
        return {"page": page}
```

Abra `/users`. La solicitud espera y la terminal de `nx dev` muestra pdb en esa línea. En la parte frontal de una vista, pdb muestra el módulo compilado en `__nexy__/src/apps/`.
<!-- /router -->

Escriba `p page` para imprimir un valor, `n` para la siguiente línea, `c` para permitir que la solicitud continúe. Elimine la línea cuando haya terminado: la siguiente solicitud se detiene allí nuevamente.

## Depurar con código VS

Instale `debugpy` en el entorno del proyecto:

```bash
uv add --dev debugpy
```

Luego agregue una configuración de inicio. `nexy.modules.cli` es el módulo detrás del comando `nx`, por lo que funciona igual en Linux, macOS y Windows:

```json filename=".vscode/launch.json"
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "nx dev",
      "type": "debugpy",
      "request": "launch",
      "module": "nexy.modules.cli",
      "args": ["dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

Presione F5. Establezca puntos de interrupción en sus archivos `.py` y en el módulo compilado en `__nexy__/` para un archivo `.nexy`: VS Code no puede detenerse en un archivo `.nexy`, porque no es Python hasta que se compila. Los números de línea del módulo compilado siguen el principio, por lo que un punto de interrupción puede moverse después de editar la página; `breakpoint()` al principio no.

## Conectar desde otro terminal

Para iniciar el servidor de desarrollo usted mismo y adjuntar un depurador más tarde:

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m nexy.modules.cli dev
```

`--wait-for-client` mantiene el inicio hasta que se adjunta un depurador; déjalo afuera para comenzar de inmediato. En VS Code, adjunte con una configuración de `"request": "attach"` y `"connect": { "host": "127.0.0.1", "port": 5678 }`.

debugpy puede advertir que "se están utilizando módulos congelados". Comience Python con `-Xfrozen_modules=off` (`python -Xfrozen_modules=off -m debugpy ...`) si se omite un punto de interrupción en la biblioteca estándar; los puntos de interrupción en su propio código no se ven afectados.

## Próximos pasos

- [Solución de problemas](troubleshooting.md): los primeros problemas que encuentra la gente
- [Pruebas](testing.md): reproduce el error en una prueba una vez que lo hayas encontrado
- [Archivos .nexy](../views/nexy/README.md): frontmatter, accesorios y plantillas
