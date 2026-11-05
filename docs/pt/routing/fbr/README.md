# Roteamento baseado em arquivo

Uma rota é um arquivo. A URL é o caminho do arquivo relativo a `src/routes/`, menos a extensão.

## Arquivo para URL

| Arquivo | URL |
|---|---|
| `index.nexy` | `/` |
| `about.nexy` | `/about` |
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/{slug}` |
| `docs/[...path].nexy` | `/docs/{path:path}` |
| `(marketing)/pricing.nexy` | `/pricing` |
| `api/users.py` | `/api/users` |

`index` mapeia para seu diretório, não para `/index`. Um diretório entre parênteses é um **grupo**: ele organiza arquivos sem aparecer na URL.

No modo cliente, os arquivos de página são `.tsx`, `.vue` ou `.svelte` em vez de `.nexy`; as regras de URL são as mesmas.

## Dois modos

`useCSR` decide quais são as páginas. Os dois não podem ser misturados em um projeto: Nexy se recusa a iniciar quando uma página do servidor fica próxima a uma rota do cliente.

| Modo | Páginas | Layout raiz | Veja |
|---|---|---|---|
| Servidor (`useCSR = False`) | `.nexy`, `.md`, `.mdx` | `layout.nexy` | [Modo servidor e modo cliente](modes.md) |
| Cliente (`useCSR = True`) | arquivos de estrutura | `layout.tsx` | [layout.tsx](../../views/react/differences.md) |

`.py` arquivos são manipuladores de API em ambos os modos.

## O que não é uma rota

- Nomes de arquivos reservados: `layout.*`, `loading.nexy`, `errors.nexy`, `notfound.nexy`, `dependencies.py`, `middleware.py`, `__init__.py`.
- Arquivos e pastas começando com `_` ou `.`: use-os para parciais e rascunhos.
- Extensões que não estão ativas para o seu projeto. Um arquivo cuja extensão está inativa é ignorado com um aviso.

## Um arquivo por URL

Dois arquivos que resolvem para o mesmo URL são registrados. Não crie `blog.nexy` próximo a `blog/index.nexy` e não misture `index.nexy` e `index.py` para o mesmo caminho. Escolha um.

## Nesta seção

| Pasta | O que ela cobre |
|---|---|
| [páginas/](pages/README.md) | páginas, [rotas dinâmicas](pages/dynamic-routes.md), grupos de rotas |
| [layouts/](layouts/README.md) | uma página por tipo de arquivo de layout |
| [manipuladores/](handlers/README.md) | `.py` manipuladores, validação e erros |
| [dependências/](dependencies/README.md) | `dependencies.py`, guardas |
| [middleware/](middleware/README.md) | `middleware.py` |
| [erros/](errors/README.md) | páginas de erro e não encontradas |
| [navegação/](navigation/linking-and-navigating.md) | links, ganchos |
| [tempo real/](realtime/websocket.md) | WebSocket |
| [herança](inheritance.md) | as regras de herança em uma tabela |

## Próximas etapas

- [Modo servidor e modo cliente](modes.md)
- [Layouts](layouts/README.md)
- [Roteamento modular](../modular/README.md)
