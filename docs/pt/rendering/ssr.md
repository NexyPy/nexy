# SSR (renderização de servidor)

## Definição

SSR é o padrão: o servidor renderiza a página em HTML para cada solicitação. Nada permite isso, e
nenhum sinalizador o desativa - um projeto no modo servidor é renderizado em cada solicitação, a menos que uma página declare
`revalidate`.

## Como funciona

| Arquivo de rota | O que produz o HTML | Quando |
|---|---|---|
| `.nexy` | o módulo Python compilado, através do Jinja2 | cada solicitação |
| `.md` | `cmarkgfm`, então o layout mais próximo | a cada solicitação |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | o framework, renderizado no Node | na construção quando a rota não tem layout, caso contrário no navegador |
| `.py` | nada: retorna JSON ou um `Response` | - |

Uma rota componente é o único caso que precisa de uma segunda frase. Na produção, uma rota de componentes
**sem** um layout é servido com o HTML produzido na construção, e o componente o hidrata. Com
um layout ou em desenvolvimento, o contêiner está vazio e o componente é renderizado no navegador - o
page é então um shell que se preenche.

## Ciclo de vida de renderização

1. A solicitação chega ao roteador baseado em arquivo. O caminho é correspondido e os segmentos dinâmicos são convertidos para
   os tipos que o componente declara.
2. O componente é executado. Aquele que espera no Node - um documento cliente - é executado em um pool de threads, então
   não paralisa o loop de eventos.
3. O corpo é transmitido como `text/html`. Um componente que produz pedaços os transmite à medida que faz
   eles.
4. O navegador recebe HTML. As ilhas hidratam de acordo com sua [diretiva](islands.md).

Um erro gerado durante a renderização é transformado em uma página por `errors.nexy` quando o projeto possui uma: veja
[páginas de erro](../routing/fbr/errors/README.md).

## Quando usar

- A página mostra algo que o leitor possui: uma sessão, uma conta, um carrinho.
- Os dados devem ser atualizados em cada carga.
- O conteúdo deve estar em HTML para crawlers que não executam JavaScript.
- A página é barata para renderizar: uma consulta, um modelo.

## Configuração

Nenhum. Duas saídas, e elas não têm a mesma granulação:

| Para deixar SSR para | Faça isso | Grão |
|---|---|---|
| uma página, com um cache | `revalidate = 60` em seu frontmatter → [ISR](isr.md) | página |
| todo o projeto, roteado pelo cliente | `useCSR = True` em `nexyconfig.py` → [CSR](csr.md) | projeto |

## Exemplo

```nexy filename="src/rotas/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` executa este modelo uma vez, com `slug` definido como `hello`. Uma segunda solicitação o executa
novamente: nada é mantido entre os dois. A string de consulta não é uma propriedade - leia-a com os ganchos em
[navegação](../routing/fbr/navigation/hooks.md).

## Limitações

- **Uma renderização por solicitação.** Dois visitantes no mesmo segundo pagam cada um pela renderização e pelo
  perguntas por trás disso.
- **Sem cache.** Não há cache de resposta compartilhada para aquecer: [ISR](isr.md) adiciona um, por URL.
- **O streaming só ajuda um componente que produz resultados.** Uma consulta lenta no topo da página ainda atrasa
  o primeiro byte.
- **Sem saída estática.** No modo servidor nada é congelado na compilação: não há modo SSG e não
  comando de exportação. Consulte [Renderização](README.md).
- **O escape automático está desativado** nos modelos `.nexy`. Escape de valores não confiáveis ​​com `| e`.

## Próximas etapas

- [ISR](isr.md): armazenar esta página em cache por URL
- [Ilhas](islands.md): mantenha o SSR e torne um widget interativo
- [CSR](csr.md): navegação manual para o navegador
- [Desempenho](../deployment/performance.md)