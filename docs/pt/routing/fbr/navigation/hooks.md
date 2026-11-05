# Ganchos

Os ganchos leem a solicitação HTTP atual de dentro de uma página `.nexy`, um manipulador de API ou um controlador modular. Seus nomes correspondem aos ganchos do roteador cliente (`@nexy/client`) onde eles fazem a mesma coisa.

> [!NOTE]
> os ganchos só funcionam enquanto uma solicitação está sendo tratada. Pagar um em qualquer outro lugar aumenta `RuntimeError`.

## Os ganchos

| Gancho | Retorna |
|---|---|
| `usePathname()` | caminho de solicitação, por exemplo. `"/blog/post-1"` |
| `useSearchParams()` | string de consulta como `dict[str, str]`, primeiro valor por chave |
| `useParams()` | parâmetros de caminho dinâmico, por ex. `{"slug": "post-1"}` |
| `useQuery()` | o nome original de `useParams()`, mantido para páginas existentes |
| `useRequest()` | a solicitação Starlette, para o que os outros ganchos não cobrem |
| `useHeaders()` | os cabeçalhos da solicitação como `dict[str, str]`, nomes em letras minúsculas |
| `useUrl()` | o URL completo: `.scheme`, `.hostname`, `.port`, `.path`, `.query` |
| `useIsActive(href, exact=False)` | se `href` é a página atual ou um de seus pais |
| `useRouter()` | `{"path", "base_url", "url_for"}` |
| `useCookies()` | todos os cookies como `dict[str, str]` |
| `useSession()` | o ditado da sessão, `{}` quando as sessões não estão habilitadas |
| `useToc(depth_range="2-6")` | índice HTML para a página atual, `""` quando nenhum |
| `useViews(path, context=None)` | renderiza outra visualização e retorna um `HTMLResponse` |

## Leia o pedido

```nexy filename="src/rotas/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```

## Um link ativo em uma barra de navegação

`useIsActive` segue a mesma regra do cliente: a string de consulta, o fragmento e uma barra final são ignorados, um link para um pai está ativo em seus filhos, a menos que `exact` esteja definido, e `/` só está ativo em `/`.

```nexy filename="src/componentes/NavLink.nexy"
---
from nexy import useIsActive

href: prop[str]
label: prop[str]
---
<a href="{{ href }}"{% if useIsActive(href) %} aria-current="page"{% endif %}>{{ label }}</a>
```

## Notas

- `useQuery()` retorna os parâmetros **path**, não a string de consulta, e é por isso que `useParams()` existe. A string de consulta é `useSearchParams()`.
- `useRouter()` aqui está o gancho de solicitação. Não é o campo de configuração `useRouter` que monta um `APIRouter`.
- `useSession()` precisa de `useSession = {...}` em `nexyconfig.py`; sem ele, o ditado está vazio.
- `useViews("about.tsx", {"title": "About"})` retorna HTML: uma visualização `.nexy` é renderizada por seu módulo compilado, uma visualização `.tsx`/`.jsx`/`.vue`/`.svelte`/`.mdx` se torna um contêiner de montagem do cliente.

## Próximas etapas

- [Páginas](../pages/README.md): segmentos dinâmicos e layouts
- [Receitas](../../../guides/recipes.md): um fluxo de login testado baseado em `useSession()`
- [Config](../../../reference/config.md): habilitar sessões e localidades
- [.nexy files](../../../views/nexy/README.md): onde os ganchos geralmente são chamados
