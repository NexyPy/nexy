# O que é Nexy?

Nexy é uma estrutura Python para aplicações web fullstack: suas páginas e sua API residem em um projeto e são atendidas por um servidor.

## O que você ganha

- **Páginas em Python.** Um arquivo `.nexy` é HTML com algumas linhas de Python no topo; um arquivo `.md` também é uma página. Não é necessário JavaScript para renderizar uma página.
<!-- router:fbr -->
- **Uma API no mesmo projeto.** Um arquivo `.py` em `src/routes/` responde a solicitações HTTP: uma função chamada `GET` responde `GET`, uma função chamada `POST` responde `POST`.
<!-- /router -->
<!-- router:modular -->
- **Uma API no mesmo projeto.** Um controlador responde a solicitações HTTP: seu método `get` responde `GET`, seu método `post` responde `POST`, e um módulo agrupa controladores e seus serviços.
<!-- /router -->
<!-- router:custom -->
- **Uma API no mesmo projeto.** O roteador FastAPI que você já possui continua respondendo, e as páginas e arquivos de rota de `src/routes/` respondem ao lado dele.
<!-- /router -->
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

<!-- router:fbr,custom -->
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
<!-- /router -->

<!-- router:modular -->
Uma visualização e os controladores que respondem `/hello/` e `GET /api/items/`. O endpoint está listado em `/docs` sem nenhum código extra, e uma URL sem a última barra redireciona para ele:

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

```python filename="src/apps/hello_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews("src/apps/hello_view.nexy", context={"title": "Hello"})


@Controller("/api/items")
class ItemsController:
    async def get(self):
        return {"items": []}
```

O módulo raiz os lista e `useRouter = AppModule` em `nexyconfig.py` monta-o:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .hello_controller import HelloController, ItemsController


@Module()
class AppModule:
    controllers = [HelloController, ItemsController]
```
<!-- /router -->

## O que Nexy deixa para você

O banco de dados, o login e as regras sobre quem pode fazer o que pertencem à sua aplicação, então você escolhe as bibliotecas. [Bancos de dados](../guides/databases.md) e [Middleware e segurança](../guides/middleware-and-security.md) mostram onde cada um se conecta.

## Próximas etapas

- [Instalação](installation.md): instale uv e crie um projeto
- [Início rápido](quick-start.md): execute, altere uma página, construa-a
- [Conceitos básicos](core-concepts.md): as poucas palavras que o restante dos documentos usa
