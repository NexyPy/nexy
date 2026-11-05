# O que é Nexy?

Nexy é uma estrutura Python para aplicações web fullstack: suas páginas e sua API residem em um projeto e são atendidas por um servidor.

## O que você ganha

- **Páginas em Python.** Um arquivo `.nexy` é HTML com algumas linhas de Python no topo; um arquivo `.md` também é uma página. Não é necessário JavaScript para renderizar uma página.
- **Uma API no mesmo projeto.** Um arquivo `.py` em `src/routes/` responde a solicitações HTTP: uma função chamada `GET` responde `GET`, uma função chamada `POST` responde `POST`.
- **Documentação da API gratuitamente.** Cada rota da API aparece em um esquema OpenAPI, e Scalar a mostra como uma referência interativa em `/docs`.
- **Formulários que chamam Python.** Um formulário, ou uma chamada digitada no navegador, atinge a mesma função Python.
- **Uma estrutura de frontend quando você quiser.** React, Vue, Svelte, Solid ou Preact, para um componente ou para todo o site.
- **Um comando para funcionar, um para enviar.** `nx dev` recarrega conforme você salva; `nx build` prepara a produção.

## Em que é construído

A versão atual, 2.2, baseia-se em ferramentas que você já deve conhecer:

| Parte | Construído em | O que isso significa para você |
|---|---|---|
| Servidor e API | [FastAPI](https://fastapi.tiangolo.com/) | uma rota de API é uma rota FastAPI: Pydantic validação e dependências funcionam normalmente |
| Referência da API | OpenAPI e [Escalar](https://scalar.com/) | o esquema está em `/openapi.json`, a referência em `/docs` |
| Páginas | Jinja2 | uma página `.nexy` usa tags Jinja2 como `{{ title }}` |
| Front-end (opcional) | [Vite](https://vite.dev/) | apenas com um framework frontend, que também precisa de Node.js |

## Uma primeira página e um primeiro endpoint

Uma página, em `/hello`:

```nexy filename="src/rotas/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

Um endpoint, em `GET /api/items`, listado em `/docs` sem nenhum código extra:

```python filename="src/routes/api/items.py"
from nexy.http import Request


async def GET(request: Request):
    return {"items": []}
```

## O que Nexy deixa para você

O banco de dados, o login e as regras sobre quem pode fazer o que pertencem à sua aplicação, então você escolhe as bibliotecas. [Bancos de dados](../guides/databases.md) e [Middleware e segurança](../guides/middleware-and-security.md) mostram onde cada um se conecta.

## Próximas etapas

- [Instalação](installation.md): instale uv e crie um projeto
- [Início rápido](quick-start.md): execute, altere uma página, construa-a
- [Conceitos básicos](core-concepts.md): as poucas palavras que o restante dos documentos usa
