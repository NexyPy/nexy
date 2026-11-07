+++
date = 2026-11-13
platforms = ["linkedin"]
link = "https://nexypy.github.io/nexy/docs/routing/fbr/"
cta = "comment"
ask = "none"
alt = [
  "A route is a file. routes/about.nexy.",
  "The folder is the URL. routes/blog/[slug].nexy.",
  "Markdown is a route. routes/changelog.md.",
  "React is a route too. routes/counter.tsx.",
  "Python is the API. routes/api/users.py.",
  "One origin. No CORS. nx dev, port 3000.",
]
+++

Six files. Six routes. One dev server.

Under src/routes/, the extension decides what a file becomes: a Jinja page, a Markdown page, a React
or Vue page in client mode, a Python endpoint in both. The URL is the file path, so there is no route
table to keep in sync with what is on disk.

Swipe for the six.

- Espoir Loem
