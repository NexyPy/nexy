# Convenções de arquivo

Nomes e regras reservados em `src/routes/`.

## Arquivos de rota

| Arquivo | Torna-se |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | a rota de seu diretório |
| `about.nexy` | `/about` |
| `[slug].nexy` | segmento dinâmico `{slug}` |
| `[...path].nexy` | pega-tudo `{path:path}` |
| `(group)/page.nexy` | `/page`: o grupo não aparece na URL |
| `name.py` | manipulador de API; nomes de funções `GET`, `POST`, ... são os métodos |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | rota do cliente quando a estrutura está habilitada com `useFF` |

## Arquivos reservados

| Arquivo | Função | Detalhes |
|---|---|---|
| `layout.nexy` | modo servidor: envolve todas as páginas abaixo dele; o root possui o documento HTML | [layout.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | modo cliente (React): o raiz possui o documento HTML, os aninhados quebram as páginas | [layout.tsx](../views/react/differences.md) |
| `layout.vue`, `layout.svelte` | modo cliente: layouts aninhados | [layout.vue](../views/vue/differences.md), [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | página 404 para seu diretório | [Páginas de erro](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 páginas para seu diretório | [Páginas de erro](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | página 403 para seu diretório | [Páginas de erro por pasta](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | 401 página para seu diretório | [Páginas de erro por pasta](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | reservado; nenhum efeito de tempo de execução ainda | [Páginas de erro](../routing/fbr/errors/README.md) |
| `middleware.py` | um `async def middleware(request, call_next)` agrupando as solicitações do diretório e abaixo de | [Arquivos de middleware](../routing/fbr/middleware/README.md) |
| `dependencies.py` | uma lista `dependencies = [fn, ...]` aplicada ao diretório e seus filhos | [Dependências](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Marcador de pacote Python | |
| `favicon.ico` | servido em `/favicon.ico` | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions`,
`useUnauthorizedExtensions` e `useLoadingExtensions` reservam mais extensões para esses nomes. Veja
[Configuração](config.md).

## Arquivos ignorados

- Um arquivo ou pasta começando com `_` ou `.`: use-o para parciais, rascunhos e auxiliares.
- Um arquivo cuja extensão não está ativa para o projeto: é ignorado com um aviso.

## Um arquivo por URL

Dois arquivos que resolvem para o mesmo URL são registrados. Não coloque `blog.nexy` próximo a
`blog/index.nexy`.

## Fora `src/routes/`

| Pasta | Finalidade |
|---|---|
| `src/components/` | componentes importados por páginas; nunca encaminha |
| `src/apps/` | controladores e módulos do [roteador modular](../routing/modular/README.md) |
| `public/` | arquivos estáticos, servidos na raiz: `public/logo.svg` é `/logo.svg` (também em `/public/`) |
| `__nexy__/` | saída gerada; não cometa |

## Próximas etapas

- [Roteamento](../routing/README.md)
- [Estrutura do projeto](../getting-started/project-structure.md)