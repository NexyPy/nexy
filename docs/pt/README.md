# Documentação Nexy

**Uma Python estrutura para aplicações web fullstack.**

Nexy coloca suas páginas e sua API em um Python projeto, servido por um servidor. A versão 2.2 é construída em FastAPI: cada rota API é uma rota FastAPI, listada em um esquema OpenAPI que Scalar mostra em `/docs`.

- **Python primeiro.** Páginas, endpoints, formulários e ações são Python, e uma página não precisa de JavaScript.
- **Um frontend quando você quiser.** React, Vue, Svelte, Solid ou Preact, para um componente ou para todo o site.
- **Um arquivo, uma URL.** Um arquivo em `src/routes/` é uma rota: `.nexy` é uma página, `.py` é um endpoint de API.
- **Espaço para crescer.** Comece com um arquivo; mude para módulos ou conecte um roteador FastAPI existente, quando o projeto crescer.

Novo aqui? Leia [O que é Nexy?](getting-started/what-is-nexy.md), depois o [Início rápido](getting-started/quick-start.md).

## Primeiros passos

### Primeiros passos
| Página | O que você fará |
|---|---|
| [O que é Nexy?](getting-started/what-is-nexy.md) | Saiba o que é Nexy, em que se baseia e o que você ganha |
| [Instalação](getting-started/installation.md) | Instale uv e o Nexy CLI e crie seu primeiro projeto |
| [Início rápido](getting-started/quick-start.md) | Crie um projeto, execute-o com recarga ao vivo e construa-o para produção |
| [Tutorial](getting-started/tutorial.md) | Crie uma página de notas com um endpoint, dados compartilhados e uma construção de produção em 10 minutos |

### Entenda o modelo
| Página | O que você fará |
|---|---|
| [Conceitos básicos](getting-started/core-concepts.md) | Obtenha o modelo mental: rota, página, visualização, componente, manipulador, endpoint |
| [Estrutura do projeto](getting-started/project-structure.md) | Saiba para que serve cada pasta e arquivo de um projeto |
| [Escolha um roteador](routing/README.md) | Escolha o roteador baseado em arquivo, modular ou personalizado |
| [Escolha um formato de visualização](views/README.md) | Escolha `.nexy`, Markdown ou uma estrutura de cliente para uma página |

### Vindo de outro lugar
| Página | O que você fará |
|---|---|
| [Vindo de outra estrutura](getting-started/coming-from-other-frameworks.md) | Traduzir FastAPI, Next.js e expressar hábitos em Nexy |

## Roteamento

### Baseado em arquivo {fbr}
| Página | O que você fará |
|---|---|
| [Roteamento baseado em arquivo](routing/fbr/README.md) | Transforme um caminho de arquivo em um URL |
| [Páginas](routing/fbr/pages/README.md) | Escreva uma página |
| [Rotas dinâmicas](routing/fbr/pages/dynamic-routes.md) | Use `[slug]`, `[...path]` e grupos de rotas |
| [Metadados da página](routing/fbr/pages/metadata.md) | Defina o título, a descrição e a imagem de compartilhamento de uma página {new} |
| [Layouts](routing/fbr/layouts/README.md) | Compartilhe um quadro entre páginas |
| [Herança](routing/fbr/inheritance.md) | Leia a ordem de resolução de layouts, dependências e páginas de erro |
| [Modo servidor e modo cliente](routing/fbr/modes.md) | `useCSR`, e o que cada modo permite |
| [Vinculando e navegando](routing/fbr/navigation/linking-and-navigating.md) | Vincular páginas, navegar no cliente, pré-buscar |
| [Ganchos](routing/fbr/navigation/hooks.md) | Leia o caminho, consulta, cookies e sessão |

