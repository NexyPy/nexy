# Ilhas e hidratação

## Definição

Uma ilha é um componente cliente - React, Vue, Svelte, Solid ou Preact - importado para uma página `.nexy`. O servidor renderiza seu HTML; o navegador torna esse componente interativo. O resto da página permanece HTML.

As ilhas existem no modo servidor. No modo cliente os componentes *são* as páginas: veja [CSR](csr.md).

## Como funciona

<!-- router:fbr,custom -->
```nexy filename="src/rotas/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter directive="client:visible" />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Static heading</h1>
<Counter directive="client:visible" />
```
<!-- /router -->

Nexy renderiza o componente em tempo de construção, armazena seu HTML e o coloca dentro da página. A resposta da página carrega esse HTML mais os adereços como um atributo JSON. No navegador, o tempo de execução da ilha carrega o componente e assume o controle do contêiner.

`directive` decide **quando** isso acontece. Sem ele, a ilha hidrata assim que seu tempo de execução estiver pronto.

## Ciclo de vida de renderização

1. Na construção, cada componente do cliente é renderizado em HTML e escrito em `__nexy__/client/static/`.
2. Uma solicitação renderiza a página `.nexy`; o HTML da ilha é inserido no lugar da tag.
3. A resposta carrega o HTML, os adereços e a diretiva como atributos.
4. No navegador, o runtime agenda a hidratação de acordo com a diretiva.
5. A hidratação substitui o HTML estático pelo componente ativo; o resto da página permanece intacto.

No desenvolvimento não há build snapshot: o contêiner está vazio e o componente é renderizado no navegador. A página parece a mesma, mas a primeira pintura difere da produção.

## Quando usar

- Uma página que contém principalmente conteúdo e possui um ou dois pontos interativos.
- Um widget que deve existir no HTML para crawlers e ainda funcionar.
- Um componente que precisa do navegador, mas não deve arrastar a página inteira para a renderização do cliente.

## Configuração

| Diretiva | Hidrata |
|---|---|
| nenhum, ou `client:load` | imediatamente |
| `client:idle` | quando o navegador está ocioso (`requestIdleCallback`, tempo limite de 2 s) |
| `client:visible` | quando a ilha entra na janela de visualização, 200 px antes |
| `client:media` | quando uma consulta de mídia corresponde; configure-o com a propriedade `media` |

```nexy
<Chart directive="client:media" media="(min-width: 768px)" />
```

`client:media` padrão é `(min-width: 768px)` quando `media` está ausente e hidrata uma vez. Em um navegador sem `IntersectionObserver`, `client:visible` volta ao modo inativo.

`directive` e `media` são consumidos pelo Nexy: eles não são passados ​​para o seu componente.

## Exemplo

```tsx filename="src/componentes/Counter.tsx"
import { useState } from "react"

export default function Counter({ start = 0 }: { start?: number }) {
  const [count, setCount] = useState(start)
  return <button onClick={() => setCount(count + 1)}>{count}</button>
}
```

<!-- router:fbr,custom -->
```nexy filename="src/rotas/index.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Count</h1>
<Counter start=3 directive="client:idle" />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Counter.tsx" import Counter
---
<h1>Count</h1>
<Counter start=3 directive="client:idle" />
```
<!-- /router -->

## Limitações

- **`client:only` nunca hidrata.** É aceito, mas o tempo de execução o ignora, então o HTML do servidor permanece inerte. Use uma rota de cliente ([CSR](csr.md)) quando um componente não puder ser renderizado no servidor.
- **`client:manual` não tem gatilho público.** Ele também é ignorado automaticamente e o identificador que o retoma é interno.
- **Props devem ser JSON.** Eles são serializados com `json.dumps`; um valor que não pode ser serializado é eliminado e a ilha recebe `{}` - silenciosamente.
- **Uma ilha não é um componente cliente com estado compartilhado.** Duas ilhas não compartilham estado sem um mecanismo que você mesmo adiciona.
- **A ilha não é renderizada novamente pelo servidor.** Seu HTML é o instantâneo da construção, além de tudo o que o componente faz depois de hidratado.
- **Uma página de ilhas é uma página CSR disfarçada.** Se cada bloco precisar se comunicar entre si, escolha o modo cliente.

## Próximas etapas

- [Renderização](README.md): os quatro modos
- [Componentes](../views/nexy/components.md): como uma página `.nexy` importa uma
- [React](../views/react/differences.md), [Vue](../views/vue/differences.md), [Svelte](../views/svelte/differences.md), [Solid](../views/solid/differences.md), [Preact](../views/preact/differences.md)
