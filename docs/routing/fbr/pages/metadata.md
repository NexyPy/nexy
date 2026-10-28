# Page metadata

A page names its title and its head tags, and the root layout writes them once.

## Say it in the page

For a page that never changes, write a literal at the top of the frontmatter:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

When the title depends on the data, call `setMetadata` instead:

```nexy filename="src/routes/posts/[slug].nexy"
---
from nexy import notFound, setMetadata

from src.posts import find

slug: prop[str]
post = find(slug) or notFound()
setMetadata(title=post.title, description=post.summary, og={"image": post.cover})
---
<h1>{{ post.title }}</h1>
```

A modular controller calls `setMetadata(...)` before it returns `useViews(...)`.

## Write it in the layout

The root layout owns the `<head>`. One line writes what the page said, escaped:

```nexy filename="src/routes/layout.nexy"
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

A page runs before its layouts, so the layout finds what the page asked for. A page that says
nothing gets the `useTitle` of your `nexyconfig.py`, and no other tag.

## The fields

| Field | Written as |
|---|---|
| `title` | `<title>`; with `title_template="%s \| My site"` the title is put in the `%s` |
| `description` | `<meta name="description">` |
| `canonical` | `<link rel="canonical">` |
| `robots` | `<meta name="robots">`, for example `"noindex"` |
| `icon` | `<link rel="icon">` |
| `og` | one `<meta property="og:...">` per key: `{"image": "/cover.png"}` gives `og:image` |
| `twitter` | one `<meta name="twitter:...">` per key |
| `extra` | a list of attribute dicts, one `<meta>` each: `[{"name": "theme-color", "content": "#fff"}]` |

A later call replaces a value; `og`, `twitter` and `extra` add to what is there. A field that does
not exist raises `TypeError`, so a typo does not silently do nothing.

## Safe by default

Every value is HTML-escaped, so a title built from a URL or from the database cannot close the tag
and inject a script. A value is escaped once, when the layout calls `html()`: do not escape it
yourself.

## Next steps

- [Pages](README.md)
- [Layouts](../layouts/README.md)
- [Error pages](../errors/README.md)
