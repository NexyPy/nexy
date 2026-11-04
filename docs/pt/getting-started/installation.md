# Instalação

## Requisitos

| Requisito | Por que |
|---|---|
| Python 3.12+ | `requires-python` em `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | cria o projeto, instala seus pacotes e executa Nexy |
| Node.js 18+ | apenas para uma estrutura de cliente (React, Vue, Svelte, Solid, Preact) |

Um projeto sem uma estrutura de cliente não precisa de Node.js.

## Instale o UV primeiro

`uvx` não é uma ferramenta separada: ela vem com uv, então instale o uv antes de qualquer coisa.

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verifique com `uv --version` e `uvx --version`.

## Crie um projeto

```bash
uvx nexy new my-app
```

`uvx` executa o Nexy em um ambiente temporário e não deixa nada para trás. Isso é suficiente para **criar** um
projeto (`new`, `init`) e nada mais: o ambiente temporário contém Nexy e nenhum outro
pacote. `nexy new` cria o próprio ambiente virtual do projeto, `.venv`, e instala seus pacotes
lá.

`nexy new my-app` faz quatro perguntas: roteador (baseado em arquivo ou modular), tipo de projeto (web ou API),
estrutura do cliente, ORM. A instalação das dependências do Python e do Node é executada com uma linha por
etapa e sua duração. Consulte [CLI](../reference/cli.md).

Ignore as solicitações com um modelo registrado:

```bash
uvx nexy new my-app --template <name>
```

## Trabalhar dentro do ambiente virtual do projeto

Todos os outros comandos (`nexy dev`, `nexy build`, `nexy migrate`...) devem ser executados **dentro do projeto
ambiente virtual**. É aí que residem seus próprios pacotes: seu ORM, suas bibliotecas e o Nexy
o projeto foi construído com. Fora dele, um projeto que precisa de `sqlmodel` falha com
`ModuleNotFoundError: No module named 'sqlmodel'`.

Ative-o uma vez por terminal, na pasta do projeto:

| Shell | Comando |
|---|---|
| PowerShell, cmd (Windows) | `.venv\Scripts\activate` |
| macOS, Linux | `source .venv/bin/activate` |

O prompt então começa com `(.venv)`. A partir daí:

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Abra <http://localhost:3000>.

Para pular a ativação, deixe uv fazer isso com um comando: `uv run nexy dev`.

> [!NOTA]
> `nexy` e `nx` são o mesmo binário. Uma cópia instalada com `uv tool install
> nexy` lives in its own environment, like `uvx`, então use-o para criar projetos e executar tudo
> else do ambiente do projeto.

## Adicionar Nexy a um projeto existente

Execute-o a partir do ambiente virtual do projeto, com Nexy entre seus pacotes (`uv add nexy`):

```bash
nexy init
```

## Próximas etapas

- [Início rápido](quick-start.md)
- [Tutorial](tutorial.md)
- [Estrutura do projeto](project-structure.md)
- [Solução de problemas](../guides/troubleshooting.md)