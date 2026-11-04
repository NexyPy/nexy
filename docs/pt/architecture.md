# Arquitetura

## Definição

Nexy tem cinco camadas, e cada uma tem uma função que as outras não fazem. Conhecer o limite responde mais
Perguntas do tipo "por que funciona assim": uma página lenta é uma questão de renderizador, uma página errada é um roteador
pergunta, uma página que nunca aparece é uma pergunta do cliente.

Esta página é para pessoas que escrevem um aplicativo. Os pacotes do próprio Nexy e os mecanismos
atrás deles, estão descritos em `ARCHITECTURE.md` na raiz do repositório, para contribuidores.

## As camadas

```diagram filename="Um pedido, cinco camadas"
Browser
   │
   ▼
Uvicorn ───── ASGI transport
   │
   ▼
Middleware ── sessions, CORS, gzip, trusted hosts, your own
   │
   ▼
Router ────── FBR | Modular | Custom ── picks the file that answers
   │
   ▼
Renderer ──── HTML (Jinja2, Markdown, Node) or JSON
   │
   ▼
Response
```

| Camada | Responsabilidade | Não |
|---|---|---|
| Uvicorn | aceite a conexão, fale ASGI | saiba o que é uma página |
| Middleware | decore a solicitação: sessão, CORS, gzip, hosts confiáveis, redirecionamento HTTPS, seu | escolha uma rota |
| Roteador | corresponde a URL de um arquivo, com seus layouts, dependências e páginas de erro | produz conteúdo |
| Renderizador | executa a página e transforma seu resultado em HTML ou JSON | busca seus dados |
| Cliente | Vite e sua estrutura: pacotes, hidratação, navegação do cliente | responder a uma solicitação do servidor |

## Quem constrói o quê

| Ator | Possui | Não possui |
|---|---|---|
| Nexy | roteamento, renderização de servidor, ações, `.nexy` compilação, uma origem | componentes, reatividade, dados |
| Vite | pacotes de clientes, o servidor de desenvolvimento, hot reload | roteamento, renderização do servidor, ações |
| Sua estrutura | componentes, reatividade, o ecossistema | roteamento, o documento (Nexy pede seu layout) |
| Sua aplicação | dados, autenticação, autorização, regras de negócios | transporte, renderização |

A regra por trás da mesa: **Nexy constrói o que possui e nunca compila o que Vite compila.** Para
uma rota de componente, o Python escreve um módulo wrapper fino que aponta para o arquivo.

## Quando uma solicitação é decidida

1. O middleware é executado e pode alterar a solicitação ou interrompê-la.
2. O roteador escolhe um arquivo e os layouts em torno dele.
3. O renderizador executa esse arquivo com os dados que ele mesmo lê.
4. A resposta volta e a camada do cliente assume o controle se a página tiver JavaScript.

Cada etapa, com a precedência exata entre os roteadores e a ordem de `nx dev`, está em
[Como funciona o Nexy](getting-started/how-nexy-works.md). Esta página não a repete.

## Desenvolvimento e produção

As mesmas cinco camadas, montadas duas vezes:

| Camada | `nx dev` | `nx build` então `nx start` |
|---|---|---|
| Compilador | é executado quando você salva | é executado uma vez, antes do tempo |
| Vite | servidor de desenvolvimento, hot reload, proxy através do pacote de origem do Nexy | gravado em `__nexy__/client/`, sem servidor de desenvolvimento |
| O nó | renderiza documentos do cliente sob demanda | os renderiza na construção, não durante a veiculação |
| Observador | reinicia o uvicorn na mudança | ausente |
| Origem | uma porta | uma porta |

O que muda é *quando* o trabalho acontece, não *quem* o faz. Uma página que se comporta de maneira diferente entre os
dois é um bug na página, não uma propriedade do modo.

## Limites

Nexy para na borda do seu aplicativo, de propósito:

| Preocupação | O que Nexy fornece | O que você escreve |
|---|---|---|
| Autenticação | middleware de sessão, `AuthenticationMiddleware` quando habilitado | o login, a pesquisa do usuário, a política de cookies |
| Autorização | `dependencies.py`, guardas, herança por pasta | a própria regra |
| Banco de dados | nada: sem ORM, sem migrações | a camada do modelo ([Bancos de dados](guides/databases.md)) |
| Internacionalização | nada para suas páginas; apenas a CLI é traduzida | a biblioteca e as mensagens ([i18n](guides/i18n.md)) |
| Trabalhos em segundo plano | nada: sem fila, sem agendador | um processo de trabalho |
| E-mail, pagamentos, pesquisa | nada | o serviço que você escolher |

O motivo é o mesmo para todos os seis: uma estrutura que escolhe seu ORM ou sua biblioteca de autenticação decide
coisas que somente seu aplicativo pode decidir. O custo é explícito: nada está programado para você e o
as páginas de guia acima dizem onde conectar cada um.

## Próximas etapas

- [Como funciona o Nexy](getting-started/how-nexy-works.md): uma solicitação, passo a passo
- [Estrutura do projeto](getting-started/project-structure.md): onde cada camada reside em um projeto
- [Routing](routing/README.md): os três roteadores e como escolher
- [Renderização](rendering/README.md): de onde vem o HTML