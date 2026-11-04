# Layouts de front-end

Um **Layout** é um wrapper que define a estrutura compartilhada em torno de uma ou mais páginas. Os layouts permitem a experiência "semelhante a um aplicativo", preservando o estado e evitando recarregamentos de página inteira durante a navegação.

## Lógica de aninhamento

Os layouts seguem uma estrutura hierárquica baseada na árvore de diretórios em `src/routes/`.

1.  **Layout raiz**: Todo projeto tem um layout raiz (por exemplo, `src/routes/layout.nexy`). Este é o único layout responsável por definir o shell do documento: `<html>`, `<head>` e `<body>`.
2.  **Layouts aninhados**: Qualquer pasta pode conter seu próprio arquivo `layout.*`. Este layout envolve todas as páginas e sublayouts dessa pasta.
3.  **Herança**: Uma página é agrupada por todos os layouts desde a raiz até sua própria pasta.

## Estado e composição compartilhados

Os layouts são projetados para serem estáveis. Ao navegar entre duas páginas que compartilham o mesmo layout, o layout **não** é renderizado novamente; apenas o conteúdo filho muda.

- **Slots**: Os layouts fornecem um "slot" (geralmente `children` em JSX ou `{{ content }}` em Jinja2) onde a página aninhada é injetada.
- **Preservação de Estado**: Como o layout permanece montado, qualquer estado contido nele (por exemplo, uma consulta de pesquisa em um cabeçalho) é preservado durante a navegação.

## Restrições estáticas

Para rotas pré-renderizadas (SSG), o layout raiz não pode depender de dados de horário de solicitação, como cookies ou cabeçalhos. Deve ser representável como uma concha estática que o cliente hidrata.

## Implementação da Estrutura

A implementação de slots e aninhamento varia ligeiramente de acordo com a estrutura. Consulte o guia **Diferenças** da tecnologia escolhida:

- [Reagir diferenças](../react/differences.md)
- [Diferenças de Vue](../vue/differences.md)
- [Diferenças esbeltas](../svelte/differences.md)
- [Diferenças sólidas](../solid/differences.md)
- [Pré-agir diferenças](../preact/differences.md)