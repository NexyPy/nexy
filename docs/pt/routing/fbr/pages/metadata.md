# Metadados da página

Uma página nomeia seu título e suas tags de cabeçalho, e o layout raiz os escreve uma vez.

## Diga na página

Para uma página que nunca muda, escreva um literal no topo do frontmatter:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

Quando o título depender dos dados, chame `setMetadata`:

```nexy filename="src/rotas/posts/[slug].nexy"
---
from nexy import notFound, setMetadata

from src.posts import find

slug: prop[str]
post = find(slug) or notFound()
setMetadata(title=post.title, description=post.summary, og={"image": post.cover})
---
<h1>{{ post.title }}</h1>
```

Um controlador modular chama `setMetadata(...)` antes de retornar `useViews(...)`.

## Escreva no layout

O layout raiz possui o `<head>`. Uma linha escreve o que a página disse, escapou:

```nexy filename="src/rotas/layout.nexy"
---
from nexy import setMetadata, useMetadata

children: prop[NexyElement]
setMetadata(title_template="%s | My site")
---
<!DOCTYPE html>
<html>
  <head>
    {{ useMetadata().html() }}
  </head>
  <body>{{ children }}</body>
</html>
```

Uma página é executada antes de seus layouts, para que o layout encontre o que a página solicitou. Uma página que não diz nada recebe o `useTitle` do seu `nexyconfig.py`, e nenhuma outra tag.

## Os campos

| Campo | Escrito como |
|---|---|
| `title` | `<title>`; com `title_template="%s \| My site"` o título é colocado no `%s` |
| `description` | `<meta name="description">` |
| `canonical` | `<link rel="canonical">` |
| `robots` | `<meta name="robots">`, por exemplo `"noindex"` |
| `icon` | `<link rel="icon">` |
| `og` | um `<meta property="og:...">` por chave: `{"image": "/cover.png"}` dá `og:image` |
| `twitter` | um `<meta name="twitter:...">` por chave |
| `extra` | uma lista de dictos de atributos, um `<meta>` cada: `[{"name": "theme-color", "content": "#fff"}]` |

Uma chamada posterior substitui um valor; `og`, `twitter` e `extra` adicionam ao que está lá. Um campo que não existe gera `TypeError`, portanto, um erro de digitação não faz nada silenciosamente.

## Seguro por padrão

Cada valor tem escape de HTML, portanto, um título construído a partir de uma URL ou do banco de dados não pode fechar a tag e injetar um script. Um valor é escapado uma vez, quando o layout chama `html()`: não escape dele você mesmo.

## Próximas etapas

- [Páginas](README.md)
- [Layouts](../layouts/README.md)
- [Páginas de erro](../errors/README.md)
