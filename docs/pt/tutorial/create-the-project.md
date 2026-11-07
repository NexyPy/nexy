# Construa um aplicativo de notas com Nexy, parte 1: crie o projeto

A Parte 1 do tutorial cria o projeto que você transformará em um aplicativo de notas e o executa em seu navegador em cerca de cinco minutos.

**Antes de começar:** [uv](https://docs.astral.sh/uv/) e Node.js 20 ou mais recente. O tutorial segue o roteador escolhido no topo do menu: mude para lá e tudo mostra os arquivos daquele roteador.

## O que você vai construir

Ao final do tutorial, o aplicativo possui páginas e uma API JSON para notas, um banco de dados, contas, notas compartilhadas por e-mail, atualizações ao vivo, testes e uma construção de produção. Cada parte termina com um aplicativo em execução, para que você possa parar após qualquer uma delas.

## Crie o projeto

```bash
uvx nexy new notes
```

Responda às perguntas desta forma:

| Pergunta | Resposta |
|---|---|
| Roteador baseado em arquivo? | `Yes` para os roteadores personalizados e baseados em arquivo, `No` para o modular |
| Tipo de projeto | `Web` |
| Roteamento do lado do cliente | `No`: o servidor renderiza as páginas |
| Estrutura do cliente | `React`: volta na unidade 4, para ilhas |
| Estilo | `Tailwind CSS` |
| Alias de importação | `@` |
| ORM | `No database`: parte 5 adiciona um |

<!-- router:custom -->
O roteador personalizado é aquele baseado em arquivo mais um `APIRouter` que você já possui. O tutorial cria o aplicativo com arquivos; [Incluir um roteador FastAPI existente](../routing/custom/README.md) mostra como montar o seu próximo a eles.
<!-- /router -->

## Execute-o

```bash
cd notes
source .venv/bin/activate    # Windows: .venv\Scripts\activate
nexy dev
```

Abra <http://localhost:3000>. Você deverá ver a página de boas-vindas. Deixe o `nexy dev` rodando: a partir de agora, cada arquivo que você salvar recarregará o navegador.

## O que você aprendeu

- `uvx nexy new` cria um projeto e instala seus pacotes Python e JavaScript.
- `nexy dev` serve e recarrega ao salvar.
<!-- router:fbr,custom -->
- As páginas ficam em `src/routes/`: a próxima parte adiciona uma.
<!-- /router -->
<!-- router:modular -->
- Os controladores e suas visualizações residem em `src/apps/`: a próxima parte adiciona um.
<!-- /router -->

## Próximas etapas

- [Parte 2: páginas e layouts](pages-and-layouts.md)
- [Estrutura do projeto](../getting-started/project-structure.md): para que serve cada arquivo do projeto