### Manipuladores e erros {fbr}
| Página | O que você fará |
|---|---|
| [Manipuladores de rota](routing/fbr/handlers/README.md) | Adicione um ponto de extremidade Python |
| [Validação e erros](routing/fbr/handlers/validation-and-errors.md) | Responda `422` e `404`, e levante um `HTTPException` |
| [WebSocket manipuladores](routing/fbr/realtime/websocket.md) | Lidar com uma conexão `SOCKET` |
| [Dependências e guardas](routing/fbr/dependencies/README.md) | Execute `dependencies.py` antes de um manipulador e herde-o |
| [Arquivos de middleware](routing/fbr/middleware/README.md) | Envolva solicitações com `middleware.py`, herdadas por diretório |
| [Páginas de erro](routing/fbr/errors/README.md) | Responda com erros `notfound.nexy`, `errors.nexy` e JSON |
| [Páginas de erro por pasta](routing/fbr/errors/folder-pages.md) | Caso extremo: erros de subpastas |

### Roteador modular {modular}
Controladores e módulos.
| Página | O que você fará |
|---|---|
| [Roteamento modular](routing/modular/README.md) | Monte controladores e módulos |
| [Injeção de dependência](routing/modular/dependency-injection.md) | Definir serviços, seus escopos e o contêiner |
| [Guardas e metadados](routing/modular/guards-and-metadata.md) | Proteja e documente rotas |
| [Roteador modular vs NestJS](routing/modular/vs-nestjs.md) | Comparação com NestJS |

### Integração de roteador personalizado {custom}
| Página | O que você fará |
|---|---|
| [Roteamento personalizado](routing/custom/README.md) | Incluir um aplicativo FastAPI existente |

## Interface

### Contratos compartilhados
| Página | O que define |
|---|---|
| [Páginas de front-end](views/frontend/pages.md) | Um arquivo, uma rota: adereços, renderização, metadados |
| [Layouts de front-end](views/frontend/layouts.md) | O shell do documento, o aninhamento e o que um layout não pode fazer |
| [Ações e navegação](views/frontend/actions-and-navigation.md) | Chame uma ação digitada, vincule páginas, leia o URL |

### Visualizações próximas
| Página | O que você fará |
|---|---|
| [Arquivos .nexy](views/nexy/README.md) | Escreva uma página com Python, Jinja2 e adereços |
| [Componentes](views/nexy/components.md) | Use `Image`, `Link`, `Audio`, `Video` e `Import` |
| [layout.nexy](views/nexy/layouts.md) | Escreva o layout do modo servidor |
| [Markdown e MDX](views/nexy/markdown.md) | Escreva páginas de conteúdo |

### Diferenças de estrutura
| Página | O que muda |
|---|---|
| [React diferenças](views/react/differences.md) | Componentes, ganchos e `layout.tsx` {new} |
| [Vue diferenças](views/vue/differences.md) | SFCs, referências e `layout.vue` {new} |
| [Svelte diferenças](views/svelte/differences.md) | Runas, lojas e `layout.svelte` {new} |
| [Solid diferenças](views/solid/differences.md) | Sinais, acessadores e `layout.tsx` {new} |
| [Preact diferenças](views/preact/differences.md) | Ganchos, sinais e `layout.tsx` {new} |

## Renderização

### Modos
| Página | O que você vai decidir |
|---|---|
| [Renderização](rendering/README.md) | Qual modo de renderização se ajusta a uma página |
| [RSS](rendering/ssr.md) | Renderização de servidor, o padrão |
| [ISR](rendering/isr.md) | Armazenar páginas em cache com obsoletos enquanto revalidam |
| [RSE](rendering/csr.md) | Roteamento do lado do cliente |
| [Ilhas](rendering/islands.md) | Hidrate-se em consultas ociosas, visíveis ou de mídia |

## Guias

### Formulários e dados
| Página | O que você fará |
|---|---|
| [Ações](guides/actions.md) | Chame uma função Python de um formulário ou de uma função TypeScript digitada |
| [Bancos de dados](guides/databases.md) | Escolha um ORM e execute migrações |

