# Glossário

As palavras que esses documentos usam, uma linha cada, em ordem alfabética. Um termo que precisa de mais do que uma linha
tem uma página: siga o link. Para saber como as noções se encaixam, leia
[Conceitos básicos](../getting-started/core-concepts.md).

## Termos

| Termo | Em uma linha |
|---|---|
| Ação | uma função Python marcada como `@Action`, servida como `POST` e chamável pelo cliente ([actions](../guides/actions.md)) |
| ASGI | a interface falada pelo Uvicorn, implementada por FastAPI e Starlette |
| Modo cliente | `useCSR = True`: os arquivos do framework são as rotas e o navegador navega ([modos](../routing/fbr/modes.md)) |
| Componente | um bloco de construção de UI reutilizável usado para compor uma visualização ([views](../views/README.md)) |
| CSR | renderização do lado do cliente: o navegador renderiza páginas após o primeiro documento ([CSR](../rendering/csr.md)) |
| Dependência | uma função FastAPI é executada antes de um manipulador, por rota ou por pasta ([dependências](../routing/fbr/dependencies/README.md)) |
| Document shell | o `<html>`, `<head>` e `<body>` em torno de uma página, de propriedade do layout mais próximo ou de Nexy ([layouts](../routing/fbr/layouts/README.md)) |
| Endpoint | a combinação única de uma URL e um método HTTP ([views](../views/README.md)) |
| FBR | roteamento baseado em arquivo: um arquivo em `src/routes/` é uma rota ([routing](../routing/fbr/README.md)) |
| Frontmatter | o bloco Python entre as duas `---` linhas de um arquivo `.nexy` ou `.md` ([arquivos .nexy](../views/nexy/README.md)) |
| Guarde | uma dependência que recusa uma solicitação aumentando `HTTPException` ([guards](../routing/modular/guards-and-metadata.md)) |
| Handler | uma função Python que lida com uma solicitação HTTP para um método específico ([views](../views/README.md)) |
| HMR | substituição de módulo a quente: o servidor de desenvolvimento troca os módulos que foram alterados, sem uma recarga completa ([frontend](../guides/frontend.md)) |
| Hidratação | o navegador anexando uma estrutura ao HTML o servidor já enviou ([ilhas](../rendering/islands.md)) |
| Ilha | um componente cliente montado dentro de uma página renderizada pelo servidor ([ilhas](../rendering/islands.md)) |
| ISR | regeneração estática incremental: uma página em cache por caminho, atualizada em segundo plano ([ISR](../rendering/isr.md)) |
| Layout | um arquivo `layout.*` que agrupa as páginas abaixo de sua pasta ([layouts](../routing/fbr/layouts/README.md)) |
| Roteador modular | rotas declaradas com `@Module` e `@Controller` em `src/apps/` ([modular](../routing/modular/README.md)) |
| Página | um recurso endereçável por URL definido por um arquivo em `src/routes/` ([views](../views/README.md)) |
| Pré-busca | carregando a página atrás de um link antes que o leitor clique nele ([linking](../routing/fbr/navigation/linking-and-navigating.md)) |
| Props | os valores que um pai passa para um componente ([arquivos .nexy](../views/nexy/README.md)) |
| Revalidar | o número de segundos após os quais uma página ISR é reconstruída em segundo plano ([ISR](../rendering/isr.md)) |
| Rota | um padrão de URL, produzido pelo caminho de um arquivo de rota ([routing](../routing/README.md)) |
| Grupo de rotas | uma pasta entre parênteses que agrupa rotas sem adicionar um segmento ([rotas dinâmicas](../routing/fbr/pages/dynamic-routes.md)) |
| Manipulador de rota | a `GET`, `POST`,… função de um arquivo de rota `.py` ([handlers](../routing/fbr/handlers/README.md)) |
| Modo servidor | `useCSR = False`, o padrão: o servidor renderiza `.nexy` e `.md` páginas ([modos](../routing/fbr/modes.md)) |
| Habilidade | uma pasta com um `SKILL.md` que ensina a um agente de codificação uma parte do Nexy ([agentes de codificação](../guides/ai-agents.md)) |
| SSG | geração de sites estáticos; **não é um modo Nexy**: o HTML construído antecipadamente é sempre lido pelo servidor ([renderização](../rendering/README.md)) |
| SSR | renderização no lado do servidor: o servidor renderiza cada página para sua solicitação e é o padrão ([SSR](../rendering/ssr.md)) |
| Veja | o processo de produção do corpo de resposta para uma página ([visualizações](../views/README.md)) |

## Arquivos e pastas

| Nome | Em uma linha |
|---|---|
| `__nexy__/` | saída gerada: páginas compiladas, a entrada do cliente e o cliente de ação; nunca editado, nunca confirmado |
| `nexyconfig.py` | a configuração do projeto, uma classe de `use*` campos ([config](config.md)) |
| `public/` | arquivos servidos na raiz, como `public/logo.svg` → `/logo.svg` ([convenções de arquivo](file-conventions.md)) |
| `src/apps/` | controladores e módulos do roteador modular ([modular](../routing/modular/README.md)) |
| `src/components/` | componentes importados por páginas; nunca roteia ([convenções de arquivo](file-conventions.md)) |
| `src/routes/` | as rotas da aplicação ([convenções de arquivo](file-conventions.md)) |

## Próximas etapas

- [Conceitos básicos](../getting-started/core-concepts.md): o modelo ao qual essas palavras pertencem
- [Índice de documentação](../README.md): a página da tarefa em questão
- [Convenções de arquivo](file-conventions.md): os nomes reservados por trás dessas definições
- [Para agentes de IA](../guides/ai-agents.md): as mesmas invariantes, escritas para um agente