# CLI

O binário é `nx` (também instalado como `nexy`). `uvx nexy new` cria um projeto (`uvx` vem com uv). Execute todos os outros comandos dentro do ambiente virtual do projeto, ou através de `uv run`, por exemplo `uv run nexy dev`: é onde estão seus próprios pacotes.

## Comandos

| Comando | Alias | O que isso faz |
|---|---|---|
| `nx dev` | `nx d` | servidor de desenvolvimento: compilação na mudança, Vite, HMR |
| `nx start` | `nx s` | servidor de produção na saída compilada |
| `nx build` | `nx b` | construção de produção |
| `nx new` | `nx n` | estruturar um projeto |
| `nx init` | `nx i` | adicione Nexy a um projeto existente |
| `nx add` | - | adicione um componente de UI do registro ou uma URL para `src/components/ui` |
| `nx migrate` | `nx m` | crie ou aplique migrações de banco de dados com Alembic ou Aerich |
| `nx check` | `nx c` | verificação de tipo: mypy em Python, `tsc` em TypeScript |
| `nx format` | `nx f` | formato Python (ruff), JS/TS (mais bonito), `.nexy` arquivos |
| `nx test` | - | execute pytest; `--client` adiciona vitest |
| `nx skills` | - | adicione ou atualize as habilidades `AGENTS.md` e `CLAUDE.md` para agentes de codificação |

## Bandeiras

| Comando | Bandeira | Padrão |
|---|---|---|
| `dev`, `start` | `--port` | `usePort`, `3000` |
| `dev`, `start` | `--host` | `useHost`, `0.0.0.0` |
| `dev` | `--open`, `-o` | off - abra o navegador no endereço local assim que o servidor responder |
| `build` | `--check` | off - executa ruff e mypy após a compilação |
| `format` | `--check` | off - relatar em vez de reescrever |
| `test` | `--client` | off - execute também o vitest em vez de pytest sozinho |
| `test` | `--no-server` | on - pule pytest quando quiser apenas testes de cliente |
| `new` | `--template`, `-t` | nenhum - clona um modelo registrado sem avisos |
| `new` | `--no-agents` | agentes ativados - pule `AGENTS.md` e as habilidades do agente |
| `add` | `--ui`, `--url` | off - força um nome de registro ou URL quando é ambíguo |
| `add` | `--all`, `-a` | off - adicione todos os componentes do registro |
| `add` | `--sha256` | nenhum – resumo esperado de um componente remoto; uma incompatibilidade aborta |
| `migrate` | `--init` | off - escreva a configuração Alembic ou Aerich |
| `migrate` | `--upgrade`, `-u` | off - aplique as migrações em vez de escrever uma nova |
| `migrate` | `--message`, `-m` | vazio - nome da nova revisão |

## Saída

Etapas longas (instalação de pacotes, compilação, empacotamento) mostram um botão giratório com o tempo decorrido e a última linha que o comando imprimiu, depois deixa uma linha para trás, como uv faz: `Synced .venv with uv in 1.4s`. Um grupo de etapas (as instalações de `nx new`) também mostra uma barra de progresso e o número de etapas concluídas, `2/5`. Uma etapa com falha é uma linha `error:` com sua causa, `cause: exit 1 after 2.1s`, seguida pelas últimas linhas da saída do comando em vez de ocultá-la. Algo para olhar diz `warning: ...` e o que fazer a seguir `hint: ...`. Os logs de desenvolvimento são lidos `GET » /about 200 in 12ms` para solicitações e `vite » ...` para Vite.

## Erros durante a execução de `nx dev`

Salvar um arquivo quebrado nunca para o servidor. Um arquivo `.py` com erro de sintaxe é relatado com seu arquivo e linha, e o servidor continua servindo a última versão funcional até que você o corrija:

```text
  nexy » error  src/routes/users.py:3
  SyntaxError: invalid syntax

    1 | import json
    2 |
  > 3 | def GET(:
                ^
    4 |     x = 1
    5 |     return {"v": 2}

  Fix it and save: the server keeps its last working version.
```

Um arquivo que analisa, mas falha quando o aplicativo é carregado (uma importação ausente, um erro no nível do módulo) é relatado da mesma maneira e `nx dev` aguarda seu próximo salvamento; nada é servido até que o aplicativo seja carregado novamente. Um salvamento válido lê `nexy » update <file>` enquanto o servidor é recarregado. Markdown arquivos fora de `src/routes`, como `README.md`, não são páginas e não acionam nada. `nx start` é mais rigoroso: sai com o código 1 e não inicia nada, se um arquivo de rota não puder ser carregado ou se `nx build` ainda não tiver compilado o projeto.

