# Nexy e NestJS

O roteador modular é inspirado em NestJS: controladores, módulos e injeção de construtor. É uma camada fina sobre FastAPI, portanto não tenta reproduzir tudo de NestJS. Esta página lista ambos os lados.

## O que combina

| NestJS | Nexy |
|---|---|
| `@Controller('users')` | `@Controller(prefix="/users")` |
| `@Module({ controllers, providers, imports, exports })` | `@Module()` com os mesmos quatro atributos de classe |
| `@Injectable()` | `@Injectable()` |
| Parâmetros de injeção de construtor | `__init__` resolvidos a partir de anotações de tipo |
| Singleton, solicitação e escopos transitórios | `Scope.SINGLETON`, `Scope.REQUEST`, `Scope.TRANSIENT` |
| `@UseGuards(AuthGuard)` | `@UseGuard(guard)` (uma dependência FastAPI) |
| `@ApiOperation`, `@ApiResponse` (arrogância) | `@UseRoute`, `@UseResponse` (OpenAPI, servido em `/docs`) |
| WebSocket gateways | `async def SOCKET(...)` em um controlador |
| Validação DTO (`class-validator`) | Pydantic modelos, nativos de FastAPI |
| Detecção de dependência circular | `RecursionError` nomeando a classe |

## O que difere

- Handlers são métodos nomeados após o verbo HTTP (`get`, `post`...), um por controlador.
- Guardas e decoradores de middleware são FastAPI `Depends`, não classes com `canActivate`.
- Parâmetros (`@Body`, `@Param`, `@Query`) são parâmetros FastAPI: anotações de tipo, `Query`, `Path`, `Body`.
- Pipes são Pydantic validação e FastAPI dependências.

## O que está faltando

| NestJS recurso | Status no Nexy |
|---|---|
| Provedores personalizados (`useValue`, `useFactory`, `useClass`, tokens de string) | não disponíveis: apenas `@Injectable()` classes |
| Injeção por interface ou classe abstrata | não disponível |
| Encapsulamento do módulo | não aplicado: o contêiner abrange todo o processo, `exports` controla apenas a resolução antecipada |
| Módulos dinâmicos e globais (`forRoot`, `@Global`) | não disponíveis |
| Ganchos de ciclo de vida (`onModuleInit`, `onApplicationShutdown`) | não disponíveis |
| Interceptores | usam middleware ASGI (`useMiddlewares`) ou dependências |
| Filtros de exceção | usam FastAPI manipuladores de exceção |
| Módulo de teste com substituições de provedor | sem API pública; use FastAPI `dependency_overrides` e `TestClient` |
| Módulo de configuração, agendamento, filas, CQRS, microsserviços, cache | não faz parte do Nexy; use o ecossistema Python |

## Quando escolher

Escolha o roteador modular quando desejar uma estrutura baseada em classes com injeção para uma API maior. Escolha o roteador baseado em arquivo quando a estrutura da URL for o princípio de organização. Ambos são estruturados por `nx new`, executados na mesma aplicação FastAPI e podem coexistir.

> [!NOTA]
> os itens que faltam acima são a lacuna honesta. Se você precisar de `useFactory` provedores ou provedores substituíveis em testes hoje, mantenha a lógica em funções simples e FastAPI `Depends`, que compõem e substituem naturalmente.

## Próximas etapas

- [Injeção de dependência](dependency-injection.md)
- [Guardas e metadados](guards-and-metadata.md)
- [Teste](../../guides/testing.md)
