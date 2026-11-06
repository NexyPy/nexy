# Convenções de arquivo

Nomes e regras reservados em `src/routes/`.

## Arquivos de rota

| Arquivo | Torna-se |
|---|---|
| `index.nexy`, `index.md`, `index.mdx`, `index.py` | a rota do seu diretório |
| `about.nexy` | `/about` |
| `[slug].nexy` | segmento dinâmico `{slug}` |
| `[...path].nexy` | pega tudo `{path:path}` |
| `(group)/page.nexy` | `/page`: o grupo não aparece na URL |
| `name.py` | Manipulador de API; nomes de funções `GET`, `POST`, ... são os métodos |
| `name.tsx`, `.jsx`, `.vue`, `.svelte` | rota do cliente quando a estrutura está habilitada com `useFF` |

```text
src/routes/
├─ index.nexy           /
├─ about.nexy           /about
├─ (marketing)/
│  └─ pricing.nexy      /pricing
├─ blog/
│  ├─ index.md          /blog
│  └─ [slug].nexy       /blog/{slug}
├─ docs/
│  └─ [...path].nexy    /docs/{path:path}
└─ api/
   └─ users.py          GET /api/users, POST /api/users
```

```python filename="src/routes/api/users.py"
async def GET():
    return {"users": []}


async def POST():
    return {"created": True}
```

## Arquivos reservados

| Arquivo | Função | Detalhes |
|---|---|---|
| `layout.nexy` | modo servidor: envolve todas as páginas abaixo dele; o root possui o documento HTML | [layout.nexy](../views/nexy/layouts.md) |
| `layout.tsx` | modo cliente (React): o root possui o documento HTML, os aninhados quebram as páginas | [layout.tsx](../views/react/differences.md) |
| `layout.vue`, `layout.svelte` | modo cliente: layouts aninhados | [layout.vue](../views/vue/differences.md), [layout.svelte](../views/svelte/differences.md) |
| `notfound.nexy` | Página 404 para seu diretório | [Páginas de erro](../routing/fbr/errors/README.md) |
| `errors.nexy` | 500 páginas para seu diretório | [Páginas de erro](../routing/fbr/errors/README.md) |
| `forbidden.nexy` | Página 403 para seu diretório | [Páginas de erro por pasta](../routing/fbr/errors/folder-pages.md) |
| `unauthorized.nexy` | Página 401 para seu diretório | [Páginas de erro por pasta](../routing/fbr/errors/folder-pages.md) |
| `loading.nexy` | reservado; nenhum efeito de tempo de execução ainda | [Páginas de erro](../routing/fbr/errors/README.md) |
| `middleware.py` | um `async def middleware(request, call_next)` envolvendo as solicitações do diretório e abaixo | [Arquivos de middleware](../routing/fbr/middleware/README.md) |
| `dependencies.py` | uma lista `dependencies = [fn, ...]` aplicada ao diretório e seus filhos | [Dependências](../routing/fbr/dependencies/README.md) |
| `__init__.py` | Python marcador de pacote | |
| `favicon.ico` | servido em `/favicon.ico` | |

`useLayoutExtensions`, `useNotFoundExtensions`, `useErrorsExtensions`, `useForbiddenExtensions`, `useUnauthorizedExtensions` e `useLoadingExtensions` reservam mais extensões para esses nomes. Consulte [Configuração](config.md).

Os dois Python arquivos da tabela, lado a lado em uma pasta:

```python filename="src/routes/admin/middleware.py"
from nexy.http import Request


async def middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["x-admin"] = "1"
    return response
```

```python filename="src/routes/admin/dependencies.py"
from nexy.http import Header, HTTPException


def require_admin(x_role: str = Header(...)) -> None:
    if x_role != "admin":
        raise HTTPException(status_code=403, detail="Admins only")


dependencies = [require_admin]
```

E uma página que responde o 404 da sua pasta:

```nexy filename="src/rotas/notfound.nexy"
<h1>Page not found</h1>
<p><a href="/">Back home</a></p>
```

## Arquivos ignorados

- Um arquivo ou pasta começando com `_` ou `.`: use-o para parciais, rascunhos e auxiliares.
- Um arquivo cuja extensão não está ativa para o projeto: é ignorado com um aviso.

```text
src/routes/
├─ index.nexy           /
├─ _card.nexy           ignored: a partial the pages include
├─ _helpers/            ignored, with everything inside
│  └─ format.py
└─ .draft.nexy          ignored: a draft
```

## Um arquivo por URL

Dois arquivos que resolvem para o mesmo URL são registrados. Não coloque `blog.nexy` próximo a `blog/index.nexy`.

```text
src/routes/
├─ blog.nexy            /blog
└─ blog/
   └─ index.nexy        /blog as well: keep only one of the two
```

## Fora `src/routes/`

| Pasta | Objetivo |
|---|---|
| `src/components/` | componentes importados por páginas; nunca rotas |
| `src/apps/` | controladores e módulos do [roteador modular](../routing/modular/README.md) |
| `public/` | arquivos estáticos, servidos na raiz: `public/logo.svg` é `/logo.svg` (também em `/public/`) |
| `__nexy__/` | saída gerada; não se comprometa |

```text
my-app/
├─ nexyconfig.py
├─ public/
│  └─ logo.svg          /logo.svg
├─ src/
│  ├─ routes/           the routes
│  ├─ components/
│  │  └─ Counter.tsx    imported by pages, never served on its own
│  └─ apps/             the modular router, when you use it
└─ __nexy__/            generated: add it to .gitignore
```

## Próximas etapas

- [Roteamento](../routing/README.md)
- [Estrutura do projeto](../getting-started/project-structure.md)