## Perguntas de `nx new`

`nx new` pergunta, nesta ordem: roteador baseado em arquivo, tipo de projeto (web ou API), roteamento do lado do cliente, estrutura do cliente, como estilizar o aplicativo, alias de importação, ORM, banco de dados e URL do banco de dados. Cada opção possui uma breve descrição e a atual é destacada. As perguntas que não se aplicam são ignoradas (um projeto de API não tem estrutura ou estilo; escolha **Sem banco de dados** pois o ORM ignora o banco de dados e a URL). Mova-se com as setas (ou `j`/`k`, ou um número), confirme com `enter`, volte à pergunta anterior com `←` ou `esc`, saia com `ctrl+c`.

| Pergunta | Escolhas |
|---|---|
| Alias de importação | `@` (`@/components/...` aponta para `src/`) ou outro prefixo como `~` ou `#app` |
| Estilo | Tailwind CSS, UnoCSS, Vanilla CSS, Outro (sem ferramenta CSS, mesma folha de estilo simples do Vanilla) |
| ORM | SQLModel, SQLAlchemy, Tortoise-ORM, sem banco de dados |
| Banco de dados (com um ORM) | SQLite, PostgreSQL, Neon, MySQL / MariaDB, Outro (você digita a URL) |

O driver de banco de dados para o ORM escolhido é instalado com ele (`psycopg`, `pymysql`, `asyncpg` ou `aiomysql`), e a URL é gravada em `.env`.

Antes de instalar os pacotes, `nx new` verifica a conexão. Sem ele, ele ignora as instalações e solicita que você execute `uv sync` e a instalação do seu gerenciador de pacotes mais tarde. Com um, ele imprime a latência e velocidade de download, e avisa quando a conexão está lenta (acima de 400 ms, ou abaixo de 100 KB/s). Cada linha de instalação nomeia a ferramenta e a pasta que ela preenche, por exemplo `pnpm install node_modules` ou `uv sync .venv`.

## O que `dev`, `build` e `start` criam

Antes de serem executados, os três comandos criam um `__init__.py` vazio em `src/` e em cada pasta abaixo dele que contém um arquivo `.py` ou `.nexy`, então uma rota como `src/routes/users.py` importa da mesma maneira em todos eles. Os arquivos existentes nunca são tocados e `nx dev` faz o mesmo novamente quando você adiciona uma pasta. O bytecode Python vai para `__nexy__/__pycache__`, então nenhuma pasta `__pycache__` aparece ao lado de suas fontes.

## Idioma

A linha de comando fala inglês, chinês, hindi, espanhol, português, francês, alemão, japonês, russo, coreano, indonésio e árabe. Ele usa o primeiro deles que suporta:

1. a variável de ambiente `NEXY_LANG` (`NEXY_LANG=ja nx dev`);
2. as variáveis ​​de localidade do seu shell (`LC_ALL`, `LC_MESSAGES`, `LANG`, então `LANGUAGE`);
3. o idioma do seu sistema operacional.

Qualquer outra coisa é inglês, assim como qualquer mensagem que um idioma ainda não tenha. Somente o que `nx` imprime é traduzido: erros do compilador, tracebacks e a saída das ferramentas que ele executa permanecem como estão. As traduções ainda não foram revisadas por falantes nativos: correções são bem-vindas como pull requests para `nexy/modules/i18n/<language>.json`.

## Comportamento de construção

`nx build` compila as rotas e agrupa o cliente quando `useVite` está ativado.

> [!NOTE]
> não há sinalizador `--static`. A hospedagem estática é uma opção de implantação, não um modo de construção - consulte [Implantação](../deployment/README.md).

## Trabalhando no próprio Nexy

Dentro deste repositório os portões são:

```bash
python scripts/verify.py             # lint, format, typecheck, tests
python scripts/audit_dependencies.py # supply-chain audit against the lock
```

## Próximas etapas

- [Primeiros passos](../getting-started/quick-start.md): primeiro projeto
- [Testando](../guides/testing.md): o que `nx test` é executado
- [Implantar](../deployment/README.md): `build` e `start` em produção
