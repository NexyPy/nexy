---
name: nexy-svelte
description: Writing Svelte 5 components, routes and layouts in a Nexy project in idiomatic Svelte - runes, snippets, never hand-written DOM scripts. Load it for any .svelte file when useFF = svelte().
---

# Svelte in Nexy

## Idiomatic Svelte 5 only

Use runes.

- State: `$state`. Derived: `$derived`. Side effects: `$effect`. Props: `let { title } = $props()`.
- Children are snippets: `{@render children?.()}`. Events are plain attributes: `onclick={...}`.
- Template blocks (`{#if}`, `{#each items as item (item.id)}`, `{#await}`), not DOM calls. No
  `document.querySelector`, no document-level listeners, no `innerHTML`; use `{@html}` only for
  trusted content and `bind:this` when the DOM is truly needed.
- Shared logic goes in `.svelte.ts` modules that export functions using runes.

The one allowed script is a short one in the layout head that sets the saved theme class on
`<html>` before the first paint.

```svelte
<script lang="ts">
  let count = $state(0);
</script>

<button type="button" onclick={() => count++}>Clicked {count} times</button>
```

## Files

- `src/routes/*.svelte`: pages. `src/components/*.svelte`: components, never inside `src/routes/`.
- `src/routes/layout.svelte`: the root one owns the document and renders its page with
  `{@render children?.()}`.

## Rules

- One component per file. Styles in a `<style>` block are scoped by Svelte; keep them for what the
  project's styling mode cannot express ([nexy-styling](../nexy-styling/SKILL.md)).
- Buttons are `<button type="button">`; navigation is a link. Labels on every field.
- Import with `@/`. Server calls: `useAction` from `@nexy/client` is a store (`$save.pending`,
  `$save.data`, `$save.error`, `save.run(input)`).
- Icons are SVG components. No emoji.
- Inside a `.nexy` template, wrap Svelte's `{ }` blocks in `{% raw %}...{% endraw %}`.

Run [nexy-ux-audit](../nexy-ux-audit/SKILL.md) before building a view, and test first
([nexy-testing](../nexy-testing/SKILL.md)).
