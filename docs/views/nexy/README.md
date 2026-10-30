# .nexy files

A `.nexy` file is a component: Python on top, HTML in the middle, CSS at the bottom.

**Before you start:** a project created by the [Quick start](../../getting-started/quick-start.md).
A `.nexy` file needs no build configuration: `nx dev` compiles it on save.

```nexy filename="src/routes/blog/[slug].nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```

## Frontmatter

Everything between the two `---` lines is Python. Imports are resolved when the component is
compiled; the rest runs for every request, so it can read request state.

| What | Example |
|---|---|
| Import a module | `import json`, `from datetime import datetime` |
| Import a component | `from "@/components/card.nexy" import Card` |
| Declare a property | `title: prop[str] = "Default"` |
| Compute a value | `year = datetime.now().year` |
| Read the request | `pathname = usePathname()` |
| Cache the page (ISR) | `revalidate = 60` |

## Properties

Properties are the component's API. `prop[type]` declares the type, `= value` gives a default. A
property without a default must be passed by the parent.

Imports that start with an alias are resolved through `useAliases`. The setup `nx new` writes maps
`@` to `src`, which makes `@/components/card.nexy` mean `src/components/card.nexy`.

## Template

Below the frontmatter is HTML with Jinja2. Variables from the frontmatter and the properties are in
scope.

```html
{% for item in items %}
  <li>{{ item.name }}</li>
{% endfor %}

{% if user %}
  <p>Welcome, {{ user.name }}</p>
{% endif %}
```

Autoescaping is **off**: templates are the project's own HTML, so `{{ value }}` is inserted as
written. Escape untrusted values yourself with `{{ value | e }}`. `| safe` therefore changes nothing.

> [!NOTE]
> wrap JavaScript that contains `{{` or `{%` in `{% raw %}...{% endraw %}`.
> Frameworks such as Vue and Svelte use the same braces.

## Components

Any imported callable whose name starts with an uppercase letter can be used as a tag. The compiler
rewrites it to a Jinja call: attributes become keyword arguments.

```nexy filename="src/routes/index.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```

The last line is exactly `{{ Audio("/theme.mp3", controls=True) }}`. Both syntaxes are valid for the
built-in `Image`, `Link`, `Audio` and `Video` helpers - see
[components](components.md#two-syntaxes-one-function).

Children are rendered through `<Slot />` (capital S) inside the child component, and through `{{ children }}`
inside a layout.

Pass a computed value with Jinja inside the attribute: `<Icon path="{{ icon }}" size="{{ size }}" />`.
A bare name such as `path=icon` is the text `icon`, not the variable. To give a component a CSS
class, declare a `class_name` prop: `class` is a Python keyword.

> [!NOTE]
> a helper tag is always self-closing. Passing content to `Link` goes through its
> `children` argument (`<Link href="/about" children="About" />`), not through element content.

## Styles

`<style>` blocks are emitted with the page that declares them. They are not scoped: a class name
used in two components is one class. Prefix or namespace your classes.

## Rules that save time

- One component per file. The file name is the component name, in PascalCase (`CopyChip.nexy`). A
  `.nexy` component is imported as a Python module: a hyphen in the name (`copy-chip.nexy`) does not
  compile.
- Declare props before using them: an undeclared variable renders as an empty string, because
  Jinja2's undefined is silent here.
- Keep side effects inside functions - the frontmatter runs again on every request.

## Next steps

- [Markdown and MDX](markdown.md): content pages
- [ISR](../../rendering/isr.md): cache a page per path
- [CSR](../../rendering/csr.md): client-side rendering
