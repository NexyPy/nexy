# Vindo de outra estrutura

Nexy é FastAPI mais roteamento baseado em arquivo, páginas renderizadas pelo servidor e ilhas opcionais React, Vue, Svelte, Solid ou Preact. Esta página mapeia o que você já sabe.

Cada framework abaixo também possui uma página própria, tarefa por tarefa, com o código que você conhece e depois o código Nexy:

| Python | Back-end | Pilha completa JavaScript |
|---|---|---|
| [FastAPI](../coming-from/fastapi.md) | [Expressar](../coming-from/express.md), [Rápido](../coming-from/fastify.md) | [Next.js](../coming-from/nextjs.md), [Remix](../coming-from/remix.md) |
| [Flask](../coming-from/flask.md) | [Elísia](../coming-from/elysia.md), [Hono](../coming-from/hono.md) | [Nuxt](../coming-from/nuxt.md) |
| [Django](../coming-from/django.md) | [NestJS](../coming-from/nestjs.md), [Bota de mola](../coming-from/spring-boot.md) | [SvelteKit](../coming-from/sveltekit.md) |
| | [Laravel](../coming-from/laravel.md), [Ruby on Rails](../coming-from/rails.md) | [Astro](../coming-from/astro.md) |

## De FastAPI

<!-- router:fbr,custom -->
| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` em um módulo que você importa | Função `GET` em `src/routes/users.py` |
| `app.include_router(router)` | o caminho do arquivo é o URL; nada para registrar |
| Parâmetro de caminho `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | ainda `Depends(...)`: manipuladores são FastAPI manipuladores |
| Jinja2 `TemplateResponse` | uma página `.nexy` próxima ao endpoint |
| Execute com `uvicorn main:app` | `nx dev`, então `nx build && nx start` |

Tudo em `src/routes/*.py` é comum FastAPI: dependências, Pydantic modelos, middleware e `/docs` continuam funcionando.

O mesmo endpoint, antes e depois:

```python filename="principal.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/rotas/usuários/[id].py"
async def GET(id: int):
    return {"id": id}
```
<!-- /router -->

<!-- router:modular -->
| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` em um módulo que você importa | `async def get(self)` em uma aula `@Controller("/users")` |
| `app.include_router(router)` | o controlador listado no `controllers` de um `@Module` |
| Parâmetro de caminho `/users/{id}` | `@Controller("/users/{id}")`, com `async def get(self, id: int)` |
| `Depends(...)` | ainda `Depends(...)`: um método de controlador é um endpoint FastAPI |
| Jinja2 `TemplateResponse` | `useViews("src/apps/....nexy")`, retornado pelo método |
| Execute com `uvicorn main:app` | `nx dev`, então `nx build && nx start` |

Dependências, Pydantic modelos, middleware e `/docs` continuam funcionando.

O mesmo endpoint, antes e depois:

```python filename="principal.py"
from fastapi import FastAPI

app = FastAPI()


@app.get("/users/{id}")
async def get_user(id: int):
    return {"id": id}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users/{id}")
class UserController:
    async def get(self, id: int):
        return {"id": id}
```
<!-- /router -->

## De Next.js

<!-- router:fbr,custom -->
| Next.js | Nexy |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` ou `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (possui `<html>`) | `src/routes/layout.tsx` com `useCSR = True` (React) ou `src/routes/layout.nexy` no modo servidor |
| aninhado `layout.tsx` | aninhado `layout.tsx` / `layout.vue` / `layout.svelte` no modo cliente, aninhado `layout.nexy` no modo servidor |
| `use client` componentes em uma página do servidor | [ilhas](../rendering/islands.md) em modo servidor |
| Manipuladores de rota `route.ts` | `src/routes/api/x.py`, escrito em Python |
| `(group)` pastas | mesmo: `(group)/` |
| Ações do servidor | [`@Action`](../guides/actions.md) funções chamadas de um formulário ou como funções de cliente digitadas |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

O backend é Python, então sua API compartilha código com seus dados e trabalho de ML. Os componentes do cliente são hidratados como ilhas em vez de uma árvore React de página inteira.

Uma página Next.js se move quase como está, e seu componente `"use client"` se torna uma ilha de uma página do servidor:

```tsx filename="src/rotas/blog/[slug].tsx"
import { useParams } from "@nexy/client";

