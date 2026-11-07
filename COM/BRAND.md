# BRAND

Five decisions about how Nexy looks in public, then the looks we refuse and why.

The constraint that produces everything below: we have no illustrator, no photographer and no
design budget. A brand built on drawn assets would be borrowed art standing in for a project that
does not have any. A brand built on type, code and screenshots is one we can make ourselves, every
week, without lying about how big we are.

## 1. The mark is type

The logo is the monogram `nx`, set in the same monospace as the code, and the wordmark `nexy`, set
in the text face. Two letters, no symbol, no orbit, no node, no spark.

```
nx  nexy
```

Reasons it is not a drawing: a symbol needs an idea behind it, and every idea for a Python/JS
framework is taken and forgettable (a snake, a lightning bolt, a hexagon). Type is honest about
being type. It also survives every size: `nx` at 16 px in a favicon, `nx` at 400 px on a card, the
same two letters.

Spacing: `nx` is always lowercase, always monospace, always tight (`letter-spacing: -0.02em`);
`nexy` sits after it with one space of the monospace advance, never a period, never a `™`. The
favicon becomes the monogram on the paper colour, which also removes the borrowed Heroicons path
that ships today.

## 2. Two faces, both free, one of them the reader's

**Text: `system-ui`.** Not Inter. Inter is the typeface of every generated landing page of the last
three years, it is a 300 kB download, and it looks like the machine the reader is *not* using. The
system stack renders in the reader's own UI font: SF on macOS and iOS, Segoe on Windows, Roboto on
Android, Ubuntu or Cantarell on Linux. The page then looks like it belongs to the operating system
it is open on, which is the only sense in which a web page can look native.

**Code: one monospace, vendored.** JetBrains Mono (OFL 1.1), served from our own origin, subset to
Latin plus the punctuation code actually uses. One file, no CDN, no `@import`, no third party
watching a docs page. Geist Mono is refused for the same reason as Inter: it is the house style of
another company's landing pages.

Until the font is vendored, the card generator in `scripts/make_com_cards.py` draws with DejaVu Sans
and DejaVu Sans Mono, which every Linux machine has. That is a known gap, not a decision: the cards
are regenerated once the faces are in the repository.

## 3. One accent, four neutrals

| token | value | used for |
|---|---|---|
| `paper` | `#fafafa` | page and card background |
| `ink` | `#0a0a0a` | text, and the background of the dark cards |
| `muted` | `#52525b` | secondary text, captions, metadata |
| `line` | `#e4e4e7` | 1 px borders, table rules, dividers |
| `accent` | `#0f766e` | links, one word per card, the caret in a terminal |
| `accent-lit` | `#5eead4` | the accent on a dark card, where teal-700 has no contrast |

That is the whole palette. No second accent, no "success green" next to a "brand teal", no gradient
between two of them. Colour carries one meaning: this is the thing to look at. When everything on a
page is coloured, nothing is.

## 4. Depth is a border

A card is a rectangle with a 1 px `line` border and nothing else. No shadow, no glow, no blur, no
glass, no 3D tilt, no floating pane over a blurred screenshot of the same pane. A shadow at 10 %
opacity is not depth, it is a smudge that makes text at 14 px harder to read.

The only shadow in the system is on things that genuinely float above the page and can be dismissed
- a menu, a dialog, the dev toolbar - and it is `0 1px 2px rgb(0 0 0 / 0.06)`.

Radius: `2px` on inputs and code blocks, `0` everywhere else. Not 16 px on everything: a uniform
16 px radius is the strongest single signal that a page came out of a template, because a human
choosing radii uses at least two, on purpose.

## 5. The only image is a screenshot

A post or a page shows a terminal, a browser, an editor or a card. That is the full list.

A screenshot is cropped to the part that proves something, shown at its own resolution (no fake
browser chrome, no rounded device frame, no drop shadow under the image, no fake cursor drawn on
top), and its `alt` says the number it contains. If a sentence cannot be proved by a screenshot, a
diff or a card, it does not get an image: it gets rewritten until it can.

## The looks we refuse

These are not matters of taste. Each one is a documented visual default of generated pages, and each
one makes a project look like it was described rather than built.

1. **Purple-to-indigo gradient** on a hero, a button or a heading. It arrived with AI landing pages
   and it now reads as "no designer was involved". Our accent is one flat teal.
2. **Inter everywhere**, with a 700 weight headline and `-0.02em` tracking applied to everything.
3. **A centred hero, a subtitle, two buttons, then three cards with an icon each** - "Fast", "Simple",
   "Powerful". Our homepage leads with a command that runs.
4. **Uniform 16 px radius on every surface**, plus a 1 px border on cards that also have a shadow.
5. **A 10 % black shadow under every card** to fake depth on a flat page.
6. **Glassmorphism**, blurred background panels, gradient borders, glowing orbs behind the content.
7. **Abstract 3D blobs and isometric illustrations** of servers, arrows and little people. They exist
   to fill the space where a real screenshot was never taken.

Two more, in words rather than pixels: a headline that could belong to any product ("Build faster.
Ship better."), and a testimonial from someone the reader cannot find.

## Cards

One grid for every carousel, so a swipe is visible at thumbnail size.

- 1080 × 1350 px, 4:5. Nothing at the edges: 64 px of margin, and no text within 60 px of a border.
- Cards alternate `paper` and `ink`. At 270 px wide, the alternation is what tells the reader that
  there is a next card.
- One idea per card. Headline at 92 px, in the text face, sentence case, six to nine words. A code
  line under it at 56 px in the monospace, in `accent` (`accent-lit` on the dark cards).
- Footer at 40 px: the monogram `nx` on the left, the position (`3 / 6`) on the right, in `muted`.
  No page number in words, no "@nexypy" handle, no "swipe →" arrow drawn on the card.
- The first card states the claim; the last one states the command. Never a card that only says
  "Thanks for reading".
- Body text, when a card needs a sentence, is 44 px with 1.35 line height, at most three lines.

Six cards is the default length. Nine is the maximum before the reader's thumb wins.

## The banner

`nexy.png` at the root is the 1200 × 630 banner rendered from this grid: the `nexy.svg` wordmark the
template header already ships, the claim, the mechanism it comes from, the command that starts a
project (`uvx nexy new`) and the docs URL. It is drawn by
`python scripts/make_com_media.py --slug repo-banner` (`COM/design/repo-banner/banner.png`), and the
same file serves the README and the social preview. Nothing else may be used as the banner.
