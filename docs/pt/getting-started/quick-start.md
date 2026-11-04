# Início rápido

Você criará um projeto Nexy, executá-lo e verá uma mudança de página conforme você o edita. São necessários três
minutos. O [Tutorial](tutorial.md) então adiciona um endpoint e uma construção de produção.

## Antes de começar

| Você precisa de | Por que |
|---|---|
| Python 3.12+ | `requires-python` em `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | fornece `uvx`, cria o projeto e instala seus pacotes |
| Node.js 18+ | somente se você usar uma estrutura de cliente (React, Vue, Svelte, Solid, Preact) |

Ainda não tem UV? Consulte [Instalação](installation.md).

## 1. Crie o projeto

```bash
uvx nexy new my-app
```

`uvx` vem com uv, então instale o uv primeiro. Ele roda o Nexy em um ambiente temporário, suficiente para **criar** o projeto. `nexy new` então faz
o próprio projeto `.venv` e instala seus pacotes lá. Quatro prompts decidem a fiação:

| Aviso | Efeito |
|---|---|
| Roteador baseado em arquivo? | `Yes` verifica `src/routes/`; `No` estrutura o roteador modular em `src/apps/` |
| Tipo de projeto | `Web` adiciona um layout e ativos de cliente, `API` inicia sem visualizações |
| Componente cliente? | adiciona uma estrutura e sua configuração Vite |
| ORM/banco de dados | adiciona uma camada de modelo, ou nada |

Não tenho certeza? Responda `Yes`, `Web` e nenhum componente cliente. Você pode adicionar cada um mais tarde.

## 2. Execute-o

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Abra <http://localhost:3000>. Você deverá ver a página inicial. A porta vem de `usePort`
(padrão `3000`); `--port` e `--host` substituem-no por execução.

> [!NOTA]
> Execute todos os comandos, exceto `new` e `init` dentro do ambiente virtual do projeto, ou prefixe-o
> com `uv run`, como em `uv run nexy dev`. Fora dele, um projeto que precisa `sqlmodel` falha com
> `No module named 'sqlmodel'`.

## 3. Alterar uma página

<!-- router:fbr,custom -->
Um arquivo em `src/routes/` é uma rota. Criar `src/routes/hello.nexy`:

```nexy filename="src/rotas/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```
<!-- /router -->

<!-- router:modular -->
Um controlador retorna uma visualização. Criar `src/apps/hello_view.nexy`:

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

Em seguida, declare a página em `src/apps/app_controller.py` e adicione-a ao módulo:

```python filename="src/apps/app_controller.py"
@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/hello_view.nexy")})
```

```python filename="src/apps/app_module.py"
from .app_controller import AboutController, AppController, HelloController

controllers = [AppController, AboutController, HelloController]
```
<!-- /router -->

Abra <http://localhost:3000/hello>. Mude `"Hello"` para `"Bonjour"` e salve: a página é atualizada
sem recarga manual. Se o código estiver errado, o navegador mostra o erro em vez de uma página em branco.

`prop[str]` declara uma propriedade digitada. A marcação sob o frontmatter é Jinja2 - veja
[arquivos .nexy](../views/nexy/README.md).

## Onde será o próximo

| Você deseja | Ler |
|---|---|
| Adicione um endpoint Python e envie uma compilação | [Tutorial](tutorial.md) |
| Saiba onde cada arquivo pertence | [Estrutura do projeto](project-structure.md) |
| Entenda quem constrói o quê | [Como funciona o Nexy](how-nexy-works.md) |
| Use React, Vue, Svelte, Solid ou Preact | [Visualizações](../views/README.md) |