### Segurança e implantação
| Página | O que você fará |
|---|---|
| [Middleware e segurança](guides/middleware-and-security.md) | Configure CORS, GZip, hosts e sessões confiáveis |
| [Implantar](deployment/README.md) | Construa, conteinerize e sirva |
| [Desempenho](deployment/performance.md) | Meça e ajuste os padrões |

### Construir e testar
| Página | O que você fará |
|---|---|
| [Vite e estilo](guides/frontend.md) | Configure Vite, o estilo e a construção do cliente |
| [Teste](guides/testing.md) | Teste com pytest, `TestClient` e vitest |

### Ferramentas e ajuda
| Página | O que você fará |
|---|---|
| [Barra de ferramentas de desenvolvimento](guides/devtools.md) | Use a barra de ferramentas de `nexy dev` e desligue-a |
| [Agentes de codificação](guides/ai-agents.md) | Dê Claude Code, Codex e OpenCode as regras do seu projeto |
| [Solução de problemas](guides/troubleshooting.md) | Corrija os primeiros problemas que as pessoas enfrentam |

## Referência

### Comandos e configuração
| Página | O que lista |
|---|---|
| [CLI](reference/cli.md) | Comandos, sinalizadores, prompts e códigos de saída |
| [Configuração](reference/config.md) | Cada campo `nexyconfig.py` e seu padrão |

### Python API e erros
| Página | O que lista |
|---|---|
| [API Python](reference/python-api.md) | Cada nome que Nexy exporta, por módulo |
| [Exceções e erros](reference/exceptions.md) | Cada falha, seu status e o arquivo que a responde |

### Convenções e conceitos
| Página | O que você fará |
|---|---|
| [Convenções de arquivo](reference/file-conventions.md) | Arquivos reservados e regras de roteamento |
| [Glossário](reference/glossary.md) | As palavras que esses documentos usam |
| [Segurança](reference/security.md) | Pisos de versão, regras que Nexy segue, auditorias |

## Disposição
```text
docs/
├─ README.md
├─ getting-started/     what is Nexy, installation, quick start, tutorial, core concepts,
│                       project structure, how Nexy works, migration
├─ routing/             FBR Router, Modular Router, Custom Router
│  ├─ fbr/              file-based routing
│  │  ├─ modes.md       server mode and client mode
│  │  ├─ inheritance.md layouts, dependencies, error pages
│  │  ├─ pages/         pages, dynamic routes, route groups, metadata
│  │  ├─ layouts/       layout resolution, layout.tsx, layout.vue, layout.svelte
│  │  ├─ handlers/      .py route handlers, validation and errors
│  │  ├─ dependencies/  dependencies.py, guards
│  │  ├─ middleware/    middleware.py
│  │  ├─ errors/        not-found and error pages
│  │  ├─ navigation/    links, hooks
│  │  └─ realtime/    WebSocket
│  ├─ modular/          controllers, injection, guards, NestJS comparison
│  └─ custom/           include an existing FastAPI router
├─ rendering/           SSR, ISR, CSR, islands
├─ views/               choose a format, one page per client framework
│  ├─ frontend/         the four contracts every framework shares
│  └─ nexy/             .nexy files, components, layouts, Markdown and MDX
├─ guides/              actions, i18n, databases, middleware, frontend, testing
├─ deployment/          deploy, performance
└─ reference/           CLI, config, Python API, exceptions, file conventions, glossary,
                        security, agents
```

## Avançado

### Avançado {advanced}

| Página | O que você fará |
|---|---|
| [Como funciona o Nexy](getting-started/how-nexy-works.md) | Veja o que acontece entre um arquivo e uma página e o que o Nexy deixa para você |
| [Atualizando para 2.2](getting-started/upgrading.md) | Migrar de 2.1 para 2.2 |
| [Internacionalização (i18n)](guides/i18n.md) | Adicione traduções com sua escolha de biblioteca |
| [Receitas](guides/recipes.md) | Exemplos e padrões, não um tutorial |

*Essas páginas não fazem parte do caminho de leitura padrão. Um link "Toda a documentação" permite que você veja tudo.*
