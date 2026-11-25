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

| Estrutura | Importar |
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

| Prop | Significado |
|---|---|
| `href` | Uma rota do projeto (um erro de digitação é um erro de tipo), opcionalmente com `?query` ou `#fragment`, ou uma URL externa. |
| `replace` | Substitua a entrada do histórico em vez de adicionar uma. |
| `scroll` | `false` mantém a posição de rolagem após navegar. Padrão: `true`. |
| `prefetch` | `'intent'` (padrão) carrega a página ao passar o mouse, focar ou tocar; `'viewport'` quando o link aparece; `false` nunca. |
| `activeClassName` | Adicionado à classe enquanto o link aponta para a página atual ou para uma página abaixo dela (`activeClass` em Vue e Svelte). |
| `exact` | Ativo apenas na página exata. |

O link que aponta para a página atual também recebe `aria-current="page"`.

## Ganchos

A localização está disponível em todas as estruturas, no idioma dessa estrutura. Durante o primeiro, o lado do servidor renderiza a resposta dos ganchos com a URL da solicitação, para que a página seja hidratada sem incompatibilidade.

| | React, Preact | Solid | Vue | Svelte |
|---|---|---|---|---|
| Caminho | `usePathname()` | `usePathname()` retorna um acessador | `usePathname()` retorna uma referência | `$pathname` loja |
| Parâmetros de rota | `useParams()` | `useParams()` acessador | `useParams()` referência | `$params` loja |
| Consulta | `useSearchParams()` | `useSearchParams()` acessador | `useSearchParams()` referência | `$searchParams` loja |
| Tudo | `useLocation()` | `useLocation()` acessador | `useLocation()` referência | `$location` loja |
| Navegar | `useRouter()` | `useRouter()` | `useRouter()` | `router` |
| Navegação em voo | `useTransition()` | `useTransition()` acessador | `useTransition()` referência | `useTransition()` loja |
| Combine um caminho | `useMatch(path?)` | `useMatch(path?)` acessador | `useMatch(path?)` referência | `useMatch(path?)` loja |
| Pergunte antes de sair | `useBlocker(dirty)` | `useBlocker(dirty())` em `createEffect` | `useBlocker(dirtyRef)` | `useBlocker(dirty)` em `$effect` |

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

## Mostre um estado de carregamento com `useTransition`

`useTransition()` informa se a navegação do cliente está em voo. `pending` é `true` desde o clique até a próxima página ser mostrada, e `next` é o local para onde ela está indo. Volta para `{ pending: false, next: null }` assim que a página é mostrada, quando a navegação para ou quando uma mais nova a substitui.

```tsx
import { useTransition } from "@nexy/client";

export default function Progress() {
  const { pending, next } = useTransition();
  return pending ? <p role="status">Loading {next?.pathname}</p> : null;
}
```

## Combine um caminho com `useMatch`

`useMatch(path)` informa se `path` corresponde a uma rota do cliente. Ele retorna `{ match, found }`, onde `match` contém a rota `file`, seu `layouts` e seu `params`, ou é `null`. Sem caminho ele corresponde à página atual e segue cada navegação. Durante a renderização do servidor ainda não há roteador, então `match` é `null` e `found` é `false`.

```tsx
import { useMatch } from "@nexy/client";

export default function Breadcrumb() {
  const { match } = useMatch();
  return match?.params.id ? <span>User {match.params.id}</span> : null;
}
```

## Capture uma página que falha com `ErrorBoundary`

`ErrorBoundary` mostra um substituto em vez de seus filhos quando um deles é lançado enquanto é renderizado no navegador. O fallback recebe o erro e `reset`, que renderiza os filhos novamente.

| Estrutura | Importar | Alternativa |
|---|---|---|
| React, Preact, Solid | `import { ErrorBoundary } from "@nexy/client"` | `fallback={(error, reset) => ...}` |
| Vue | `import { ErrorBoundary } from "@nexy/client"` | uma função `fallback` prop; as crianças vão para o slot padrão |
| Svelte | `import ErrorBoundary from "@nexy/ErrorBoundary.svelte"` | um trecho `fallback` |

