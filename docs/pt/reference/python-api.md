# Python API

Cada nome que o Nexy exporta para o seu código Python, por módulo. Um teste verifica esta página em relação ao código em ambas as direções: um nome listado aqui deve existir e um nome que o código exporta deve estar listado aqui.

## `nexy`

Componentes para modelos `.nexy` e ganchos de solicitação.

| Nome | O que é isso |
|---|---|
| `Audio`, `Video` | players nativos `<audio>` e `<video>`, consulte [componentes](../views/nexy/components.md) |
| `Image` | um `<img>` que carrega lentamente por padrão |
| `Link` | um lado do cliente `<a>` com pré-busca opcional |
| `Import` | importar um componente cliente para uma página `.nexy` |
| `Template` | renderizar modelos Jinja2 e Markdown |
| `Vite` | a tag do cliente Vite que toda página precisa |
| `Form` | um espaço reservado sem comportamento: use um `<form>` simples com uma [ação](../guides/actions.md) |
| `usePathname` | o caminho da solicitação atual |
| `useSearchParams` | a string de consulta como um ditado |
| `useParams` | os parâmetros do caminho dinâmico como um ditado, como `useParams()` no cliente |
| `useQuery` | o nome original de `useParams`, mantido para páginas existentes (não lê a string de consulta) |
| `useRequest` | a solicitação atual, para o que os outros ganchos não cobrem |
| `useHeaders` | os cabeçalhos da solicitação como um ditado com nomes em letras minúsculas |
| `useUrl` | o URL completo: `.scheme`, `.hostname`, `.path`, `.query` |
| `useIsActive` | se um link aponta para a página atual ou para um de seus pais, para uma barra de navegação |
| `useRouter` | `path`, `base_url` e `url_for` da solicitação atual |
| `useSession` | o ditado da sessão, vazio quando as sessões estão desativadas |
| `useCookies` | a solicitação de cookies como um ditado |
| `useToc` | o índice da página atual, como HTML |
| `useViews` | renderizar um arquivo de visualização como `about.tsx` de um manipulador |
| `setMetadata`, `useMetadata` | nomeie o título e as tags de cabeçalho de uma página e escreva-os no layout |
| `redirect`, `permanentRedirect` | envie o visitante para outro lugar (307, 308) e interrompa a solicitação |
| `notFound`, `forbidden`, `unauthorized` | responda 404, 403 ou 401 de qualquer lugar |

Os ganchos funcionam apenas dentro de uma solicitação: consulte [hooks](../routing/fbr/navigation/hooks.md).

<!-- router:fbr,custom -->
```nexy filename="src/rotas/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```
<!-- /router -->

## `nexy.http`

O vocabulário HTTP de um manipulador. Importe daqui em vez de FastAPI, para que seus manipuladores dependam do contrato da Nexy.

| Nome | O que é isso |
|---|---|
| `Request`, `Response` | a solicitação recebida e uma resposta de saída |
| `HTTPException` | pare o manipulador com um status e um `detail` |
| `status` | códigos de status nomeados, como `status.HTTP_404_NOT_FOUND` |
| `Depends` | execute uma função primeiro e passe seu resultado |
| `Header`, `Cookie`, `Query`, `Path`, `Body` | de onde vem um parâmetro |
| `Form`, `File`, `UploadFile` | campos de formulário e uploads (precisa de `python-multipart`) |
| `BackgroundTasks` | trabalho que é executado após o envio da resposta |
| `JSONResponse`, `HTMLResponse`, `PlainTextResponse` | respostas com um tipo de conteúdo fixo |
| `RedirectResponse` | um redirecionamento HTTP |
| `redirect`, `permanentRedirect` | levantar um redirecionamento (307, 308) de uma página, um manipulador, um controlador ou um guarda |
| `notFound`, `forbidden`, `unauthorized` | levante um 404, 403 ou 401 dos mesmos lugares |
| `FileResponse`, `StreamingResponse` | responda com um arquivo ou stream |

<!-- router:fbr,custom -->
```python filename="src/rotas/api/items/[id].py"
from nexy.http import Depends, Header, HTTPException, status


def api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad key")
    return x_api_key


async def GET(id: int, key: str = Depends(api_key)):
    return {"id": id}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/items/items_by_id_api_controller.py"
from nexy.decorators import Controller
from nexy.http import Depends, Header, HTTPException, status


def api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad key")
    return x_api_key


@Controller("/api/items/{id}")
class ItemsByIdApiController:
    async def get(self, id: int, key: str = Depends(api_key)):
        return {"id": id}
```

Liste o controlador em `controllers` do módulo raiz.
<!-- /router -->

## `nexy.decorators`

| Nome | O que é isso |
|---|---|
| `Action` | transformar uma função em um endpoint `POST`, consulte [ações](../guides/actions.md) |
| `revalidate` | diga ao navegador quais páginas uma ação tornou obsoleta |
| `Module`, `Controller` | declare um módulo e um controlador no [roteador modular](../routing/modular/README.md) |
| `Injectable`, `Container`, `Scope` | [injeção de dependência](../routing/modular/dependency-injection.md) e seus tempos de vida |
| `UseGuard`, `Middleware` | guarde ou envolva um manipulador, consulte [guardas](../routing/modular/guards-and-metadata.md) |
| `UseRoute`, `useRoute`, `RouteMeta` | nomeie uma rota e descreva-a para OpenAPI |
| `UseResponse`, `ResponseMeta` | descrever a resposta de uma rota |
| `HTTP_METHODS` | os métodos HTTP que um arquivo manipulador pode definir |
| `ACTIONS_STORE` | o registro de ações, para ferramentais e testes |

```python filename="src/actions/posts.py"
from nexy.decorators import Action, revalidate


@Action
async def publish(post_id: int) -> bool:
    revalidate("/blog")
    return True
```

## `nexy.testing`

| Nome | O que é isso |
|---|---|
| `render` | o HTML de um componente `.nexy` para determinados adereços, sem servidor, consulte [testes](../guides/testing.md) |

```python filename="testes/test_button.py"
from nexy.testing import render


def test_the_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

## Onde será o próximo

- [Configuração](config.md): os campos `use*` por trás desses nomes
- [Exceções e erros](exceptions.md): o que cada falha responde
- [Índice de documentação](../README.md): a página do que você está construindo
