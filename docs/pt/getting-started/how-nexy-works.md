# Como funciona o Nexy

O modelo mental em uma página: o que Nexy constrói, o que Vite constrói e o que acontece entre um arquivo e uma página em seu navegador. Leia uma vez; o resto da documentação é então um conjunto de detalhes.

## A arquitetura Nexy

Uma solicitação atravessa cinco camadas: Uvicorn a aceita, o middleware a decora, o roteador escolhe um arquivo, o renderizador transforma esse arquivo em HTML ou JSON e a camada do cliente assume o controle se a página tiver JavaScript. Nexy possui os três do meio; Vite e sua estrutura são donas do cliente; seu aplicativo possui os dados, a autenticação e a autorização.

Cada camada, e o que ela se recusa a fazer, está em [Arquitetura](../architecture.md). Para os pacotes do próprio Nexy, veja `ARCHITECTURE.md` na raiz do repositório - ele foi escrito para contribuidores.

## O ciclo de vida do aplicativo

`nx dev` faz seis coisas antes da primeira solicitação:

1. valida `nexyconfig.py` e para em uma configuração inválida;
2. garante que os pacotes Python do projeto sejam importáveis;
3. resolve as portas e exclui o marcador obsoleto `__nexy__/nexy.prod`;
4. gera os arquivos do cliente e compila as rotas, em paralelo;
5. inicia Vite e espera até que ele responda;
6. instala o inspetor de arquivos e permite a importação do uvicorn `nexy.modules.routers.app:_server`.

Essa importação monta o aplicativo – middleware, ações, roteadores, manipuladores de erros – e a primeira solicitação é atendida por esse assembly. Quando você salva, o observador reinicia o uvicorn; uma página que apareceu, desapareceu ou foi movida também regenera a lista de rotas do cliente.

## O sistema de roteamento

Um caminho em `src/routes/` torna-se um URL por quatro regras:

| Arquivo | URL |
|---|---|
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/hello` |
| `blog/[...parts].nexy` | `/blog/a/b` |
| `(marketing)/about.nexy` | `/about` |

A extensão nunca aparece; `index` é a rota de sua pasta; uma pasta entre parênteses agrupa arquivos sem adicionar um segmento.

Quando duas coisas podem responder a mesma URL, **a primeira cadastrada vence**, e Nexy sempre se cadastra nesta ordem:

1. o ponto final de Ações;
2. arquivos estáticos: `/public`, `/assets`, `/favicon.ico`;
3. um modular `APIRouter` (`useRouter`);
4. rotas de arquivo, as mais específicas primeiro: caminhos estáticos, depois caminhos dinâmicos com os segmentos mais fixos e, em seguida, caminhos genéricos.

Duas rotas de arquivos de igual especificidade são registradas em ordem alfabética de caminhos, então `[id].nexy` responde antes de `[slug].nexy`. Uma rota modular, portanto, supera uma página com o mesmo caminho. Esta é uma ordem de precedência na qual você pode confiar, não uma regra de desempate para brincar: dê a um URL um arquivo.

## O sistema de visualização

A extensão de um arquivo decide o que é, e a configuração do projeto decide quais extensões estão ativas.

| Extensão | Ativa quando | Compilada por | Servida como |
|---|---|---|---|
| `.nexy` | modo servidor | Nexy: frontmatter se torna Python, a marcação se torna Jinja2 | uma página |
| `.md` | sempre | Nexy: com sabor de GitHub Markdown, IDs de cabeçalho, índice | uma página, dentro do layout mais próximo |
| `.mdx` | sempre | Vite, com React ou Preact | uma rota componente |
| `.tsx` | `useFF` é React, Solid ou Preact | Vite e a estrutura | uma rota de componente |
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
| Quando chega JavaScript? | apenas para uma ilha, ou para todo o documento | [Ilhas](../rendering/islands.md), [CSR](../rendering/csr.md) |

No modo servidor, o servidor renderiza cada página, `revalidate` armazena em cache uma página por URL e as ilhas adicionam JavaScript a um componente. No modo cliente, o primeiro documento é renderizado no Node e a navegação acontece no navegador.

`__nexy__/` contém tudo o que é gerado: páginas compiladas, a entrada do cliente, a saída da compilação. Nunca edite, nunca comprometa; exclua-o para forçar uma compilação limpa.

## A integração front-end

**Vite não substitui Nexy.** Vite agrupa e fornece código do cliente. Ele não roteia uma solicitação, renderiza uma página `.nexy`, executa uma ação ou possui a origem. O navegador se comunica com uma origem - Nexy's - e em desenvolvimento Nexy proxies Vite os endpoints através dele, portanto não há CORS para configurar.

**Nexy não substitui React.** Nexy decide qual componente será renderizado, quando e com quais adereços; a estrutura possui o modelo de componentes, a reatividade e o ecossistema. Uma página `.nexy` importa um componente como uma ilha; no modo cliente, uma rota *é* um componente.

Para uma rota de componente, Python escreve apenas um módulo wrapper fino que aponta para o arquivo. A compilação e a renderização do lado do servidor são trabalho de Vite.

## Desenvolvimento e produção

| | `nx dev` | `nx build` então `nx start` |
|---|---|---|
| Páginas | compiladas quando você salva | compiladas uma vez, antecipadamente |
| Código do cliente | Vite dev server com hot reload, por trás do próprio pacote de origem do Nexy | em `__nexy__/client/`, HTML pré-renderizado |
| Node.js | executado ao lado de Python | não é necessário para veicular |
| Erros | sobreposição no navegador, barra de ferramentas em todas as páginas | páginas de status sem detalhes |
| Origem | uma porta, `3000` | uma porta |

O que não muda: as mesmas regras de roteamento, os mesmos arquivos de páginas, os mesmos `nexyconfig.py`. Uma página que se comporta de maneira diferente entre as duas é um bug, não um modo.

## Indo mais fundo

- [Estrutura do projeto](project-structure.md): todas as pastas de um projeto
- [Renderização](../rendering/README.md): SSR, ISR, CSR e ilhas
- [Frontend](../guides/frontend.md): Vite, estilo e construção do cliente
- [Routing](../routing/README.md): os roteadores baseados em arquivos, modulares e personalizados
