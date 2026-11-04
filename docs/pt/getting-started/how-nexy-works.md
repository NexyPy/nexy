# Como funciona o Nexy

O modelo mental em uma página: o que Nexy constrói, o que Vite constrói e o que acontece entre um arquivo
e uma página no seu navegador. Leia uma vez; o resto da documentação é então um conjunto de detalhes.

## A arquitetura Nexy

Uma solicitação atravessa cinco camadas: o Uvicorn a aceita, o middleware a decora, o roteador escolhe um arquivo,
o renderizador transforma esse arquivo em HTML ou JSON, e a camada do cliente assume o controle se a página tiver
JavaScript. Nexy possui os três do meio; Vite e sua estrutura são donos do cliente; seu aplicativo
detém os dados, a autenticação e a autorização.

Cada camada, e o que ela se recusa a fazer, está em [Arquitetura](../architecture.md). Para os pacotes de
O próprio Nexy, veja `ARCHITECTURE.md` na raiz do repositório - ele foi escrito para contribuidores.

## O ciclo de vida do aplicativo

`nx dev` faz seis coisas antes da primeira solicitação:

1. valida `nexyconfig.py` e para em uma configuração inválida;
2. garante que os pacotes Python do projeto sejam importáveis;
3. resolve as portas e exclui o marcador obsoleto `__nexy__/nexy.prod`;
4. gera os arquivos do cliente e compila as rotas, em paralelo;
5. inicia o Vite e espera até que ele responda;
6. instala o inspetor de arquivos e permite a importação do uvicorn `nexy.modules.routers.app:_server`.

Essa importação reúne o aplicativo - middleware, ações, roteadores, manipuladores de erros - e o
a primeira solicitação é atendida por esse assembly. Quando você salva, o observador reinicia o uvicorn; uma página que
apareceu, desapareceu ou foi movido também regenera a lista de rotas do cliente.

## O sistema de roteamento

Um caminho em `src/routes/` torna-se um URL por quatro regras:

| Arquivo | URL |
|---|---|
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/hello` |
| `blog/[...parts].nexy` | `/blog/a/b` |
| `(marketing)/about.nexy` | `/about` |

A extensão nunca aparece; `index` é a rota de sua pasta; uma pasta entre parênteses grupos
arquivos sem adicionar um segmento.

Quando duas coisas podem responder a mesma URL, **a primeira cadastrada vence**, e Nexy sempre
registra nesta ordem:

1. o endpoint de Ações;
2. arquivos estáticos: `/public`, `/assets`, `/favicon.ico`;
3. um modular `APIRouter` (`useRouter`);
4. rotas de arquivo, as mais específicas primeiro: caminhos estáticos, depois caminhos dinâmicos com os segmentos mais fixos,
   então pega-tudo.

Duas rotas de arquivos de igual especificidade são registradas em ordem alfabética de caminhos, então `[id].nexy`
respostas antes de `[slug].nexy`. Uma rota modular, portanto, supera uma página com o mesmo caminho. Este é um
ordem de precedência na qual você pode confiar, não uma regra de desempate para brincar: forneça a um URL um arquivo.

## O sistema de visualização

A extensão de um arquivo decide o que é, e a configuração do projeto decide quais extensões são
ativo.

| Extensão | Ativa quando | Compilada por | Servida como |
|---|---|---|---|
| `.nexy` | modo servidor | Nexy: frontmatter se torna Python, a marcação se torna Jinja2 | uma página |
| `.md` | sempre | Nexy: Markdown com sabor de GitHub, ids de cabeçalho, índice | uma página, dentro do layout mais próximo |
| `.mdx` | sempre | Vite, com React ou Preact | uma rota de componente |
| `.tsx` | `useFF` é React, Solid ou Preact | Vite e o framework | uma rota de componente |
| `.vue` | `useFF` é Vue | Vite e Vue | uma rota de componente |
| `.svelte` | `useFF` é Svelte | Vite e Svelte | uma rota componente |
| `.py` | sempre | Python | um manipulador de API: `GET`, `POST`, ... são os métodos |

Um arquivo cuja extensão não está ativa é ignorado com um aviso e não é veiculado. No modo cliente, `.nexy`
é rejeitado antes do servidor ser iniciado. Consulte [Convenções de arquivo](../reference/file-conventions.md).

## O ciclo de vida da renderização

Três perguntas decidem tudo o que o leitor percebe:

| Pergunta | Resposta | Página |
|---|---|---|
| Quem produz o HTML? | o servidor ou o navegador para uma rota do cliente | [Renderização](../rendering/README.md) |
| Quando os dados são lidos? | em cada solicitação, em cada regeneração ou no navegador | [SSR](../rendering/ssr.md), [ISR](../rendering/isr.md) |
| Quando o JavaScript chega? | apenas para uma ilha, ou para todo o documento | [Ilhas](../rendering/islands.md), [CSR](../rendering/csr.md) |

No modo servidor, o servidor renderiza cada página, `revalidate` armazena em cache uma página por URL e as ilhas adicionam
JavaScript para um componente. No modo cliente, o primeiro documento é renderizado em Node e navegação
então acontece no navegador.

`__nexy__/` contém tudo o que é gerado: páginas compiladas, a entrada do cliente, a saída da compilação. Nunca
edite-o, nunca comprometa-o; exclua-o para forçar uma compilação limpa.

## A integração front-end

**Vite não substitui Nexy.** Vite agrupa e fornece código de cliente. Ele não encaminha uma solicitação,
renderize uma página `.nexy`, execute uma ação ou possua a origem. O navegador se comunica com uma origem - Nexy's -
e no desenvolvimento, o Nexy faz proxy dos endpoints do Vite por meio dele, portanto, não há CORS para configurar.

**Nexy não substitui React.** Nexy decide qual componente será renderizado, quando e com quais adereços;
a estrutura possui o modelo de componentes, a reatividade e o ecossistema. Uma página `.nexy` importa um
componente como uma ilha; no modo cliente, uma rota *é* um componente.

Para uma rota de componente, o Python escreve apenas um módulo wrapper fino que aponta para o arquivo. O
a compilação e a renderização do lado do servidor são trabalho do Vite.

## Desenvolvimento e produção

| | `nx dev` | `nx build` então `nx start` |
|---|---|---|
| Páginas | compiladas quando você salva | compiladas uma vez, antecipadamente |
| Código do cliente | Vite dev server com hot reload, por trás da própria origem do Nexy | pacote em `__nexy__/client/`, HTML pré-renderizado |
| Node.js | roda próximo ao Python | não é necessário para servir |
| Erros | sobreposição no navegador, barra de ferramentas em todas as páginas | páginas de status sem detalhes |
| Origem | uma porta, `3000` | uma porta |

O que não muda: as mesmas regras de roteamento, os mesmos arquivos de páginas, os mesmos `nexyconfig.py`. Uma página
que se comporta de maneira diferente entre os dois é um bug, não um modo.

## Indo mais fundo

- [Estrutura do projeto](project-structure.md): todas as pastas de um projeto
- [Renderização](../rendering/README.md): SSR, ISR, CSR e ilhas
- [Frontend](../guides/frontend.md): Vite, estilo e construção do cliente
- [Routing](../routing/README.md): os roteadores baseados em arquivo, modulares e personalizados