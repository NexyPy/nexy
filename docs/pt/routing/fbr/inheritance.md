# Herança

Vários arquivos em `src/routes/` se aplicam a tudo abaixo de seu diretório. Todos eles resolvem da mesma maneira: Nexy começa no diretório da rota e caminha até `src/routes/`.

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| Arquivo | Regra |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | cada layout da raiz até a página envolve-o, **o mais externo primeiro** |
| `middleware.py` | cada arquivo da raiz até a rota envolve a solicitação, **mais externo primeiro**, antes das dependências |
| `dependencies.py` | cada arquivo da raiz até a rota é executado, **mais externo primeiro**, depois os próprios guardas do manipulador |
| `notfound.nexy`, `errors.nexy` | o **mais próximo** vence, por código de status |

Para a página acima, os layouts são aninhados como `root layout > (shop) layout > cart layout > page` e as dependências são executadas como `root > (shop) > cart > handler guards`.

## Por que o mais externo primeiro

Um layout externo desenha a moldura e uma dependência externa decide quem pode entrar. Colocá-los em primeiro lugar significa que os internos podem confiar neles: um diretório que requer autenticação é executado antes de um manipulador que lê o usuário.

A dependência `(shop)` da árvore verifica o cookie do carrinho, então a dependência do carrinho abaixo dela pode ler o carrinho sem verificar novamente:

```python filename="src/routes/(loja)/dependencies.py"
from nexy.http import HTTPException, Request


def require_cart(request: Request) -> None:
    if "cart" not in request.cookies:
        raise HTTPException(status_code=400, detail="No cart")


dependencies = [require_cart]
```

## Layouts

Todos os arquivos de layout de uma pilha de família de pastas: consulte [Layouts](layouts/README.md). Famílias diferentes não se misturam: um `layout.vue` nunca quebra uma página `.tsx`, e um projeto tem `layout.nexy` ou layouts de cliente, nunca ambos ([modos](modes.md)).

O layout mais interno da árvore apenas adiciona seu próprio quadro: o layout raiz ao redor ainda desenha o documento.

```nexy filename="src/rotas/(loja)/cart/layout.nexy"
---
children: prop[NexyElement]
---
<section class="cart">
  <h2>Your cart</h2>
  {{ children | safe }}
</section>
```

## Arquivos de middleware

Veja [Arquivos de middleware](middleware/README.md): eles rodam antes das dependências e podem responder sem atingir a rota.

Uma raiz `middleware.py` envolve todas as rotas da árvore, incluindo o carrinho:

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## Dependências

Consulte [Dependências](dependencies/README.md) para a ordem em um arquivo manipulador, incluindo `@UseGuard` e `@Middleware`.

## Páginas de erro

`notfound.nexy` e `errors.nexy` são instalados uma vez na raiz das rotas; uma cópia em um subdiretório refina a página para esse prefixo. Consulte [Páginas de erro](errors/README.md).

Uma cópia em `cart/` responde aos 404 em `/cart`, e a raiz mantém o resto:

```nexy filename="src/rotas/(loja)/cart/notfound.nexy"
---
title: Product not found
---
<h1>This product is gone</h1>
<p><a href="/cart">Back to your cart</a></p>
```

## Próximas etapas

- [Layouts](layouts/README.md)
- [Dependências](dependencies/README.md)
- [Páginas de erro](errors/README.md)
