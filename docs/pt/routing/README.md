# Roteamento

Nexy possui dois roteadores nativos. Você pode escolher um por recurso; eles podem coexistir no mesmo aplicativo.

**Não tenho certeza? Use roteamento baseado em arquivo.** Abrange páginas e endpoints de API sem configuração. Adicione o roteador modular quando um back-end precisar de controladores, serviços injetados ou protetores.

| Você está construindo | Usar |
|---|---|
| Páginas, conteúdo, um site com alguns endpoints | Baseado em arquivo |
| Uma grande API com serviços compartilhados entre rotas | Modular |
| Ambos: páginas para pessoas, uma API estruturada para máquinas | Baseado em arquivo e modular juntos |

<!-- router:fbr,custom -->
```diagram filename="O roteador baseado em arquivo, em resumo"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```
<!-- /router -->

<!-- router:modular -->
```diagram filename="O roteador modular, em resumo"
@Controller()             class AppController   →  /
@Controller("/about")     class AboutController →  /about/
@Controller("/api/users") class UserController  →  /api/users/  (get, post, …)
@Module()                 class AppModule       →  lists the controllers
useRouter = AppModule     nexyconfig.py         →  mounts the module
```
<!-- /router -->

| Roteador | Fonte | Ativado por |
|---|---|---|
| [Baseado em arquivo (FBR)](fbr/README.md) | cada arquivo em `src/routes/` | o diretório existe |
| [Modular](modular/README.md) | controladores e módulos | `useRouter = AppModule` em `nexyconfig.py` |

FBR é verificado sempre `src/routes/` existe, mesmo com um roteador modular montado.

## Coexistência e prioridades

Você pode combinar integração FBR, modular e personalizada. Nexy registra essas rotas na ordem em que são descobertas. Se dois roteadores definirem o mesmo caminho de URL, o primeiro registrado vence. 

*Observação: Nexy atualmente não fornece diagnóstico para colisões de URL; a primeira rota para reivindicar um caminho simplesmente obscurece as outras.*

<!-- router:fbr,custom -->
## Roteamento baseado em arquivo

Uma rota é um arquivo. A URL é o caminho em `src/routes/`, menos a extensão. Assim como Next.js, um projeto está em um dos dois modos, escolhidos com `useCSR`:

| | `useCSR = False` (padrão) | `useCSR = True` |
|---|---|---|
| Páginas | `.nexy`, `.md`, `.mdx` | arquivos da sua estrutura de cliente |
| Layout raiz | `layout.nexy` | `layout.tsx` (React) |
| Componentes do cliente | permitido, como ilhas dentro das páginas | as próprias páginas |
| Rotas de API | `.py` | `.py` |

Consulte [Modo servidor e modo cliente](fbr/modes.md).

| Seção | O que cobre |
|---|---|
| [fbr/páginas](fbr/pages/README.md) | páginas, [rotas dinâmicas](fbr/pages/dynamic-routes.md) e grupos de rotas |
| [fbr/layouts](fbr/layouts/README.md) | `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` |
| [fbr/manipuladores](fbr/handlers/README.md) | `.py` manipuladores de rota, [validação e erros](fbr/handlers/validation-and-errors.md) |
| [fbr/dependências](fbr/dependencies/README.md) | `dependencies.py` e guardas, herdados por diretório |
| [fbr/middleware](fbr/middleware/README.md) | `middleware.py`, herdado por diretório |
| [fbr/erros](fbr/errors/README.md) | `notfound.nexy`, `errors.nexy`, erros JSON |
| [fbr/navegação](fbr/navigation/linking-and-navigating.md) | vinculação, navegação do cliente, [ganchos](fbr/navigation/hooks.md) |
| [fbr/tempo real](fbr/realtime/websocket.md) | WebSocket manipuladores |
| [fbr/herança](fbr/inheritance.md) | como layouts, dependências e páginas de erro herdam |
<!-- /router -->

## Roteamento modular

Controladores, módulos e injeção de dependência, no estilo de NestJS. Consulte [Roteamento modular](modular/README.md) e [Nexy e NestJS](modular/vs-nestjs.md).

<!-- router:modular -->
| Seção | O que cobre |
|---|---|
| [modular](modular/README.md) | `@Controller`, `@Module`, importações e exportações |
| [modular/injeção de dependência](modular/dependency-injection.md) | `@Injectable`, escopos e o contêiner |
| [modular/guardas e metadados](modular/guards-and-metadata.md) | `@UseGuard`, `@UseResponse` e os OpenAPI metadados |

Um controlador retorna uma visualização `.nexy` com `useViews` e a passa para seu layout manualmente: não há `layout.nexy` aplicado por pasta.
<!-- /router -->

## Integração Personalizada

Você também pode integrar um roteador FastAPI existente em seu projeto Nexy. Consulte [Integração de roteamento personalizado](custom/README.md).

## Próximas etapas

<!-- router:fbr,custom -->
- [Roteamento baseado em arquivo](fbr/README.md)
<!-- /router -->
<!-- router:modular -->
- [Roteamento modular](modular/README.md)
<!-- /router -->
- [Renderização](../rendering/README.md)
- [Visualizações](../views/README.md): o que há dentro dos arquivos
