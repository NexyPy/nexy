# Vinculando e navegando

Com o roteamento de cliente (`useCSR = True`), um link entre duas páginas troca a página no navegador em vez de recarregar o documento. Os layouts mantêm seu estado.

## Links simples já funcionam

Cada `<a href>` para uma página do seu projeto navega no cliente, sem componente e sem marcador:

```html
<a href="/about">About</a>
```

Um link é deixado no navegador e carrega a página normalmente, quando:

- uma tecla modificadora é pressionada ou o botão não é o principal;
- tem `target` (diferente de `_self`), `download`, `rel="external"` ou `data-nexy-reload`;
- o `href` é outra origem, um link `mailto:` ou `tel:`, ou apenas um `#fragment`;
- o caminho não corresponde a nenhuma rota do cliente, então o servidor responde.

## `Link`

`Link` é a mesma âncora que uma simples não pode fazer: seu `href` é verificado em relação às suas rotas, aquece a página de destino e sabe quando aponta para a página atual. Nexy gera o `Link` do seu framework em `__nexy__/src` quando você executa `nx dev` ou `nx build`.

| Estrutura | Importação |
|---|---|
| React, Preact, Solid, Vue | `import { Link } from "@nexy/client"` |
| Svelte | `import Link from "@nexy/Link.svelte"` |

```tsx
import { Link } from "@nexy/client";

export default function Nav() {
  return (
    <Link href="/dashboard" activeClassName="on">
      Dashboard
    </Link>
  );
}
```

| Suporte | Significado |
|---|---|
| `href` | Uma rota do projeto (um erro de digitação é um erro de tipo), opcionalmente com `?query` ou `#fragment`, ou uma URL externa. |
| `replace` | Substitua a entrada do histórico em vez de adicionar uma. |
| `scroll` | `false` mantém a posição de rolagem após navegar. Padrão: `true`. |
| `prefetch` | `'intent'` (padrão) carrega a página ao passar o mouse, focar ou tocar; `'viewport'` quando o link aparece; `false` nunca. |
| `activeClassName` | Adicionado à classe enquanto o link aponta para a página atual ou uma página abaixo dela (`activeClass` em Vue e Svelte). |
| `exact` | Ativo apenas na página exata. |

O link que aponta para a página atual também recebe `aria-current="page"`.

## Ganchos

A localização está disponível em todas as estruturas, no idioma dessa estrutura. Durante o primeiro, o lado do servidor renderiza a resposta dos ganchos com a URL da solicitação, para que a página seja hidratada sem incompatibilidade.

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| Caminho | `usePathname()` | `usePathname()` retorna um acessador | `usePathname()` retorna uma referência | `$pathname` loja |
| Parâmetros de rota | `useParams()` | `useParams()` acessador | `useParams()` ref | `$params` loja |
| Consulta | `useSearchParams()` | `useSearchParams()` acessador | `useSearchParams()` ref | `$searchParams` loja |
| Tudo | `useLocation()` | `useLocation()` acessador | `useLocation()` ref | `$location` loja |
| Navegue | `useRouter()` | `useRouter()` | `useRouter()` | `router` |

A consulta é um `URLSearchParams`. `useRouter()` e `router` fornecem `push(href)`, `replace(href)`, `back()`, `forward()`, `refresh()` e `prefetch(href)`; `push` e `replace` aceitam `{ scroll: false }`.

```tsx
import { useParams, useRouter, useSearchParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  const tab = useSearchParams().get("tab") ?? "profile";
  const router = useRouter();
  return <button onClick={() => router.push(`/users/${id}?tab=posts`)}>{tab}</button>;
}
```

## `Image`

`Image` renderiza um `<img>` que é preguiçoso por padrão e não muda o layout quando seu tamanho é conhecido.

| Estrutura | Importação |
|---|---|
| React, Preact, Solid, Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` é obrigatório; use `alt=""` para uma imagem decorativa. Nexy avisa uma vez quando está faltando.
- Com `width` e `height`, os atributos fornecem ao navegador a proporção de aspecto e a imagem permanece fluida (`height: auto; max-width: 100%`).
- `priority` carrega a imagem agora em alta prioridade, para aquela que está visível na chegada.
- `fill` faz a imagem cobrir seu pai posicionado, ignorando `width` e `height`.
- `sizes` e `srcSet` passam. Nexy não redimensiona nem converte imagens.

## Link de uma página `.nexy`

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` renderiza `<a href="/about" data-nexy-link="true">`. Cada atributo e `href` têm escape de HTML.

## O que o roteador faz

Numa navegação, o roteador:

1. corresponde ao caminho com as rotas do cliente (`.tsx`, `.jsx`, `.vue`, `.svelte`);
2. importa e renderiza a página e seus [layouts](../layouts/README.md) **primeiro**, e só então move a URL com `history.pushState`, para que a barra de endereço nunca mostre uma página que falhou;
3. despacha um evento `nexy:navigated` em `document`;
4. rola para o topo ou para o alvo `#fragment`.

Uma navegação mais recente cancela uma navegação mais antiga que ainda está sendo renderizada. Se uma página não puder ser renderizada, o navegador a solicitará ao servidor. Os botões voltar e avançar renderizam a página dessa entrada e restauram sua posição de rolagem.

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

O roteador inicia apenas em um projeto com rotas de cliente, portanto, um projeto renderizado pelo servidor mantém o botão Voltar do próprio navegador e a restauração de rolagem.

## Próximas etapas

- [Layouts](../layouts/README.md)
- [CSR](../../../rendering/csr.md)
- [Componentes](../../../views/nexy/components.md)