export default function Post() {
  const { slug } = useParams<{ slug: string }>();
  return <h1>{slug}</h1>;
}
```

```nexy filename="src/rotas/blog/[slug].nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
| Next.js | Nexy |
|---|---|
| `app/page.tsx` | um controlador que retorna `useViews("src/apps/home_view.nexy")` |
| `app/blog/[slug]/page.tsx` | `@Controller("/blog/{slug}")`, com `async def get(self, slug: str)` |
| `app/layout.tsx` (possui `<html>`) | uma visualização de layout que o controlador envolve em torno de sua visualização, por meio de `children` |
| `use client` componentes em uma página do servidor | [ilhas](../rendering/islands.md) em uma vista |
| Manipuladores de rota `route.ts` | um controlador que retorna um dict, escrito em Python |
| Ações do servidor | [`@Action`](../guides/actions.md) funções chamadas de um formulário ou como funções de cliente digitadas |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

O backend é Python, então sua API compartilha código com seus dados e trabalho de ML. Os componentes do cliente são hidratados como ilhas em vez de uma árvore React de página inteira.

Uma página Next.js se torna um controlador e sua visualização, e seu componente `"use client"` uma ilha da visualização:

```python filename="src/apps/blog/post_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/blog/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/blog/post_view.nexy"
---
from "@/components/Comments.tsx" import Comments

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Comments post="{{ slug }}" directive="client:visible" />
```
<!-- /router -->

## De back-ends Express ou Node

<!-- router:fbr,custom -->
| Expresso | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` com `async def GET(id)` |
| `app.use(middleware)` | FastAPI middleware, registrado em `nexyconfig.py` |
| `res.json(obj)` | retornar um dict ou um modelo Pydantic |
| Visualizações EJS/Pug | `.nexy` (Jinja2) páginas |
| `npm run dev` | `nx dev` |

`app.use(...)` torna-se um campo de `nexyconfig.py` e `res.json(...)` torna-se um valor de retorno:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/rotas/usuários/[id].py"
async def GET(id: int):
    return {"id": id, "name": "Ada"}  # res.json({ id, name })
```
<!-- /router -->

<!-- router:modular -->
| Expresso | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `@Controller("/users/{id}")`, com `async def get(self, id: int)` |
| `app.use(middleware)` | FastAPI middleware, registrado em `nexyconfig.py` |
| `res.json(obj)` | retornar um dict ou um modelo Pydantic |
| Visualizações EJS/Pug | `.nexy` (Jinja2) visualizações, retornadas por `useViews` |
| `npm run dev` | `nx dev` |

`app.use(...)` torna-se um campo de `nexyconfig.py` e `res.json(...)` torna-se um valor de retorno:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {"allow_origins": ["https://example.com"]}
    useGZip = {"minimum_size": 1000}
```

```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users/{id}")
class UserController:
    async def get(self, id: int):
        return {"id": id, "name": "Ada"}  # res.json({ id, name })
```
<!-- /router -->

## Escolhendo um roteador

| Usar | Quando |
|---|---|
| Roteador baseado em arquivo | páginas e endpoints mapeados a partir de arquivos; o padrão |
| Roteador modular | controladores, módulos e injeção de dependência, estilo NestJS |

O roteador modular em dois arquivos: um controlador e o módulo `nexyconfig.py` aponta com `useRouter = AppModule`:

```python filename="src/apps/app_controller.py"
from nexy.decorators import Controller


@Controller()
class AppController:
    async def get(self):
        return {"message": "Hello"}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module
from .app_controller import AppController


@Module()
class AppModule:
    controllers = [AppController]
```

Ambos são estruturados por `nx new` e cobertos pelos mesmos testes ponta a ponta. Consulte [Roteamento](../routing/README.md) e [Roteamento modular](../routing/modular/README.md).

## Onde será o próximo

- [Início rápido](quick-start.md): crie um projeto e execute-o
- [Estrutura do projeto](project-structure.md): onde cada arquivo pertence
- [Roteamento](../routing/README.md): escolha o roteador
