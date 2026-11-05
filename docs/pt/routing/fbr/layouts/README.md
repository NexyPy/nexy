# Layouts

Um layout envolve cada página abaixo de seu diretório. Ninho de layouts: a página é renderizada dentro do layout de seu diretório, que é renderizado dentro do layout do diretório pai, até o layout raiz.

Há uma página por tipo de arquivo de layout:

| Arquivo | Modo | Possui o documento HTML | Página |
|---|---|---|---|
| `layout.nexy` | servidor (`useCSR = False`) | sim, na raiz | [layout.nexy](../../../views/nexy/layouts.md) |
| `layout.tsx` | cliente (`useCSR = True`) | sim, na raiz (React, Solid, Preact) | [React](../../../views/react/differences.md), [Solid](../../../views/solid/differences.md), [Preact](../../../views/preact/differences.md) |
| `layout.vue` | cliente | sim, na raiz | [layout.vue](../../../views/vue/differences.md) |
| `layout.svelte` | cliente | sim, na raiz | [layout.svelte](../../../views/svelte/differences.md) |

Um projeto usa uma família. `layout.nexy` e `layout.tsx` não podem residir no mesmo projeto: o modo servidor possui layouts `.nexy` e o modo cliente possui layouts de estrutura. Consulte [Modo servidor e modo cliente](../modes.md).

## Como o navegador assume o controle do documento

No modo cliente, o Nexy renderiza o layout raiz no Node, então a primeira resposta é um documento completo. O navegador então assume o controle de uma das duas maneiras:

| Estrutura | Aquisição | O que significa |
|---|---|---|
| React, Solid | **hidratação** de todo o documento | o HTML do servidor é reutilizado como está |
| Preact, Vue, Svelte | **body takeover** | o framework constrói o corpo da página e o troca por aquele que o servidor enviou |

Preact, Vue e Svelte não podem hidratar um documento inteiro: Preact `hydrate` constrói um segundo elemento `<html>`, o compilador de Vue descarta um `<script>` de um modelo de cliente e Svelte não pode criar `<html>`, `<head>` ou `<body>` no navegador. Então para eles `<html>`, `<head>` e os atributos `<body>` são os que o servidor enviou, e apenas o corpo é construído pelo navegador. Na prática:

- Coloque o título, meta tags, fontes e script do tema no layout raiz: eles são renderizados pelo servidor e permanecem como estão.
- Uma ligação em `<html>`, `<head>` ou `<body>` (por exemplo, uma classe reativa) é aplicada pelo servidor, mas não é atualizada no navegador. Altere-os a partir de um script, como faz o script do tema.
- O navegador renderiza o corpo do zero em vez de reutilizar a marcação do servidor, então o corpo é substituído uma vez, na mesma tarefa da primeira renderização.

## O layout raiz

O layout raiz é `src/routes/layout.<ext>`. É criado por `nx new` e é o único lugar que escreve `<!DOCTYPE html>`, `<html>`, `<head>` e `<body>` (todos os frameworks e `.nexy`). Páginas e layouts aninhados nunca os repetem.

```text
src/routes/
├─ layout.*              root: the document
├─ index.*
└─ dashboard/
   ├─ layout.*           nested: UI only
   ├─ index.*
   └─ settings.*
```

`dashboard/index` é renderizado como `root layout > dashboard layout > page`.

## Grupos de rotas

Um diretório entre parênteses pode ter seu próprio layout sem alterar URLs:

```text
src/routes/
├─ layout.nexy
├─ (marketing)/
│  ├─ layout.nexy        wraps /pricing and /about only
│  ├─ pricing.nexy
│  └─ about.nexy
└─ (app)/
   └─ dashboard.nexy     only the root layout
```

## Persistência

No modo cliente um layout permanece montado enquanto o usuário navega entre as páginas que o compartilham: seu DOM, estado e posição de rolagem são mantidos. No modo servidor cada navegação é um novo documento.

## Próximas etapas

- [layout.nexy](../../../views/nexy/layouts.md)
- [layout.tsx](../../../views/react/differences.md)
- [Herança](../inheritance.md)
