# Enrutamiento modular

El enrutamiento modular utiliza clases con decoradores en lugar de archivos en `src/routes/`: controladores
manejan solicitudes, los módulos las agrupan y se inyectan proveedores. Montar el `APIRouter` resultante
con `useRouter` en `nexyconfig.py`.

**Antes de comenzar:** un proyecto Nexy y una página de trabajo. El enrutador modular reemplaza el
uno basado en archivos, así que lea [Enrutamiento](../README.md) primero si aún no ha elegido un enrutador.

| Página | Qué cubre |
|---|---|
| Esta página | Montar un módulo, escribir un controlador, controladores de grupo |
| [Inyección de dependencia](dependency-injection.md) | `@Injectable`, ámbitos, el contenedor |
| [Guardias y metadatos](guards-and-metadata.md) | `@UseGuard`, `@Middleware`, `@UseRoute`, `@UseResponse` |
| [Nexy y NestJS](vs-nestjs.md) | Qué coincide con NestJS y qué no |

## Configurar el enrutador

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule
```

> [!NOTA]
> El enrutamiento basado en archivos sigue funcionando. Si `src/routes/` existe, se escanea incluso
> cuando se establece `useRouter`.

## Escribir un controlador

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.core.types import JsonResponse


@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
```

Los métodos coinciden por nombre, sin distinguir entre mayúsculas y minúsculas: `get`, `post`, `put`, `patch`, `delete`, `options`,
`head`, `trace`.

Un controlador declara un controlador por método HTTP; un duplicado surge al inicio. Añade un prefijo con
`@Controller(prefix="/users")` - cada controlador está montado en `prefix/`. `async def SOCKET(...)` en un
El controlador registra un WebSocket en la misma ruta.

## Controladores de grupo en un módulo

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

`@Module(prefix="/api")` devuelve un `APIRouter`. `controllers` es obligatorio; `providers`, `imports`
y `exports` son opcionales. Los módulos importados se montan como subrurutadores y sus proveedores exportados.
se resuelven al inicio.

## Vistas desde un controlador

Un controlador puede devolver una página. `useViews` representa una vista `.nexy`; anidar uno dentro de otro para envolverlo
en un diseño:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller()
class AppController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/app_view.nexy"),
        })
```

Consulte [Diseños](../fbr/layouts/README.md).

## Ejemplo

Véase `examples/Modular/api/minimal/`.

## Próximos pasos

- [Inyección de dependencia](dependency-injection.md): servicios y alcances
- [Guardias y metadatos](guards-and-metadata.md): proteger y documentar rutas
- [Enrutamiento](../README.md): el enrutador basado en archivos
- [Config](../../reference/config.md): todas las opciones, incluida `useRouter`