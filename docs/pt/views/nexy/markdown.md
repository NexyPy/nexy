# Markdown e MDX

Dois formatos para páginas de conteúdo: `.md` quando você precisar apenas de Markdown, `.mdx` quando precisar de componentes.

## `.md`: puro Markdown

Um arquivo `.md` é puro conteúdo. Nexy o renderiza com `cmarkgfm` (GFM), adiciona IDs de cabeçalho, deriva um índice e o agrupa no `layout.*` mais próximo.

```md filename="src/rotas/about.md"
# About

Nexy is a fullstack Python meta-framework.
```

- Frontmatter em `.md` não é usado como lógica Python. Se você precisar de lógica de servidor, use `.nexy`.
- Quebra de layout, páginas de erro e segmentos dinâmicos funcionam da mesma maneira que outras páginas.

## `.mdx`: Markdown com componentes

Os arquivos `.mdx` são compilados por **Vite**, através do pipeline de rota da estrutura (React ou Preact). Python grava apenas o wrapper fino que atende a rota; ele nunca compila ou renderiza MDX a si mesmo. Os componentes são renderizados pela estrutura, renderizados no servidor como outras rotas de componentes e pré-renderizados para HTML por `nx build`.

- Requer que `useFF` seja React ou Preact.
- Requer os pacotes opcionais `@mdx-js/rollup`, `remark-gfm` e `@mdx-js/react` (e `@mdx-js/esbuild` para a compilação). Vite informa qual está faltando.
- A estrutura é detectada automaticamente nas importações: Preact quando o arquivo importa `preact`, React caso contrário.

> [!NOTA]
> use `.nexy` se precisar de lógica Python no frontmatter.

## Próximas etapas

- [.nexy files](README.md): o formato da página nativa
- [Visualizações](../README.md): escolha um formato
- [i18n](../../guides/i18n.md): internacionalização
