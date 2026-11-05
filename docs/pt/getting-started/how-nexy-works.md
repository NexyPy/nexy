# Como funciona o Nexy

O que acontece entre um arquivo que você escreve e a página no navegador: as camadas que uma solicitação atravessa, quem constrói o quê e o que Nexy deixa para seu aplicativo. Você não precisa desta página para começar; ele responde às perguntas "por que funciona assim" mais tarde.

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
| Roteador | combinar a URL com um arquivo, com seus layouts, dependências e páginas de erro | produzir conteúdo |
| Renderizador | execute a página e transforme seu resultado em HTML ou JSON | buscar seus dados |
| Cliente | Vite e sua estrutura: pacotes, hidratação, navegação do cliente | responder a uma solicitação do servidor |

## Quem constrói o quê

| Ator | Possui | Não possui |
|---|---|---|
| Nexy | roteamento, renderização de servidor, ações, `.nexy` compilação, uma origem | componentes, reatividade, dados |
| Vite | pacotes de clientes, o servidor de desenvolvimento, recarga a quente | roteamento, renderização de servidor, ações |
| Sua estrutura | componentes, reatividade, o ecossistema | roteamento, o documento (Nexy pede seu layout) |
| Seu aplicativo | dados, autenticação, autorização, regras de negócios | transporte, renderização |

A regra por trás da mesa: **Nexy constrói o que possui e nunca compila o que Vite compila.**

## O sistema de roteamento

Um caminho em `src/routes/` torna-se um URL por quatro regras:

