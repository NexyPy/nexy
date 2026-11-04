# Nexy e NestJS

O roteador modular é inspirado no NestJS: controladores, módulos e injeção de construtor. É um
camada fina sobre FastAPI, para que não tente reproduzir todo o NestJS. Esta página lista ambos os lados.

## O que corresponde

| NestJS | Nexy |
|---|---|
| `@Controller('users')` | `@Controller(prefix="/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` com os mesmos quatro atributos de classe |
| `@Injectable()` | `@Injectable()` |
| Injeção de construtor | `__init__` parâmetros resolvidos a partir de anotações de tipo |
| Singleton, solicitação e escopos transitórios | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (uma dependência FastAPI) |
| `@ApiOperation`, `@ApiResponse` (Swagger) | `@UseRoute`, `@UseResponse` (OpenAPI, veiculado em `/docs`) |
| Gateways WebSocket | `async def SOCKET(...)` em um controlador |
| Validação DTO (`class-validator`) | Modelos Pydantic, nativos de FastAPI |
| Detecção de dependência circular | `RecursionError` nomeando a classe |

## O que difere

- Handlers são métodos nomeados após o verbo HTTP (`get`, `post`...), um por controlador.
- Guardas e decoradores de middleware são FastAPI `Depends`, não classes com `canActivate`.
- Parâmetros (`@Body`, `@Param`, `@Query`) são parâmetros FastAPI: anotações de tipo, `Query`, `Path`,
  `Body`.
- Pipes são validação Pydantic e dependências FastAPI.

## O que está faltando

| Recurso NestJS | Status no Nexy |
|---|---|
| Provedores personalizados (`useValue`, `useFactory`, `useClass`, tokens de string) | não disponíveis: apenas `@Injectable()` classes |
| Injeção por interface ou classe abstrata | não disponível |
| Encapsulamento do módulo | não aplicado: o contêiner abrange todo o processo, `exports` controla apenas a resolução antecipada |
| Módulos dinâmicos e globais (`forRoot`, `@Global`) | não disponíveis |
| Ganchos de ciclo de vida (`onModuleInit`, `onApplicationShutdown`) | não disponíveis |
| Interceptores | usam middleware ASGI (`useMiddlewares`) ou dependências |
| Filtros de exceção | usam manipuladores de exceção FastAPI |
| Módulo de teste com substituições de provedor | sem API pública; use FastAPI `dependency_overrides` e `TestClient` |
| Módulo de configuração, agendamento, filas, CQRS, microsserviços, cache | não faz parte do Nexy; use o ecossistema Python |

## Quando escolher

Escolha o roteador modular quando desejar uma estrutura baseada em classes com injeção para uma API maior.
Escolha o roteador baseado em arquivo quando a estrutura da URL for o princípio de organização. Ambos estão em andaimes
por `nx new`, executados na mesma aplicação FastAPI e podem coexistir.

> [!NOTA]
> os itens que faltam acima são a lacuna honesta. Se você precisar de `useFactory` provedores
> ou provedores substituíveis em testes hoje, mantenham a lógica em funções simples e FastAPI
> `Depends`, que compõem e substituem naturalmente.

## Próximas etapas

- [Injeção de dependência](dependency-injection.md)
- [Guardas e metadados](guards-and-metadata.md)
- [Testando](../../guides/testing.md)