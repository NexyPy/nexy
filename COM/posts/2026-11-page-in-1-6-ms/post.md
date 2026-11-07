+++
date = 2026-11-06
platforms = ["linkedin"]
link = "https://github.com/NexyPy/nexy"
cta = "comment"
ask = "report"
proof = ["compile-2026-11.md"]
alt = "A terminal: 25 compile times of one route, median 1.66 ms, min 1.49, max 2.34."
+++

An 87-line page compiles in 1.6 ms on my laptop.

Three component imports, a query, a loop over 380 items: read the file, run the frontmatter, render,
write the HTML. That is the work the dev server repeats every time I press save. Median of 25
compiles, Ryzen 5 4500U, Python 3.13.

The HMR number everyone quotes is a browser reload: that time, plus a websocket message and Vite's
module graph. Not measured end to end, so not quoted. When it is, it comes with a date and a
machine.

What I cannot tell you: a slower laptop, or a page that waits for a database. Run the script on
yours and I would like your number, bad one included.

The script is in the first comment.

- Espoir Loem
