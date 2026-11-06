# Layouts de front-end

Um **Layout** é um wrapper que define a estrutura compartilhada em torno de uma ou mais páginas. Os layouts permitem a experiência "semelhante a um aplicativo", preservando o estado e evitando recarregamentos de página inteira durante a navegação.

## Lógica de aninhamento

Os layouts seguem uma estrutura hierárquica baseada na árvore de diretórios em `src/routes/`.

1.  **Layout raiz**: Todo projeto possui um layout raiz (por exemplo, `src/routes/layout.nexy`). Este é o único layout responsável por definir o shell do documento: `<html>`, `<head>` e `<body>`.
2.  **Layouts aninhados**: Qualquer pasta pode conter seu próprio arquivo `layout.*`. Este layout envolve todas as páginas e sublayouts dessa pasta.
3.  **Herança**: Uma página é agrupada por todos os layouts desde a raiz até sua própria pasta.

```text
src/routes/
├─ layout.tsx            root: <html>, <head>, <body>
├─ index.tsx             root > page
└─ dashboard/
   ├─ layout.tsx         nested: the dashboard menu
   └─ settings.tsx       root > dashboard > page
```

Um layout aninhado desenha apenas sua parte da UI e coloca a página onde `children` vai:

```tsx filename="src/rotas/dashboard/layout.tsx"
import type { ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  return (
    <div className="dashboard">
      <nav>Dashboard</nav>
      <main>{children}</main>
    </div>
  );
}
```

## Estado e composição compartilhados

Os layouts são projetados para serem estáveis. No modo cliente, ao navegar entre duas páginas que compartilham o mesmo layout, o layout **não** é renderizado novamente; apenas o conteúdo filho muda. No modo servidor cada navegação é um novo documento.

- **Slots**: Layouts fornecem um slot onde a página aninhada é injetada: `children` em JSX, e a propriedade `children` em um layout `.nexy`.
- **Preservação de Estado**: Como o layout permanece montado, qualquer estado contido nele (por exemplo, uma consulta de pesquisa em um cabeçalho) é preservado durante a navegação.

O mesmo slot em um layout `.nexy`:

```nexy filename="src/rotas/layout.nexy"
---
children: prop[NexyElement]
---
<!DOCTYPE html>
<html>
  <body>{{ children }}</body>
</html>
```

O campo de pesquisa abaixo mantém o que o usuário digitou enquanto ele se move entre as páginas do painel, pois o layout que o contém nunca é desmontado:

```tsx filename="src/rotas/dashboard/layout.tsx"
import { useState, type ReactNode } from "react";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const [query, setQuery] = useState("");
  return (
    <>
      <input value={query} onChange={(event) => setQuery(event.target.value)} />
      {children}
    </>
  );
}
```

## Restrições estáticas

Para rotas pré-renderizadas (SSG), o layout raiz não pode depender de dados de horário de solicitação, como cookies ou cabeçalhos. Deve ser representável como uma concha estática que o cliente hidrata.

Leia o tema no navegador, em um script do shell estático:

```tsx filename="src/routes/layout.tsx"
import type { ReactNode } from "react";

const theme = `document.documentElement.dataset.theme =
  localStorage.getItem("theme") ?? "light";`;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html>
      <head>
        <script dangerouslySetInnerHTML={{ __html: theme }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## Implementação da Estrutura

A implementação de slots e aninhamento varia ligeiramente de acordo com a estrutura. Consulte o guia **Diferenças** da tecnologia escolhida:

- [React Diferenças](../react/differences.md)
- [Vue Diferenças](../vue/differences.md)
- [Svelte Diferenças](../svelte/differences.md)
- [Solid Diferenças](../solid/differences.md)
- [Preact Diferenças](../preact/differences.md)
