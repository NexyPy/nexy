# Agentes de codificação

Um projeto feito com `nx new` carrega as regras que um agente de codificação precisa para escrever o código Nexy do seu jeito: a ordem de trabalho, o código e as regras de escrita, e uma habilidade por tópico. Esta página diz o que você obtém, para onde vai e como mantê-lo atualizado. Trabalhar no Nexy em si é um trabalho diferente: ler a raiz do repositório `AGENTS.md`.

## O que `nx new` adiciona

| Arquivo | Lido por | Retém |
|---|---|---|
| `AGENTS.md` | Codex, OpenCode | a pilha do projeto, a ordem de trabalho, as regras, a lista de habilidades |
| `CLAUDE.md` | Claude Code | uma linha, `@AGENTS.md`, então ambos leem o mesmo texto |
| `.agents/skills/` | Codex, OpenCode | as habilidades |
| `.claude/skills/` | Claude Code, OpenCode | as mesmas habilidades |

`AGENTS.md` é curto e personalizado. Um projeto Vue roteado pelo cliente lê "roteado pelo cliente, Vue, estilizado com Tailwind"; um projeto de API é informado de que não há visualizações. Somente as habilidades adequadas são copiadas: um projeto React obtém `nexy-react` e nenhuma habilidade Vue, um projeto de servidor obtém as habilidades `.nexy` e Markdown, um projeto de API não obtém nenhuma habilidade sobre visualizações.

Para pular tudo isso, crie o projeto com `nx new --no-agents`.

## As habilidades

| Habilidade | Capas |
|---|---|
| `nexy-principles` | ordem de trabalho, regras de código, regras de redação |
| `nexy-ux-audit` | a experiência e a auditoria de arquitetura de informação a serem executadas antes de qualquer visão |
| `nexy-project` | modos, pastas, convenções de arquivos, configuração, comandos |
| `nexy-file` | `.nexy` páginas, adereços, ganchos, ilhas |
| `nexy-markdown` | `.md` e `.mdx` conteúdo |
| `nexy-react`, `nexy-preact`, `nexy-solid`, `nexy-vue`, `nexy-svelte` | código idiomático para a estrutura do cliente |
| `nexy-styling` | Tailwind, UnoCSS ou CSS simples e os tokens de design |
| `nexy-backend` | Manipuladores de API, ações, WebSocket, ISR, middleware |
| `nexy-modular` | controladores, módulos, injeção e proteções do roteador modular |
| `nexy-security` | dependências, entrada, sessões, autorização, segredos |
| `nexy-testing` | o primeiro loop de teste e as portas |
| `nexy-framework-dev` | mudando o próprio Nexy, em vez de um projeto construído com Nexy |

As regras que eles impõem: auditar a experiência antes de construir uma visualização, escrever primeiro o teste com falha, uma função faz um tratamento, uma classe carrega uma intenção, uma pasta contém um conjunto de intenções relacionadas, nenhum emoji, ícones SVG reais, texto simples escrito para pessoas e nenhum script DOM escrito à mão em React, Vue, Svelte, Solid ou Preact.

## Adicione-os a um projeto existente

```bash
nx skills
```

Execute-o na raiz do projeto. Ele lê `nexyconfig.py` e `package.json` para encontrar a pilha, copia as habilidades correspondentes e escreve `AGENTS.md` e `CLAUDE.md` quando elas estão faltando.

Ele nunca substitui um arquivo que você escreveu: um `AGENTS.md` ou `CLAUDE.md` existente é mantido e o comando informa isso. Adicione a lista de habilidades ao seu próprio arquivo manualmente, se desejar. Uma habilidade sua em `.claude/skills/` ou `.agents/skills/` é deixada de lado; apenas as habilidades `nexy-*` são atualizadas.

Execute `nx skills` novamente após atualizar o Nexy para atualizar as cópias e confirme o resultado para que toda a equipe o compartilhe.

## Como um agente os encontra

- `AGENTS.md` (ou `CLAUDE.md`, que o importa) é lido no início de cada sessão. Ele nomeia as habilidades.
- Cada habilidade começa com um nome e uma descrição que diz o que abrange e quando carregá-la. O agente os lê primeiro e abre uma habilidade somente quando a tarefa corresponde.

