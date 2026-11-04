# Conceitos básicos

O modelo mental, antes da API: quatro níveis de leitura, depois as noções que voltam a cada
página. Cada noção recebe uma linha aqui e um link para a página que se aprofunda.

## Como ler estes documentos

| Nível | A pergunta que ele responde | Comece com |
|---|---|---|
| Arquitetura da aplicação | qual camada responde a uma solicitação e o que ela se recusa a fazer | [Arquitetura](../architecture.md) |
| Estrutura do aplicativo | onde fica o código e o que um arquivo se torna | [Estrutura do projeto](project-structure.md) |
| Apresentação e renderização | o que o leitor vê e quem produz o HTML | [Visualizações](../views/README.md), [Renderização](../rendering/README.md) |
| Interação do aplicativo | o que o leitor faz e o que é executado em resposta | [Ações](../guides/actions.md) |

Os níveis são lidos nessa ordem uma vez. Depois disso, a página que você precisa é uma pesquisa, não um curso.

## Arquitetura do aplicativo

Três maneiras de decidir qual código responde a uma URL. São alternativas, não camadas:

- **Roteamento baseado em arquivo (FBR)**: um arquivo em `src/routes/` é uma rota. O padrão.
- **Roteador modular**: controladores e módulos em `src/apps/`, declarados com decoradores, para um
  Base de código estilo NestJS.
- **Roteador personalizado**: um FastAPI existente `APIRouter` incluído no aplicativo.

Escolher um dos três é uma decisão. A escolha de uma estrutura de front-end é outra, separada:
consulte [Escolha um roteador](../routing/README.md) e [Visualizações](../views/README.md).

## Estrutura do aplicativo

Cinco noções que um leitor vindo do Next.js costuma mesclar em uma só. Eles não são a mesma coisa,
e a diferença explica a maioria das perguntas "por que minha página não está sendo renderizada".

| Noção | O que é | O que não é |
|---|---|---|
| **Rota** | um padrão de URL, produzido pelo caminho de um arquivo | um arquivo: um arquivo pode responder a vários URLs (`[slug]`) |
| **Page** | um arquivo de rota que renderiza uma visualização: `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | um endpoint: ele responde a um documento, não a dados |
| **Visualizar** | o que produz o corpo de uma página: Jinja2 e Python, Markdown ou um componente cliente | uma rota: a mesma visualização pode servir diversas páginas |
| **Componente** | uma peça reutilizável uma página importa | uma rota: no modo servidor um componente nunca é servido por conta própria |
| **Route handler** | a função de um arquivo de rota `.py`, nomeado após o método HTTP (`GET`, `POST`, …) | uma página: retorna JSON, um arquivo ou um `Response` |
| **Endpoint** | o par (URL, método) que um manipulador responde | um manipulador: um arquivo pode responder a vários terminais |

Em uma frase: **uma página é um arquivo de rota, uma visualização é o que a renderiza, um componente é o que uma página
reutiliza, um manipulador responde a um endpoint.**

Mais duas palavras que voltam em todos os lugares:

- **Layout**: um arquivo `layout.*` que agrupa as páginas abaixo de sua pasta; o root possui o HTML
  documento. Consulte [Layouts](../routing/fbr/layouts/README.md).
- **Dependência**: uma função que é executada antes de um manipulador, aplicada por rota ou por pasta. Veja
  [Dependências](../routing/fbr/dependencies/README.md).

## Apresentação e renderização

Duas decisões independentes, muitas vezes confusas:

- **O formato** decide qual arquivo renderiza a página: [Visualizações](../views/README.md).
- **O modo** decide quem produz o HTML e quando: [Renderização](../rendering/README.md).

| Noção | Uma linha |
|---|---|
| Modo servidor | o servidor renderiza páginas `.nexy` e `.md`; componentes são ilhas ([modos](../routing/fbr/modes.md)) |
| Modo cliente | `useCSR = True`: os arquivos do framework são as rotas, e a navegação acontece no navegador |
| SSR, ISR, CSR, ilhas | quatro modos de renderização, decididos por página, exceto CSR, que é por projeto ([renderização](../rendering/README.md)) |
| Hidratação | o navegador anexando uma estrutura ao HTML o servidor já enviou ([ilhas](../rendering/islands.md)) |
| Props | os valores que um pai passa para um componente, declarado `name: prop[type]` em um arquivo `.nexy` ([arquivos .nexy](../views/nexy/README.md)) |

## Interação do aplicativo

| Noção | Uma linha |
|---|---|
| Ação | uma função Python marcada como `@Action`, servida como `POST`, que pode ser chamada de um formulário ou como uma função digitada ([actions](../guides/actions.md)) |
| Formulário | um formulário HTML que posta em uma ação, com erros de validação voltando para a página ([actions](../guides/actions.md)) |
| Navegação | links que pré-buscam e ganchos que leem o caminho, a consulta, os cookies e a sessão ([hooks](../routing/fbr/navigation/hooks.md)) |
| Busca de dados | feita pela página ou pelo manipulador que precisa deles; Nexy não fornece nenhuma camada de dados do cliente ([handlers](../routing/fbr/handlers/README.md)) |

## O que Nexy não faz

Autenticação, autorização, base de dados, internacionalização, trabalhos em segundo plano, e-mail, pagamentos e
search são **responsabilidade da sua aplicação**, não do framework. Nexy dá a extensão
aponta e diz onde conectar cada um: veja [os limites](../architecture.md#boundaries).

A razão não é o minimalismo por si só: uma estrutura que escolhe seu ORM ou sua biblioteca de autenticação
decidiu algo que somente seu aplicativo pode decidir.

## Próximas etapas

- [Arquitetura](../architecture.md): as camadas e quem constrói o quê
- [Estrutura do projeto](project-structure.md): todas as pastas e arquivos de um projeto
- [Glossário](../reference/glossary.md): as mesmas palavras, em um índice alfabético
- [Como funciona o Nexy](how-nexy-works.md): uma solicitação, passo a passo