# Dynamic routes

A path segment written in square brackets matches any value and hands it to the page or handler.

## Dynamic segments

`blog/[slug].nexy` serves `/blog/{slug}`. In a page, declare the segment as a property; in a Python
handler, take it as an argument.

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

## Typed segments

The annotation decides the type.

| Where | Conversion |
|---|---|
| `.py` handler | any FastAPI type annotation (`int`, `UUID`, `Enum`...) |
| `.nexy` page | `int` and `float` are converted; everything else stays a string |

A value that does not match the annotation is **not found**: `/api/users/abc` answers `404`, because
a dynamic route captures any URL and a URL that cannot be converted simply does not exist. See
[Validation and errors](../handlers/validation-and-errors.md).

## Catch-all segments

`docs/[...path].nexy` serves `/docs/{path:path}`. The remaining segments arrive as one string,
slashes included.

```nexy filename="src/routes/docs/[...path].nexy"
---
path: prop[str]
---
<pre>{{ path }}</pre>
```

`/docs/a/b/c` gives `path == "a/b/c"`.

## Route groups

A directory in parentheses organises files without appearing in the URL. It still takes part in
[inheritance](../inheritance.md): its `layout.*` and `dependencies.py` apply to what is inside.

```text
src/routes/
├─ (marketing)/
│  ├─ layout.nexy        applies to the pages in the group
│  ├─ pricing.nexy       /pricing
│  └─ about.nexy         /about
└─ (app)/
   └─ dashboard.nexy     /dashboard
```

Use groups to give different sections different layouts without changing their URLs.

## Priority

Static routes win over dynamic ones, and dynamic ones over catch-alls:
`/blog/new` matches `blog/new.nexy` before `blog/[slug].nexy`.

## One file per URL

Two files that resolve to the same URL both register. Do not put `blog.nexy` next to
`blog/index.nexy`, or mix `index.nexy` and `index.py` for the same path.

## Next steps

- [Pages](README.md)
- [Error pages](../errors/README.md)
- [File conventions](../../../reference/file-conventions.md)