As habilidades seguem o [formato de habilidades do agente](https://agentskills.io/specification) aberto, para que outros agentes que leiam as pastas `SKILL.md` também possam usá-las.

## O que eles não fazem

As habilidades dizem ao agente como trabalhar; eles não tornam sua saída correta. Mantenha suas próprias verificações:

- Leia o que o agente mudou.
- Execute `nx check`, `nx test` e `nx build`. As competências exigem isso e que os resultados sejam relatados, e não resumidos.
- Dependências de auditoria que o agente adiciona (`nexy-security` explica como).

Os exemplos nas habilidades são verificados pelos próprios testes do Nexy: as importações existem, os campos de configuração existem, os comandos existem, as análises Python. Isso detecta desvios, não erros de julgamento.

## Mapa

Um agente responde mais rápido quando sabe qual página contém a resposta.

| Você precisa de | Leia |
|---|---|
| o produto, em uma página | [README](../README.md) |
| para executar um projeto | [primeiros passos](../getting-started/quick-start.md) |
| URL de um arquivo | [roteamento](../routing/README.md) |
| segmentos dinâmicos, layouts, páginas de erro | [páginas](../routing/fbr/pages/README.md) |
| o caminho atual, consulta, cookies, sessão | [hooks](../routing/fbr/navigation/hooks.md) |
| para editar uma página | [arquivos .nexy](../views/nexy/README.md) ou [visualizações](../views/README.md) |
| Markdown ou MDX | [redução](../views/nexy/markdown.md) |
| ajudantes HTML integrados | [componentes](../views/nexy/components.md) |
| modo de renderização | [SSR](../rendering/ssr.md), [CSR](../rendering/csr.md), [ISR](../rendering/isr.md) |
| um WebSocket | [websocket](../routing/fbr/realtime/websocket.md) |
| controladores e módulos | [modular](../routing/modular/README.md) |
| para adicionar um endpoint | [API](../routing/fbr/handlers/README.md) |
| um formulário postado em uma página | [ações](actions.md) |
| por que uma solicitação falhou e qual página a responde | [exceções](../reference/exceptions.md) |
| traduções | [i18n](i18n.md) |
| um campo de configuração | [configuração](../reference/config.md) |
| para testar o aplicativo | [testando](testing.md) |
| a compilação do cliente | [frontend](frontend.md) |

## Invariantes do projeto

1. `__nexy__/` é gerado. Nunca edite, nunca confirme. Exclua-o para forçar uma compilação limpa.
2. Um arquivo por URL. `index.nexy` e `index.py` para o mesmo caminho é um bug, não uma regra de prioridade.
3. Nomes reservados dentro de `src/routes/`: `layout.nexy`, `loading.nexy`, `errors.nexy`, `notfound.nexy`, `dependencies.py`, `__init__.py`. Não os use para conteúdo.
4. `.nexy` frontmatter é Python executado por solicitação. Sem efeitos colaterais no nível do módulo: sem identificadores de arquivo, sem conexões de banco de dados, sem chamadas de rede na importação.
5. `.py` em `src/routes/` é um manipulador de API. Métodos são nomes de funções (`GET`, `POST`, ...).
6. A configuração reside em `nexyconfig.py`, não em variáveis ​​de ambiente e não em constantes dispersas.
7. O escape automático está desativado em modelos `.nexy`: escape de valores não confiáveis ​​com `| e`.

```bash
nx dev      # development
nx build    # production build
nx start    # production server
nx test     # pytest, --client adds vitest
```

Quando os documentos e o código discordam, confie no código e diga o seguinte: `nexy/core/config.py` contém todas as opções, `nexy/modules/routers/fbrouter/` as regras de roteamento, `nexy/modules/compiler/` como `.nexy` arquivos se tornam módulos.

## Próximas etapas

- [CLI](../reference/cli.md): `nx new` e `nx skills`
- [Convenções de arquivo](../reference/file-conventions.md): nomes reservados e regras de roteamento
- [Glossário](../reference/glossary.md): as palavras nas quais essas regras se baseiam
- [Segurança](../reference/security.md): a versão atinge os pontos da habilidade de segurança
