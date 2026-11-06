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

| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` em um módulo que você importa | `GET` função em `src/routes/users.py` |
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

## De Next.js

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

O backend é Python, então sua API compartilha código com seus dados e trabalho de ML. Os componentes do cliente são hidratados como ilhas em vez de uma árvore de página inteira React.

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

## De back-ends Express ou Node

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
