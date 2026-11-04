# Vindo de outra estrutura

Nexy é FastAPI mais roteamento baseado em arquivo, páginas renderizadas pelo servidor e React, Vue, Svelte opcionais,
Ilhas sólidas ou pré-actas. Esta página mapeia o que você já sabe.

## Da FastAPI

| FastAPI | Nexy |
|---|---|
| `@app.get("/users")` em um módulo que você importa | `GET` função em `src/routes/users.py` |
| `app.include_router(router)` | o caminho do arquivo é a URL; nada para registrar |
| Parâmetro de caminho `/users/{id}` | `src/routes/users/[id].py` |
| `Depends(...)` | ainda `Depends(...)`: manipuladores são manipuladores FastAPI |
| Jinja2 `TemplateResponse` | uma página `.nexy` próxima ao endpoint |
| Execute com `uvicorn main:app` | `nx dev`, depois `nx build && nx start` |

Tudo em `src/routes/*.py` é FastAPI comum: dependências, modelos Pydantic, middleware
e `/docs` continue trabalhando.

## De Next.js

| Next.js | Nexy |
|---|---|
| `app/page.tsx` | `src/routes/index.tsx` ou `index.nexy` |
| `app/blog/[slug]/page.tsx` | `src/routes/blog/[slug].tsx` |
| `app/layout.tsx` (possui `<html>`) | `src/routes/layout.tsx` com `useCSR = True` (React), ou `src/routes/layout.nexy` no modo servidor |
| aninhado `layout.tsx` | aninhado `layout.tsx` / `layout.vue` / `layout.svelte` no modo cliente, aninhado `layout.nexy` no modo servidor |
| `use client` componentes em uma página de servidor | [ilhas](../rendering/islands.md) em modo servidor |
| Manipuladores de rota `route.ts` | `src/routes/api/x.py`, escritos em Python |
| `(group)` pastas | mesmo: `(group)/` |
| Ações do servidor | [`@Action`](../guides/actions.md) funções chamadas de um formulário ou como funções de cliente digitadas |
| `next dev` / `next build` / `next start` | `nx dev` / `nx build` / `nx start` |

O backend é Python, então sua API compartilha código com seus dados e trabalho de ML. Componentes do cliente
hidrate como ilhas em vez de uma árvore React de página inteira.

## De back-ends Express ou Node

| Expresso | Nexy |
|---|---|
| `app.get("/users/:id", handler)` | `src/routes/users/[id].py` com `async def GET(id)` |
| `app.use(middleware)` | Middleware FastAPI, registrado em `nexyconfig.py` |
| `res.json(obj)` | retornar um dict ou um modelo Pydantic |
| Visualizações EJS / Pug | `.nexy` (Jinja2) páginas |
| `npm run dev` | `nx dev` |

## Escolhendo um roteador

| Use | quando |
|---|---|
| Roteador baseado em arquivo | páginas e endpoints mapeados a partir de arquivos; o padrão |
| Roteador modular | controladores, módulos e injeção de dependência, estilo NestJS |

Ambos são estruturados por `nx new` e cobertos pelos mesmos testes ponta a ponta. Veja
[Roteamento](../routing/README.md) e [Roteamento modular](../routing/modular/README.md).

## Onde será o próximo

- [Início rápido](quick-start.md): crie um projeto e execute-o
- [Estrutura do projeto](project-structure.md): onde cada arquivo pertence
- [Routing](../routing/README.md): escolha o roteador