```tsx
import { ErrorBoundary } from "@nexy/client";

<ErrorBoundary fallback={(error, reset) => <button onClick={reset}>{error.message}: retry</button>}>
  <Dashboard />
</ErrorBoundary>
```

```svelte
<ErrorBoundary>
  {#snippet fallback(error, reset)}
    <button onclick={reset}>{error.message}: retry</button>
  {/snippet}
  <Dashboard />
</ErrorBoundary>
```

Não pega:

- um erro lançado posteriormente, em um manipulador de eventos, um cronômetro ou uma promessa: capture-o onde acontecer. Vue é a exceção para seus próprios manipuladores de eventos, cujos erros atingem o limite;
- uma página que o roteador não pode carregar: em vez disso, o navegador a solicita ao servidor (consulte [O que o roteador faz](#what-the-router-does)).

## Pergunte antes de sair de uma página com alterações não salvas

`useBlocker(dirty, message?)` pergunta ao visitante antes de sair enquanto `dirty` é verdadeiro: um link, um `router.push`, os botões voltar e avançar, recarregar e uma aba fechada. A navegação do cliente mostra `message` em `confirm()`: sim continua, não permanece na página. Uma aba recarregada ou fechada mostra a pergunta do próprio navegador, que nenhuma página consegue formular. Sem mensagem, a pergunta é "Você tem alterações não salvas. Sair desta página?".

```tsx
import { useState } from "react";
import { useBlocker } from "@nexy/client";

export default function Editor() {
  const [text, setText] = useState("");
  const [saved, setSaved] = useState("");
  useBlocker(text !== saved, "Your draft is not saved. Leave anyway?");
  return (
    <form onSubmit={(event) => (event.preventDefault(), setSaved(text))}>
      <textarea value={text} onChange={(event) => setText(event.target.value)} />
      <button>Save</button>
    </form>
  );
}
```

A flag é lida onde muda, no idioma de cada framework:

| Estrutura | Siga a bandeira |
|---|---|
| React, Preact | `useBlocker(dirty)` em cada renderização |
| Vue | `useBlocker(dirty)` com `dirty` uma referência ou um cálculo |
| Solid | `createEffect(() => useBlocker(dirty()))` |
| Svelte | `$effect(() => useBlocker(dirty))` |

`useBlocker` também assume uma função, para uma decisão que depende de onde o visitante vai. Ele recebe o próximo local e o atual e retorna um motivo (uma string) para ficar ou nada para continuar:

```tsx
useBlocker((next) => (next.pathname.startsWith("/admin") ? "Admins only" : undefined));
```

Uma função não solicita por si só e não recarrega; ligue para `confirm()` para perguntar.

## `Image`

`Image` renderiza um `<img>` que é preguiçoso por padrão e não muda o layout quando seu tamanho é conhecido.

| Estrutura | Importar |
|---|---|
| React, Preact, Solid, Vue | `import { Image } from "@nexy/client"` |
| Svelte | `import Image from "@nexy/Image.svelte"` |

```tsx
<Image src="/photo.jpg" alt="A mountain" width={800} height={600} />
```

- `alt` é obrigatório; use `alt=""` para uma imagem decorativa. Nexy avisa uma vez quando está faltando.
- Com `width` e `height`, os atributos fornecem ao navegador a proporção e a imagem permanece fluida (`height: auto; max-width: 100%`).
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

A troca de página é executada dentro de uma transição de visualização do navegador quando há uma disponível: consulte [Como funcionam as transições de página](page-transitions.md).

Uma navegação mais recente cancela uma navegação mais antiga que ainda está sendo renderizada. Se uma página não puder ser renderizada, o navegador a solicitará ao servidor. Os botões voltar e avançar renderizam a página dessa entrada e restauram sua posição de rolagem.

```js
document.addEventListener("nexy:navigated", (event) => {
  console.log(event.detail.pathname, event.detail.params);
});
```

O roteador inicia apenas em um projeto com rotas de cliente, portanto, um projeto renderizado pelo servidor mantém o botão Voltar do próprio navegador e a restauração de rolagem.

## Próximas etapas

- [Layouts](../layouts/README.md)
- [RSE](../../../rendering/csr.md)
- [Componentes](../../../views/nexy/components.md)