| Arquivo | URL |
|---|---|
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/hello` |
| `blog/[...parts].nexy` | `/blog/a/b` |
| `(marketing)/about.nexy` | `/about` |

A extensão nunca aparece; `index` é a rota de sua pasta; uma pasta entre parênteses agrupa arquivos sem adicionar um segmento.

Quando duas coisas podem responder a mesma URL, **a primeira registrada vence**, e Nexy sempre se registra nesta ordem:

1. o ponto final de Ações;
2. arquivos estáticos: `/public`, `/assets`, `/favicon.ico`;
3. um modular `APIRouter` (`useRouter`);
4. rotas de arquivo, as mais específicas primeiro: caminhos estáticos, depois caminhos dinâmicos com os segmentos mais fixos e, em seguida, caminhos genéricos.

Duas rotas de arquivos de igual especificidade são registradas em ordem alfabética de caminhos, então `[id].nexy` responde antes de `[slug].nexy`. Uma rota modular, portanto, supera uma página com o mesmo caminho. Esta é uma ordem de precedência na qual você pode confiar, não uma regra de desempate para brincar: dê a um URL um arquivo.

## O sistema de visualização

A extensão de um arquivo decide o que é, e a configuração do projeto decide quais extensões estão ativas.

| Extensão | Ativo quando | Compilado por | Servido como |
|---|---|---|---|
| `.nexy` | modo servidor | Nexy: frontmatter se torna Python, a marcação se torna Jinja2 | uma página |
| `.md` | sempre | Nexy: com sabor de GitHub Markdown, IDs de cabeçalho, índice | uma página, dentro do layout mais próximo |
| `.mdx` | sempre | Vite, com React ou Preact | uma rota componente |
| `.tsx` | `useFF` é React, Solid ou Preact | Vite e a estrutura | uma rota componente |
| `.vue` | `useFF` é Vue | Vite e Vue | uma rota componente |
| `.svelte` | `useFF` é Svelte | Vite e Svelte | uma rota componente |
| `.py` | sempre | Python | um manipulador de API: `GET`, `POST`, ... são os métodos |

Um arquivo cuja extensão não está ativa é ignorado com um aviso e não é veiculado. No modo cliente, `.nexy` é rejeitado antes do servidor iniciar. Consulte [Convenções de arquivo](../reference/file-conventions.md).

## O ciclo de vida da renderização

Três perguntas decidem tudo o que o leitor percebe:

| Pergunta | Resposta | Página |
|---|---|---|
| Quem produz o HTML? | o servidor ou o navegador para uma rota do cliente | [Renderização](../rendering/README.md) |
| Quando os dados são lidos? | em cada solicitação, em cada regeneração ou no navegador | [SSR](../rendering/ssr.md), [ISR](../rendering/isr.md) |
| Quando chega JavaScript? | apenas para uma ilha ou para todo o documento | [Ilhas](../rendering/islands.md), [CSR](../rendering/csr.md) |

No modo servidor, o servidor renderiza cada página, `revalidate` armazena em cache uma página por URL e as ilhas adicionam JavaScript a um componente. No modo cliente, o primeiro documento é renderizado no Node e a navegação acontece no navegador.

`__nexy__/` contém tudo o que é gerado: páginas compiladas, a entrada do cliente, a saída da compilação. Nunca edite, nunca comprometa; exclua-o para forçar uma compilação limpa.

## A integração front-end

**Vite não substitui Nexy.** Vite agrupa e fornece código do cliente. Ele não roteia uma solicitação, renderiza uma página `.nexy`, executa uma ação ou possui a origem. O navegador se comunica com uma origem - Nexy's - e em desenvolvimento Nexy proxies Vite endpoints de através dele, então não há CORS para configurar.

**Nexy não substitui React.** Nexy decide qual componente será renderizado, quando e com quais adereços; a estrutura possui o modelo de componentes, a reatividade e o ecossistema. Uma página `.nexy` importa um componente como uma ilha; no modo cliente, uma rota *é* um componente.

Para uma rota de componente, Python escreve apenas um módulo wrapper fino que aponta para o arquivo. A compilação e a renderização do lado do servidor são trabalho de Vite.

## Desenvolvimento e produção

`nx dev` verifica `nexyconfig.py`, compila as páginas, inicia Vite quando o projeto tem um framework frontend e reinicia o servidor quando você salva. `nx build` faz o mesmo trabalho uma vez, com antecedência, e `nx start` entrega o resultado.

| | `nx dev` | `nx build` então `nx start` |
|---|---|---|
| Páginas | compilado quando você salva | compilado uma vez, antes do tempo |
| Código do cliente | Vite servidor dev com hot reload, atrás da própria origem do Nexy | agrupar em `__nexy__/client/`, HTML pré-renderizado |
| Node.js | corre ao lado de Python | não é necessário servir |
| Erros | sobreposição no navegador, barra de ferramentas em todas as páginas | páginas de status sem detalhes |
| Origem | uma porta, `3000` | uma porta |

O que não muda: as mesmas regras de roteamento, os mesmos arquivos de páginas, os mesmos `nexyconfig.py`. Uma página que se comporta de maneira diferente entre as duas é um bug, não um modo.

## O que Nexy deixa para você

Nexy para na borda do seu aplicativo, de propósito:

| Preocupação | O que Nexy oferece | O que você escreve |
|---|---|---|
| Autenticação | middleware de sessão, `AuthenticationMiddleware` quando habilitado | o login, a pesquisa do usuário, a política de cookies |
| Autorização | `dependencies.py`, guardas, herança por pasta | a regra em si |
| Banco de dados | nenhum ORM próprio; `nx new` pode estruturar SQLModel, SQLAlchemy ou Tortoise, `nx migrate` executa Alembic ou Aerich | os modelos e as consultas ([Bancos de dados](../guides/databases.md)) |
| Internacionalização | nada para suas páginas; apenas a CLI é traduzida | a biblioteca e as mensagens ([i18n](../guides/i18n.md)) |
| Trabalhos em segundo plano | nada: sem fila, sem agendador | um processo de trabalho |
| E-mail, pagamentos, pesquisa | nada | o serviço que você escolher |

O motivo é o mesmo para todos os seis: uma estrutura que escolhe seu ORM ou sua biblioteca de autenticação decide coisas que somente seu aplicativo pode decidir. O custo é explícito: nada está conectado para você e os guias vinculados na tabela dizem onde conectar cada um.

## Próximas etapas

- [Estrutura do projeto](project-structure.md): onde cada parte reside em um projeto
- [Roteamento](../routing/README.md): os roteadores baseados em arquivo, modulares e personalizados
- [Renderização](../rendering/README.md): SSR, ISR, CSR e ilhas
- [Frontend](../guides/frontend.md): Vite, estilo e construção do cliente
