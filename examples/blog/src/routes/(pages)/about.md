# About Plain Text

Plain Text is a small blog about building for the web with Python. It is also the Blog example of
[Nexy](https://github.com/NexyPy/nexy): every page you read here is made by the code in
`examples/blog`, so the blog documents itself.

## How it is made

- The posts are Markdown files in `content/posts/`, read by `src/blog/posts.py`.
- The pages are `.nexy` files in `src/routes/`, rendered by Python on the server.
- This page is Markdown too: `src/routes/(pages)/about.md`, wrapped by the layout of its folder.
  The parentheses keep the folder out of the address, so the page is served at `/about`.

## Follow along

Subscribe to [the RSS feed](/rss) in any feed reader, or browse [the tags](/tags).

## Make it yours

Clone the example, change the name in `nexyconfig.py` and in the header, delete the posts, and
write your own. The README of the example lists every file and what it does.
