---
title: Dark mode without a flash
date: 2026-11-16
summary: The page knows its theme before it paints. A few lines in the head, a class on the html element, and colours that follow it.
tags: css, html
---

A page that turns dark after it loads shows a white flash first. This blog avoids it by deciding
the theme before the browser paints anything.

## Decide in the head

The layout puts a short script at the top of `<head>`, before the stylesheet. It reads the choice
saved in `localStorage` and, when there is none, the preference of the system. In short:

```js
var saved = localStorage.getItem("nexy-theme");
var dark = saved ? saved === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
document.documentElement.classList.toggle("dark", dark);
```

The script runs while the document is still being read, so the first paint already has the right
class.

## Colours that follow

The stylesheet names each colour once with `light-dark()`, and the class sets `color-scheme`:

```css
:root {
  --background: light-dark(#fafafa, #0e0e10);
}
.dark {
  color-scheme: dark;
}
```

The browser picks the second value of every `light-dark()` when the scheme is dark. Form fields
and scroll bars follow too, with no extra rule.

## The switch

The button in the header is a switch for screen readers: `role="switch"` with `aria-checked`. A
click flips the class, saves the choice, and a change made in another tab is picked up through the
`storage` event. A reader who never touches it gets the theme of the system, and keeps following
it when the system changes at sunset.
