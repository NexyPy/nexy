# Injeção de dependência

Nexy resolve dependências de construtor para controladores e serviços. Uma turma aceita `@Injectable()`.

## Injetar um serviço

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

Registre o controlador em um módulo. Listar o serviço em `providers` também resolve o problema na inicialização:

```python filename="src/apps/users/users_module.py"
from nexy.decorators import Module
from .user_controller import UserController
from .user_service import UserService


@Module()
class UsersModule:
    controllers = [UserController]
    providers = [UserService]
```

## Como funciona a resolução

- Cada parâmetro `__init__` é resolvido a partir de sua **anotação de tipo**. A anotação deve ser uma classe `@Injectable()` ou o parâmetro deve ter um valor padrão; caso contrário, a resolução aumenta `ValueError`.
- Os controladores são instanciados com `Container.resolve()` na inicialização.
- Um ciclo de dependência gera `RecursionError` nomeando a classe.
- Os serviços podem injetar outros serviços, em qualquer profundidade.

## Escopos

```python
from nexy.decorators import Injectable, Scope


@Injectable(scope=Scope.REQUEST)
class CurrentUser: ...
```

| Escopo | Vitalício |
|---|---|
| `Scope.SINGLETON` (padrão) | uma instância para todo o processo |
| `Scope.REQUEST` | uma instância por contexto de solicitação |
| `Scope.TRANSIENT` | uma nova instância em cada resolução |

## O contêiner

```python
from nexy.decorators import Container

service = Container.resolve(UserService)
```

Construir você mesmo uma classe `@Injectable()` aumenta `TypeError`: o contêiner possui seu ciclo de vida. Use `Container.resolve(...)` ou receba a classe através de outro construtor.

`Container.clear_request_scope()` descarta as instâncias da solicitação atual.

## Parâmetros de rota

FastAPI `Depends` funciona normalmente para parâmetros do manipulador, próximo à injeção do construtor:

```python
from fastapi import Depends


def get(self, limit: int = Depends(pagination)) -> list[dict]: ...
```

## Limites

O contêiner abrange todo o processo. Os provedores não são isolados por módulo, `exports` apenas decide quais provedores um módulo importador resolve avidamente e não há API pública para trocar um provedor em testes. Veja [Nexy e NestJS](vs-nestjs.md) para a comparação completa.

## Próximas etapas

- [Guardas e metadados](guards-and-metadata.md)
- [Teste](../../guides/testing.md)
