# Nexy e NestJS

O roteador modular é inspirado em NestJS: controladores, módulos e injeção de construtor. É uma camada fina sobre FastAPI, portanto não tenta reproduzir tudo de NestJS. Esta página lista ambos os lados.

## O que combina

| NestJS | Nexy |
|---|---|
| `@Controller('users')` | `@Controller("/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` com os mesmos quatro atributos de classe |
| `@Injectable()` | `@Injectable()` |
| Injeção de construtor | `__init__` parâmetros resolvidos a partir de anotações de tipo |
| Singleton, solicitação e escopos transitórios | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (uma dependência FastAPI) |
| `@ApiOperation`, `@ApiResponse` (arrogância) | `@UseRoute`, `@UseResponse` (OpenAPI, servido em `/docs`) |
| WebSocket portais | `async def SOCKET(...)` em um controlador |
| Validação DTO (`class-validator`) | Pydantic modelos, nativos de FastAPI |
| Detecção de dependência circular | `RecursionError` nomeando a classe |

O mesmo controlador e seu serviço injetado, NestJS primeiro:

```ts filename="usuários.controller.ts"
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


@Controller("/users")
class UserController:
    def __init__(self, users: UserService) -> None:
        self.users = users

    async def get(self) -> list[dict]:
        return self.users.find_all()
```

## O que difere

- Handlers são métodos nomeados após o verbo HTTP (`get`, `post`...), um por controlador.
- Guardas e decoradores de middleware são FastAPI `Depends`, não classes com `canActivate`.
- Parâmetros (`@Body`, `@Param`, `@Query`) são parâmetros FastAPI: anotações de tipo, `Query`, `Path`, `Body`.
- Pipes são Pydantic validação e FastAPI dependências.

`@Query()`, um DTO e uma classe de guarda tornam-se uma anotação, um modelo Pydantic e uma função:

```python filename="src/apps/posts/post_controller.py"
from fastapi import Header, HTTPException, Query
from pydantic import BaseModel
from nexy.decorators import Controller, UseGuard


class NewPost(BaseModel):
    title: str


def require_token(x_token: str = Header(...)) -> None:
    if x_token != "secret":
        raise HTTPException(status_code=403, detail="Forbidden")


@Controller("/posts")
@UseGuard(require_token)
class PostController:
    async def get(self, limit: int = Query(10)) -> list[dict]:
        return []

    async def post(self, body: NewPost) -> dict:
        return {"title": body.title}
```

## O que está faltando

| NestJS recurso | Status em Nexy |
|---|---|
| Provedores personalizados (`useValue`, `useFactory`, `useClass`, tokens de string) | não disponível: apenas `@Injectable()` turmas |
| Injetando por interface ou classe abstrata | não disponível |
| Encapsulamento de módulo | não aplicado: o contêiner abrange todo o processo, `exports` controla apenas a resolução antecipada |
| Módulos dinâmicos e globais (`forRoot`, `@Global`) | não disponível |
| Ganchos de ciclo de vida (`onModuleInit`, `onApplicationShutdown`) | não disponível |
| Interceptadores | use middleware ASGI (`useMiddlewares`) ou dependências |
| Filtros de exceção | use manipuladores de exceção FastAPI |
| Módulo de teste com substituições de provedor | nenhuma API pública; use FastAPI `dependency_overrides` e `TestClient` |
| Módulo de configuração, agendamento, filas, CQRS, microsserviços, cache | não faz parte da Nexy; use o ecossistema Python |

No lugar de um provedor `useFactory`, uma função simples atrás de `Depends`, que um teste substitui por `dependency_overrides`:

```python filename="src/apps/reports/report_controller.py"
from fastapi import Depends
from nexy.decorators import Controller


def get_settings() -> dict:
    return {"currency": "EUR"}


@Controller("/reports")
class ReportController:
    async def get(self, settings: dict = Depends(get_settings)) -> dict:
        return {"currency": settings["currency"]}
```

## Quando escolher

Escolha o roteador modular quando desejar uma estrutura baseada em classes com injeção para uma API maior. Escolha o roteador baseado em arquivo quando a estrutura da URL for o princípio de organização. Ambos são estruturados por `nx new`, executados na mesma aplicação FastAPI e podem coexistir.

> [!NOTE]
> os itens que faltam acima são a lacuna honesta. Se você precisar de `useFactory` provedores ou provedores substituíveis em testes hoje, mantenha a lógica em funções simples e FastAPI `Depends`, que compõem e substituem naturalmente.

## Próximas etapas

- [Injeção de dependência](dependency-injection.md)
- [Guardas e metadados](guards-and-metadata.md)
- [Teste](../../guides/testing.md)
