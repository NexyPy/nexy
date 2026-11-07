# SSR (renderização de servidor)

## Definição

SSR é o padrão: o servidor renderiza a página em HTML para cada solicitação. Nada o habilita e nenhum sinalizador o desativa - um projeto no modo servidor é renderizado a cada solicitação, a menos que uma página declare `revalidate`.

## Como funciona

<!-- router:fbr,custom -->
| Arquivo de rota | O que produz o HTML | Quando |
|---|---|---|
| `.nexy` | o módulo Python compilado, até Jinja2 | cada pedido |
| `.md` | Markdown, então o layout mais próximo | cada pedido |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | a estrutura, renderizada em Node | na construção quando a rota não tem layout, caso contrário no navegador |
| `.py` | nada: retorna JSON ou um `Response` | - |

Uma página Markdown e um manipulador, lado a lado no mesmo projeto:

```md filename="src/routes/changelog.md"
# Changelog

Rendered to HTML on every request, then wrapped in the nearest layout.
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

Uma rota componente é o único caso que precisa de uma segunda frase. Na produção, uma rota de componente **sem** um layout é veiculada com o HTML produzido na construção, e o componente o hidrata. Com um layout, ou em desenvolvimento, o contêiner fica vazio e o componente é renderizado no navegador - a página é então um shell que se preenche sozinho.

A rota do componente da tabela, sem layout, portanto a produção serve seu HTML desde o build:

```tsx filename="src/routes/pricing.tsx"
export default function Pricing() {
  return <h1>Pricing</h1>;
}
```
<!-- /router -->

<!-- router:modular -->
| Um controlador retorna | O que produz o HTML | Quando |
|---|---|---|
| `useViews("....nexy")` | o módulo Python compilado, através de Jinja2 | cada pedido |
| um `dict`, uma lista, um modelo | nada: FastAPI responde JSON | - |

Uma visualização e um endpoint JSON, lado a lado no mesmo módulo:

```nexy filename="src/apps/changelog_view.nexy"
<h1>Changelog</h1>
<p>Rendered to HTML on every request.</p>
```

```python filename="src/apps/site_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/changelog")
class ChangelogController:
    async def get(self):
        return useViews("src/apps/changelog_view.nexy")


@Controller("/api/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```
<!-- /router -->

## Ciclo de vida de renderização

<!-- router:fbr,custom -->
1. A solicitação chega ao roteador baseado em arquivo. O caminho é correspondido e os segmentos dinâmicos são convertidos nos tipos declarados pelo componente.

   ```nexy filename="src/routes/orders/[id].nexy"
   ---
   id: prop[int]
   ---
   <h1>Pedido nº{{ id + 1000 }}</h1>
   ```

   `/orders/42` renderiza `Order #1042`; `/orders/abc` respostas `404`.
2. O componente é executado. Aquele que espera no Node - um documento cliente - é executado em um pool de threads, portanto não paralisa o loop de eventos.
3. O corpo é transmitido como `text/html`. Um componente que produz pedaços os transmite à medida que os produz.
4. O navegador recebe HTML. As ilhas hidratam de acordo com sua [diretiva](islands.md).

Um erro gerado durante a renderização é transformado em uma página por `errors.nexy` quando o projeto possui uma: consulte [páginas de erro](../routing/fbr/errors/README.md).
<!-- /router -->

<!-- router:modular -->
1. A solicitação chega ao controlador. Seus parâmetros de caminho são convertidos para os tipos declarados pelo método e passados para a visualização:

   ```nome do arquivo python="src/apps/order_controller.py"
   do controlador de importação nexy.decorators
   de nexy.hooks importar useViews


   @Controller("/pedidos/{id}")
   classe OrderController:
       assíncrono def get(self, id: int):
           retornar useViews("src/apps/order_view.nexy", context={"id": id})
   ```

   ```nexy filename="src/apps/order_view.nexy"
   ---
   id: prop[int]
   ---
   <h1>Pedido nº{{ id + 1000 }}</h1>
   ```

   `/orders/42/` renderiza `Order #1042`; `/orders/abc/` respostas `404`.
2. A visualização é executada e `useViews` retorna seu HTML como resposta.
3. O navegador recebe HTML. As ilhas hidratam de acordo com sua [diretiva](islands.md).

Um erro gerado durante a renderização é respondido com a página de erro padrão.
<!-- /router -->

## Quando usar

- A página mostra algo que o leitor possui: uma sessão, uma conta, um carrinho.
- Os dados devem ser atualizados em cada carga.
- O conteúdo deve estar no HTML para crawlers que não executam JavaScript.
- A página é barata para renderizar: uma consulta, um modelo.

O primeiro caso, uma página que saúda o leitor da sessão. `useSession` lê a sessão de `useSession` em `nexyconfig.py`, sem a qual falha:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

<!-- router:fbr,custom -->
```nexy filename="src/rotas/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/account_view.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

## Configuração

<!-- router:fbr,custom -->
Nenhum. Duas saídas, e elas não têm a mesma granulação:

| Para deixar o SSR para | Faça isso | Grão |
|---|---|---|
| uma página, com cache | `revalidate = 60` em seu frontmatter → [ISR](isr.md) | página |
| todo o projeto, roteado pelo cliente | `useCSR = True` em `nexyconfig.py` → [CSR](csr.md) | projeto |

A opção em todo o projeto, em `nexyconfig.py`. O modo cliente precisa de uma estrutura de cliente:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```
<!-- /router -->

<!-- router:modular -->
Nenhum. Cada visualização retornada por um controlador é renderizada em cada solicitação: [ISR](isr.md) e [CSR](csr.md) são modos do roteador baseado em arquivo.
<!-- /router -->

## Exemplo

<!-- router:fbr,custom -->
```nexy filename="src/rotas/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` executa este modelo uma vez, com `slug` definido como `hello`. Uma segunda solicitação o executa novamente: nada é mantido entre os dois. A string de consulta não é uma propriedade - leia-a com os ganchos em [navegação](../routing/fbr/navigation/hooks.md).
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/blog_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/post_view.nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello/` executa esta visualização uma vez, com `slug` definido como `hello`. Uma segunda solicitação o executa novamente: nada é mantido entre os dois. A string de consulta não é uma propriedade - leia-a com `useSearchParams`.
<!-- /router -->

## Limitações

- **Uma renderização por solicitação.** Dois visitantes no mesmo segundo pagam cada um pela renderização e pelas consultas por trás dela.
- **Sem cache.** Não há cache de resposta compartilhada para aquecer: com rotas de arquivo, [ISR](isr.md) adiciona um, por URL.
- **O streaming ajuda apenas um componente que produz.** Uma consulta lenta no topo da página ainda atrasa o primeiro byte.
- **Nenhuma saída estática.** No modo servidor nada é congelado na construção: não há modo SSG e nenhum comando de exportação. Consulte [Renderização](README.md).
- **O escape automático está desativado** em `.nexy` modelos. Escape de valores não confiáveis ​​com `| e`.

<!-- router:fbr,custom -->
```nexy filename="src/rotas/search.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/search_view.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

## Próximas etapas

<!-- router:fbr,custom -->
- [ISR](isr.md): armazenar esta página em cache por URL
<!-- /router -->
- [Ilhas](islands.md): mantenha o SSR e torne um widget interativo
<!-- router:fbr,custom -->
- [CSR](csr.md): navegação manual para o navegador
<!-- /router -->
- [Desempenho](../deployment/performance.md)
