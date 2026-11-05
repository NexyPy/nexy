# Nexy y NestJS

El enrutador modular está inspirado en NestJS: controladores, módulos e inyección de constructor. Es una capa delgada sobre FastAPI, por lo que no intenta reproducir todo NestJS. Esta página enumera ambos lados.

## que coincide

| NestJS | nexy |
|---|---|
| `@Controller('users')` | `@Controller(prefix="/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` con los mismos cuatro atributos de clase |
| `@Injectable()` | `@Injectable()` |
| inyección de constructor | `__init__` parámetros resueltos a partir de anotaciones de tipo |
| Ámbitos singleton, de solicitud y transitorios | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (una dependencia FastAPI) |
| `@ApiOperation`, `@ApiResponse` (Arrogancia) | `@UseRoute`, `@UseResponse` (OpenAPI, servido en `/docs`) |
| WebSocket puertas de enlace | `async def SOCKET(...)` en un controlador |
| Validación DTO (`class-validator`) | Modelos Pydantic, nativos de FastAPI |
| Detección de dependencia circular | `RecursionError` nombrando la clase |

El mismo controlador y su servicio inyectado, NestJS primero:

```ts filename="usuarios.controlador.ts"
@Injectable()
export class UsersService {
  findAll() {
    return [{ id: 1, name: "Ada" }];
  }
}

@Controller("users")
export class UsersController {
  constructor(private readonly users: UsersService) {}

  @Get()
  findAll() {
    return this.users.findAll();
  }
}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller, Injectable


@Injectable()
class UserService:
    def find_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]


@Controller(prefix="/users")
class UserController:
    def __init__(self, users: UserService) -> None:
        self.users = users

    async def get(self) -> list[dict]:
        return self.users.find_all()
```

## que difiere

- Los controladores son métodos que llevan el nombre del verbo HTTP (`get`, `post`...), uno por controlador.
- Los guardias y decoradores de middleware son FastAPI `Depends`, no clases con `canActivate`.
- Los parámetros (`@Body`, `@Param`, `@Query`) son parámetros FastAPI: anotaciones de tipo, `Query`, `Path`, `Body`.
- Las canalizaciones son Pydantic validación y FastAPI dependencias.

`@Query()`, un DTO y una clase de guardia se convierten en una anotación, un modelo Pydantic y una función:

```python filename="src/apps/posts/post_controller.py"
from fastapi import Header, HTTPException, Query
from pydantic import BaseModel
from nexy.decorators import Controller, UseGuard


class NewPost(BaseModel):
    title: str


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller(prefix="/posts")
@UseGuard(require_token)
class PostController:
    async def get(self, limit: int = Query(10)) -> list[dict]:
        return []

    async def post(self, body: NewPost) -> dict:
        return {"title": body.title}
```

## lo que falta

| NestJS característica | Estado en Nexy |
|---|---|
| Proveedores personalizados (`useValue`, `useFactory`, `useClass`, tokens de cadena) | no disponible: solo `@Injectable()` clases |
| Inyectar por interfaz o clase abstracta | no disponible |
| Encapsulación de módulos | no aplicado: el contenedor abarca todo el proceso, `exports` solo controla la resolución entusiasta |
| Módulos dinámicos y globales (`forRoot`, `@Global`) | no disponible |
| Ganchos del ciclo de vida (`onModuleInit`, `onApplicationShutdown`) | no disponible |
| Interceptores | utilizar middleware ASGI (`useMiddlewares`) o dependencias |
| Filtros de excepción | utilizar FastAPI controladores de excepciones |
| Módulo de prueba con anulaciones de proveedores | sin API pública; utilice FastAPI `dependency_overrides` y `TestClient` |
| Módulo de configuración, programación, colas, CQRS, microservicios, almacenamiento en caché | no forma parte de Nexy; utilizar el ecosistema Python |

En lugar de un proveedor `useFactory`, una función simple detrás de `Depends`, que una prueba anula con `dependency_overrides`:

```python filename="src/apps/reports/report_controller.py"
from fastapi import Depends
from nexy.decorators import Controller


def get_settings() -> dict:
    return {"currency": "EUR"}


@Controller(prefix="/reports")
class ReportController:
    async def get(self, settings: dict = Depends(get_settings)) -> dict:
        return {"currency": settings["currency"]}
```

## Cuando escogerlo

Elija el enrutador modular cuando desee una estructura basada en clases con inyección para una API más grande. Elija el enrutador basado en archivos cuando la estructura de URL sea el principio organizador. Ambos están estructurados por `nx new`, se ejecutan en la misma FastAPI aplicación y pueden coexistir.

> [!NOTE]
> Los elementos que faltan arriba son la brecha honesta. Si necesita proveedores `useFactory` o proveedores reemplazables en las pruebas actuales, mantenga la lógica en funciones simples y FastAPI `Depends`, que se componen y anulan de forma natural.

## Próximos pasos

- [Inyección de dependencia](dependency-injection.md)
- [Guardias y metadatos](guards-and-metadata.md)
- [Pruebas](../../guides/testing.md)
