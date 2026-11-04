# Markdown e MDX

Dois formatos para páginas de conteúdo: `.md` quando você precisa apenas de Markdown, `.mdx` quando precisa de componentes.

## `.md`: Markdown puro

Um arquivo `.md` é puro conteúdo. Nexy o renderiza com `cmarkgfm` (GFM), adiciona IDs de cabeçalho, deriva um
índice e o agrupa no `layout.*` mais próximo.

```md filename="src/rotas/about.md"
# About

Nexy is a fullstack Python meta-framework.
```

- Frontmatter em `.md` não é usado como lógica Python. Se você precisar de lógica de servidor, use `.nexy`.
- Ajuste de layout, páginas de erro e segmentos dinâmicos funcionam da mesma maneira que outras páginas.

## `.mdx`: Markdown com componentes

Os arquivos `.mdx` são compilados por **Vite**, através do pipeline de rota do framework (React ou Preact). Pitão
grava apenas o wrapper fino que atende a rota; ele nunca compila ou renderiza o próprio MDX.
Os componentes são renderizados pela estrutura, renderizados pelo servidor como outras rotas de componentes e
pré-renderizado para HTML por `nx build`.

- Requer que `useFF` seja React ou Preact.
- Requer os pacotes opcionais `@mdx-js/rollup`, `remark-gfm` e `@mdx-js/react` (e
  `@mdx-js/esbuild` para a construção). Vite informa qual está faltando.
- A estrutura é detectada automaticamente nas importações: Preact quando o arquivo é importado `preact`, React
  caso contrário.

> [!NOTA]
> use `.nexy` se precisar de lógica Python no frontmatter.

## Próximas etapas

- [.arquivos nexy](README.md): o formato da página nativa
- [Visualizações](../README.md): escolha um formato
- [i18n](../../guides/i18n.md): internacionalização