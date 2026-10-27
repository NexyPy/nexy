---
name: nexy-styling
description: Styling a Nexy project in the style mode it was created with - Tailwind utilities, UnoCSS utilities or plain CSS - with design tokens in src/globale.css. Load it before writing any class name or stylesheet.
---

# Styling

## Follow the mode of the project

Find it before writing a class: look for `tailwindcss` or `unocss` in `package.json`, and for
`@import "tailwindcss"` or `uno.config.ts`.

| Mode | How to style |
|---|---|
| Tailwind | utility classes in the markup. No hand-written component CSS beyond tokens and base |
| UnoCSS | utility classes in the markup (the Wind preset, same names as Tailwind). Tokens in `uno.config.ts` |
| Plain CSS | semantic class names and CSS in `src/globale.css` or the component's `<style>` |

Never mix modes in one project: no `@apply` walls in a utility project, no utility classes in a
plain-CSS project.

## Tokens live in `src/globale.css`

Colours, fonts and the dark theme are CSS variables, and the utilities read them. Add or change a
token there, once. Do not hard-code a hex value in a component.

```css
:root {
  color-scheme: light;
  --background: light-dark(#ffffff, #0a0a0a);
  --foreground: light-dark(#0a0a0a, #fafafa);
}
.dark { color-scheme: dark; }
```

The dark theme is the `dark` class on `<html>`. A utility project maps tokens to names in its
config (`bg-background`, `text-foreground`).

## Writing rules

- Arbitrary gradient values need their type or Uno reads them as a colour:
  `bg-[image:linear-gradient(...)]`.
- Write class names in full (`md:grid-cols-3`), never assembled from fragments: the generator can
  only see what is written.
- Repeated class lists become a **component**, not a copied string and not a global class.
- Dark and light share the markup; differences come from tokens or `dark:` variants.
- Respect `prefers-reduced-motion`: use `motion-safe:` for animation.
- Focus is visible. Contrast meets WCAG AA.
- Pick a type scale and a spacing rhythm once and reuse them across pages.

## Icons and images

Icons are SVG components or files in `public/`, coloured with `currentColor`. Never an emoji, a
symbol character or an icon font for one glyph.

Run [nexy-ux-audit](../nexy-ux-audit/SKILL.md) before designing a view.
