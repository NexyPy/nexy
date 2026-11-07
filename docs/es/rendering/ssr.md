# SSR (renderizado del servidor)

## Definición

SSR es el valor predeterminado: el servidor representa la página en HTML para cada solicitud. Nada lo habilita y ningún indicador lo desactiva: un proyecto en modo servidor se procesa en cada solicitud a menos que una página declare `revalidate`.

## como funciona

<!-- router:fbr,custom -->
| Archivo de ruta | ¿Qué produce el HTML? | cuando |
|---|---|---|
| `.nexy` | el módulo compilado Python, hasta Jinja2 | cada solicitud |
| `.md` | Markdown, luego el diseño más cercano | cada solicitud |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | el marco, representado en Node | en la compilación cuando la ruta no tiene diseño; de lo contrario, en el navegador |
| `.py` | nada: devuelve JSON o un `Response` | - |

Una página Markdown y un controlador, uno al lado del otro en el mismo proyecto:

```md filename="src/rutas/changelog.md"
# Changelog

Rendered to HTML on every request, then wrapped in the nearest layout.
```

```python filename="src/rutas/api/health.py"
async def GET():
    return {"status": "ok"}
```

Una ruta componente es el único caso que necesita una segunda oración. En producción, una ruta de componente **sin** un diseño se entrega con el HTML producido en la compilación y el componente lo hidrata. Con un diseño, o en desarrollo, el contenedor está vacío y el componente se representa en el navegador; la página es entonces un caparazón que se llena solo.

La ruta del componente de la tabla, sin diseño, por lo que la producción entrega su HTML desde la compilación:

```tsx filename="src/rutas/precios.tsx"
export default function Pricing() {
  return <h1>Pricing</h1>;
}
```
<!-- /router -->

<!-- router:modular -->
| Un controlador regresa | ¿Qué produce el HTML? | cuando |
|---|---|---|
| `useViews("....nexy")` | el módulo compilado Python, hasta Jinja2 | cada solicitud |
| un `dict`, una lista, un modelo | nada: FastAPI responde JSON | - |

Una vista y un punto final JSON, uno al lado del otro en el mismo módulo:

```nexy filename="src/apps/changelog_view.nexy"
<h1>Changelog</h1>
<p>Rendered to HTML on every request.</p>
```

```python filename="src/apps/site_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/changelog")
class ChangelogController:
    async def get(self):
        return useViews("src/apps/changelog_view.nexy")


@Controller("/api/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```
<!-- /router -->

## Ciclo de vida de renderizado

<!-- router:fbr,custom -->
1. La solicitud llega al enrutador basado en archivos. La ruta coincide y los segmentos dinámicos se convierten en los tipos que declara el componente.

   ```nexy nombre de archivo="src/routes/orders/[id].nexy"
   ---
   id: propiedad[int]
   ---
   <h1>N.º de pedido{{ id + 1000 }}</h1>
   ```

   `/orders/42` representa `Order #1042`; `/orders/abc` responde `404`.
2. El componente se ejecuta. Uno que espera en Node (un documento de cliente) se ejecuta en un grupo de subprocesos, por lo que no detiene el bucle de eventos.
3. El cuerpo se transmite como `text/html`. Un componente que produce trozos los transmite a medida que los produce.
4. El navegador recibe HTML. Las islas se hidratan según su [directiva](islands.md).

Un error generado durante el renderizado se convierte en una página mediante `errors.nexy` cuando el proyecto tiene una: consulte [páginas de error](../routing/fbr/errors/README.md).
<!-- /router -->

