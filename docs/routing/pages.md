# Pages

A page file returns HTML. Which file type you use changes how it is produced: see
[views](../views/README.md). This page covers the routing rules that apply to every page format.

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
async def GET(request, id: int):
    return {"id": id}
```

FastAPI validates the value against the annotation in a `.py` handler and returns `422` when it does
not match.

> **Good to know**: in a `.nexy` page only `int` and `float` annotations are converted. Every other
> segment arrives as a string.

## Catch-all segments

`docs/[...path].nexy` serves `/docs/{path:path}`. The remaining segments arrive as one string,
slashes included.

```nexy filename="src/routes/docs/[...path].nexy"
---
path: prop[str]
---
<pre>{{ path }}</pre>
```

## Layouts

`layout.nexy` wraps every page in its directory. A page at `blog/[slug].nexy` renders inside
`blog/layout.nexy`, which renders inside the root `layout.nexy`. The layout receives the page as
`children`:

```nexy filename="src/routes/blog/layout.nexy"
---
children: prop[str]
---
<header>...</header>
<main>{{ children }}</main>
<footer>...</footer>
```

The root `layout.nexy` owns `<!DOCTYPE html>`, `<html>`, `<head>` and `<body>`. With React or
Preact, a `layout.tsx` also wraps the pages below it. See [Layouts](layouts.md).

## Error pages

| File | Answers |
|---|---|
| `notfound.nexy` | `404` for its directory |
| `errors.nexy` | `500` for its directory |

Both are only installed when a copy exists at the routes root; a copy in a subdirectory then refines
the page for that prefix.

The `500` handler catches every unhandled exception, API handlers included, and answers with HTML.

## Shared dependencies

`dependencies.py` follows the same directory hierarchy: a dependency declared there applies to that
directory and its children.

```python filename="src/routes/admin/dependencies.py"
from fastapi import Depends


async def current_user() -> str:
    return "user"


def get_user(user: str = Depends(current_user)) -> str:
    return user
```

## Loading

`loading.nexy` is reserved: it is excluded from routes, but it has no runtime effect yet.

## Next steps

- [Hooks](hooks.md): read the request from inside the page
- [Modular routing](modular.md): controllers instead of files
- [SSR](fbr/ssr.md): the default rendering mode
