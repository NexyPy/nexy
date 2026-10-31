# Vue: actions and navigation

What `@nexy/client` gives a Vue component: call a Python function, link pages, read and change the
URL. The same module serves pages (client mode) and islands (server mode). Everything that changes
is a ref: read it with `.value` in `<script setup>`, without it in the template.

## Actions

An action is a Python function marked `@Action`. Nexy writes a typed client for it in
`@nexy/actions`, and `useAction` tracks one call:

```python filename="src/actions/todos.py"
from pydantic import BaseModel

from nexy.decorators import Action, revalidate


class Todo(BaseModel):
    title: str


@Action
async def add_todo(title: str) -> Todo:
    revalidate()
    return Todo(title=title)
```

```vue filename="src/components/AddTodo.vue"
<script setup lang="ts">
import { ref } from "vue";
import { ActionError, useAction } from "@nexy/client";
import { add_todo } from "@nexy/actions";

const title = ref("");
const { run, pending, error, data } = useAction(add_todo, {
  onSuccess: () => (title.value = ""),
});
</script>

<template>
  <form @submit.prevent="run({ title })">
    <input v-model="title" />
    <button :disabled="pending">Add</button>
    <p v-if="error" role="alert">
      {{ error instanceof ActionError ? error.fields.title ?? error.message : "Network error" }}
    </p>
    <p v-if="data">Added {{ data.title }}</p>
  </form>
</template>
```

| Field | Meaning |
|---|---|
| `run(input)` | Calls the action. It never throws: a failure lands in `error`, and `run` resolves with `undefined`. |
| `pending` | Computed ref, `true` while the call runs. |
| `data` | Computed ref, the result of the last successful call. |
| `error` | Computed ref. An `ActionError` when the server answered an error: `status`, `detail`, and `fields` (field name to message) for a `422`. A plain `Error` when the request never arrived. |
| `reset()` | Back to the initial state; a call still running no longer updates it. |

Only the latest call updates the state. Without the hook an action is an `async` function:
`await add_todo({ title: "Milk" })`, which throws on failure.

`revalidate()` in the action asks the browser to refresh the open page: the client router re-renders
it in client mode, the browser reloads it in server mode. See [Actions](../../guides/actions.md) for
forms without JavaScript, types and security.

## Link

```vue
<script setup lang="ts">
import { Link } from "@nexy/client";
</script>

<template>
  <Link href="/todos" active-class="active">Todos</Link>
</template>
```

| Prop | Meaning |
|---|---|
| `href` | A route of the project; a typo is a type error. A `?query`, a `#fragment` or an external URL also work. |
| `replace` | Replace the history entry instead of adding one. |
| `scroll` | `false` keeps the scroll position. |
| `prefetch` | `'intent'` (default) on hover, focus or touch; `'viewport'` when visible; `false` never. |
| `activeClass` | Added while the link points at the current page or a page below it. `activeClassName` is the same. |
| `exact` | Active only on the exact page. |

The content goes in the default slot. The current link also gets `aria-current="page"`, and every
other attribute and listener reaches the `<a>`. In client mode a plain `<a href="/todos">` navigates
on the client too; `Link` adds the checked `href`, the prefetch and the active class.

## Image

```vue
<Image src="/hero.jpg" alt="The team" :width="1200" :height="600" priority />
```

Lazy by default, no layout shift when `width` and `height` are set, `priority` for the image visible
on arrival, `fill` to cover a positioned parent. `alt` is required (`alt=""` for decoration).

## Read the URL

| Hook | Returns |
|---|---|
| `usePathname()` | computed ref, `"/todos/42"` |
| `useParams<T>()` | computed ref, the dynamic segments `{ id: "42" }` |
| `useSearchParams()` | computed ref, a `URLSearchParams` |
| `useLocation()` | ref, `{ pathname, search, hash, params }` |
| `useMatch(path?)` | computed ref `{ match, found }`: which route answers `path`, the current one by default |

```vue
<script setup lang="ts">
import { useSearchParams } from "@nexy/client";

const query = useSearchParams();
</script>

<template>
  <p>Filter: {{ query.get("filter") ?? "all" }}</p>
</template>
```

Call the hooks in `setup`: they stop listening when the component unmounts. On the server they answer
with the URL of the request. They follow the client router, so in an island pass the values from the
page as props instead.

## Change the URL

```ts
import { useRouter } from "@nexy/client";

const router = useRouter();
router.push("/todos?filter=done", { scroll: false });
```

`push`, `replace`, `back`, `forward`, `refresh` and `prefetch(href)`.

### Keep the visitor on a page

```vue
<script setup lang="ts">
import { ref } from "vue";
import { useBlocker } from "@nexy/client";

const dirty = ref(false);
useBlocker(() => (dirty.value && !window.confirm("Leave without saving?") ? "unsaved" : undefined));
</script>
```

A blocker runs before every client navigation, until the component unmounts. Returning a string, or a
promise of one, cancels the navigation; anything else lets it through. Nexy asks nothing itself, so
the blocker shows the question. It does not stop a reload or a link to another site.

## Next steps

- [Actions](../../guides/actions.md): forms, types, errors, security
- [Linking and navigating](../../routing/fbr/navigation/linking-and-navigating.md): what the router does
- [Testing](../../guides/testing.md): test actions with pytest
