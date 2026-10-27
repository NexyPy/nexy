# Components

Nexy exports a small set of helpers that return HTML strings. Each one is used two ways in a
`.nexy` template: as a Jinja call, or as an HTML-style tag.

## Two syntaxes, one function

```nexy filename="src/routes/index.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```

Both lines produce the same markup:

```html
<audio preload="metadata" controls><source src="/theme.mp3" type="audio/mp3" /></audio>
```

The compiler rewrites `<Audio ... />` to `{{ Audio(...) }}`, so the tag form is not a second API:
attributes are the function's keyword arguments.

## Rules of the tag form

| In the tag | Becomes |
|---|---|
| `<Audio src="/a.mp3" />` | `Audio(src="/a.mp3")` |
| `controls=True` | `controls=True`, a real boolean |
| `width=640` | `width=640`, a number |
| `src="{{ url }}"` | `src=(url)`, evaluated in Jinja |
| any other `value` | `"value"`, a string |

- The tag must start with an uppercase letter and be imported in the frontmatter; otherwise the
  compiler raises `Missing Import: <Name> used but not declared.`
- The tag form is **self-closing**. `<Audio src="/a.mp3" />` and
  `{{ Audio("/a.mp3") }}` are equivalent; writing children inside a helper tag is not supported.
- A bare HTML attribute is not a boolean here: `controls` becomes `controls=""`, which is falsy.
  Write `controls=True`.

> **Good to know**: `class_name` is the documented keyword for CSS classes. Extra keyword arguments
> become HTML attributes, so `class="nav"` also reaches the output.

## Image

```nexy
---
from nexy import Image
---
{{ Image("/logo.png", alt="Logo", width=128, height=32) }}

<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

`Image(src, alt="", width=None, height=None, loading="lazy", class_name=None, **attrs)` renders an
`<img>` with lazy loading by default.

## Link

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` renders an `<a data-nexy-link>`
handled by the client router. With `prefetch=True`, hovering or touching the link warms the target
through `window.__nexy_prefetch`.

> **Good to know**: the tag form takes the label as `children`, not as element content:
> `<Link href="/about" children="About" />`. To put markup inside a link, use the call form with
> `children=` or a `.nexy` component that renders a `<Slot />`.

## Audio and Video

```nexy
---
from nexy import Audio, Video
---
{{ Audio("/theme.mp3", controls=True) }}
{{ Video("/demo.mp4", width=640, height=360, muted=True, sources=["/demo.webm", "/demo.mp4"]) }}

<Audio src="/theme.mp3" controls=True />
<Video src="/demo.mp4" width=640 height=360 muted=True />
```

`Audio(src, controls=True, autoplay=False, loop=False, muted=False, preload="metadata",
class_name=None, sources=None, **attrs)` and `Video(src, width=None, height=None, ...)` render native
players. `sources` adds `<source>` tags with the MIME type derived from each extension.

## Importing a client component

From a `.nexy` file, import a framework component by path; the compiler mounts it on the client and
passes the attributes as props:

```nexy
---
from "@/components/Counter.tsx" import Counter
---
<Counter start="0" />
```

`Import(path, framework, symbol)` does the same in Python:

```python
from nexy import Import

counter = Import("@/components/Counter.tsx", "react", "Counter")
html = counter(start=0)
```

The same import syntax resolves `.json`, `.css` and image files to their URLs.

## Template and Vite

`Template().render(path, context)` renders a template file (Jinja2, or Markdown rendered to HTML for
`.md` routes). `Template().invalidate(path)` drops it from the cache.

`Vite()` returns the client tags for the current mode: the HMR script in development, the built
client bundle in production. Nexy calls it for every page; you rarely need it directly.

## Not implemented yet

`Form` and `Script` are exported placeholders with no behaviour. Do not rely on them.

## Next steps

- [.nexy files](nexyfile.md): where these helpers are used
- [React](react.md): importing `.tsx` components
- [Frontend](../guides/frontend.md): how client components are bundled
