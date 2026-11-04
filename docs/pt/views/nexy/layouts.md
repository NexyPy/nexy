# layout.nexy

O arquivo de layout do modo servidor (`useCSR = False`). O root possui o documento HTML.

## Layout raiz

```nexy filename="src/rotas/layout.nexy"
---
from nexy import Vite

children: prop[NexyElement]
---
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>My app</title>
  <Vite />
</head>
<body>
  <main>{{ children | safe }}</main>
</body>
</html>
```

- `<!DOCTYPE html>`, `<html>`, `<head>` e `<body>` moram aqui e em nenhum outro lugar.
- `<Vite />` injeta os scripts e estilos do cliente uma vez, no `<head>`.
- `{{ children | safe }}` é onde a página ou o próximo layout aninhado é renderizado.

## Layouts aninhados

Um `layout.nexy` em um subdiretório envolve essa subárvore e é renderizado dentro de seu pai. Não se repete
as tags do documento:

```nexy filename="src/routes/blog/layout.nexy"
---
children: prop[NexyElement]
---
<nav>...</nav>
<article>{{ children | safe }}</article>
```

`blog/[slug].nexy` é renderizado como `layout.nexy > blog/layout.nexy > page`.

## Componentes e ilhas

Um layout pode importar `.nexy` componentes (um cabeçalho, um rodapé) e componentes do cliente. Um cliente
componente em um layout é uma [ilha](../../rendering/islands.md) como qualquer outra:

```nexy
---
from "@/components/Header.nexy" import Header
from "@/components/theme/theme.tsx" import Theme
---
<Header />
<Theme directive="client:idle" />
```

## Sem layout

Um projeto sem `layout.nexy` ainda responde com um documento válido: Nexy volta ao mínimo
shell com `<!DOCTYPE html>`, a meta da janela de visualização e as tags Vite. Adicione um layout assim que precisar
um título, fontes ou navegação.

## No roteador modular

Os controladores escolhem suas visualizações, então eles próprios compõem o layout:

```python
return useViews("src/apps/layout.nexy", context={"children": useViews("src/apps/app_view.nexy")})
```

## O que não pode fazer

- Não pode coexistir com `layout.tsx`, `layout.vue` ou `layout.svelte`: um projeto em modo servidor tem
  nenhuma rota de cliente ([modos](../../routing/fbr/modes.md)).
- Não roda no cliente: use uma ilha para interatividade.

## Próximas etapas

- [Layouts](../../routing/fbr/layouts/README.md)
- [Herança](../../routing/fbr/inheritance.md)
- [.arquivos .nexy](README.md)