<!-- router:modular -->
1. La solicitud llega al controlador. Sus parámetros de ruta se convierten a los tipos que declara el método y se pasan a la vista:

   ```python nombre de archivo="src/apps/order_controller.py"
   desde nexy.decorators importar controlador
   desde nexy.hooks importar useViews


   @Controller("/pedidos/{id}")
   clase Controlador de pedidos:
       asíncrono def get(self, id: int):
           devolver useViews("src/apps/order_view.nexy", contexto={"id": id})
   ```

   ```nexy nombre de archivo="src/apps/order_view.nexy"
   ---
   id: propiedad[int]
   ---
   <h1>N.º de pedido{{ id + 1000 }}</h1>
   ```

   `/orders/42/` representa `Order #1042`; `/orders/abc/` responde `404`.
2. La vista se ejecuta y `useViews` devuelve su HTML como respuesta.
3. El navegador recibe HTML. Las islas se hidratan según su [directiva](islands.md).

Un error generado durante la renderización se responde con la página de error predeterminada.
<!-- /router -->

## cuando usar

- La página muestra algo que pertenece al lector: una sesión, una cuenta, un carrito.
- Los datos deben estar actualizados en cada carga.
- El contenido debe estar en HTML para los rastreadores que no ejecutan JavaScript.
- La página es barata de renderizar: una consulta, una plantilla.

El primer caso, una página que saluda al lector desde la sesión. `useSession` lee la sesión de `useSession` en `nexyconfig.py`, sin la cual falla:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

<!-- router:fbr,custom -->
```nexy filename="src/rutas/cuenta.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/account_view.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

## Configuración

<!-- router:fbr,custom -->
Ninguno. Dos salidas y no tienen el mismo grano:

| Dejar SSR por | haz esto | grano |
|---|---|---|
| una página, con un caché | `revalidate = 60` en su introducción → [ISR](isr.md) | página |
| todo el proyecto, enrutado por el cliente | `useCSR = True` en `nexyconfig.py` → [RSE](csr.md) | proyecto |

El cambio de todo el proyecto, en `nexyconfig.py`. El modo cliente necesita un marco de cliente:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```
<!-- /router -->

<!-- router:modular -->
Ninguno. Cada vista que devuelve un controlador se representa en cada solicitud: [ISR](isr.md) y [CSR](csr.md) son ​​modos del enrutador basado en archivos.
<!-- /router -->

## Ejemplo

<!-- router:fbr,custom -->
```nexy filename="src/rutas/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` ejecuta esta plantilla una vez, con `slug` establecida en `hello`. Una segunda solicitud lo ejecuta nuevamente: no se guarda nada entre los dos. La cadena de consulta no es un accesorio; léala con los ganchos en [navegación](../routing/fbr/navigation/hooks.md).
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/blog_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/post_view.nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello/` ejecuta esta vista una vez, con `slug` establecido en `hello`. Una segunda solicitud lo ejecuta nuevamente: no se guarda nada entre los dos. La cadena de consulta no es un accesorio; léala con `useSearchParams`.
<!-- /router -->

## Limitaciones

- **Un render por solicitud.** Dos visitantes en el mismo segundo pagan cada uno por el render y por las consultas detrás de él.
- **Sin caché.** No hay un caché de respuesta compartido para calentar: con rutas de archivos, [ISR](isr.md) agrega uno por URL.
- **La transmisión por secuencias solo ayuda a un componente que rinde.** Una consulta lenta en la parte superior de la página aún retrasa el primer byte.
- **Sin salida estática.** En el modo servidor, nada se congela en la compilación: no hay modo SSG ni comando de exportación. Consulte [Renderizado](README.md).
- **El escape automático está desactivado** en `.nexy` plantillas. Escapa de valores que no son de confianza con `| e`.

<!-- router:fbr,custom -->
```nexy filename="src/rutas/search.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/search_view.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

## Próximos pasos

<!-- router:fbr,custom -->
- [ISR](isr.md): almacena en caché esta página por URL
<!-- /router -->
- [Islas](islands.md): mantenga SSR y haga que un widget sea interactivo
<!-- router:fbr,custom -->
- [CSR](csr.md): navegación manual al navegador
<!-- /router -->
- [Rendimiento](../deployment/performance.md)
