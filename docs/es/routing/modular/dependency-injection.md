# inyección de dependencia

Nexy resuelve las dependencias del constructor para controladores y servicios. Una clase se inscribe con `@Injectable()`.

## Inyectar un servicio

```python filename="src/apps/users/user_service.py"
from nexy.decorators import Injectable


@Injectable()
class UserService:
    def get_all(self) -> list[dict]:
        return [{"id": 1, "name": "Ada"}]
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller
from .user_service import UserService


@Controller("/users")
class UserController:
    def __init__(self, svc: UserService) -> None:
        self.svc = svc

    def get(self) -> list[dict]:
        return self.svc.get_all()
```

Registre el controlador en un módulo. Incluir el servicio en `providers` también lo resuelve rápidamente al inicio:

```python filename="src/apps/users/users_module.py"
from nexy.decorators import Module
from .user_controller import UserController
from .user_service import UserService


@Module()
class UsersModule:
    controllers = [UserController]
    providers = [UserService]
```

## Cómo funciona la resolución

- Cada parámetro `__init__` se resuelve a partir de su **anotación de tipo**. La anotación debe ser una clase `@Injectable()` o el parámetro debe tener un valor predeterminado; de lo contrario, la resolución plantea `ValueError`.
- Los controladores se crean instancias con `Container.resolve()` al inicio.
- Un ciclo de dependencia plantea `RecursionError` nombrar la clase.
- Los servicios pueden inyectar otros servicios, a cualquier profundidad.

## Alcances

```python
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class CurrentUser: ...
```

| Alcance | Toda la vida |
|---|---|
| `Scope.SINGLETON` (predeterminado) | una instancia para todo el proceso |
| `Scope.REQUEST` | una instancia por contexto de solicitud |
| `Scope.TRANSIENT` | una nueva instancia en cada resolución |

## el contenedor

```python
from nexy.decorators import Container

service = Container.resolve(UserService)
```

La construcción de una clase `@Injectable()` usted mismo genera `TypeError`: el contenedor es dueño de su ciclo de vida. Utilice `Container.resolve(...)` o reciba la clase a través de otro constructor.

`Container.clear_request_scope()` elimina las instancias de la solicitud actual.

## Parámetros de ruta

FastAPI `Depends` funciona como de costumbre para los parámetros del controlador, junto a la inyección del constructor:

```python
from fastapi import Depends


def get(self, limit: int = Depends(pagination)) -> list[dict]: ...
```

## Límites

El contenedor abarca todo el proceso. Los proveedores no están aislados por módulo, `exports` solo decide qué proveedores resuelve con entusiasmo un módulo de importación y no hay una API pública para intercambiar un proveedor en las pruebas. Consulte [Nexy y NestJS](vs-nestjs.md) para obtener una comparación completa.

## Próximos pasos

- [Guardias y metadatos](guards-and-metadata.md)
- [Pruebas](../../guides/testing.md)
