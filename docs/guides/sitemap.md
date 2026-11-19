# How do I add a sitemap.xml and robots.txt to a Nexy site?

Set `useSiteUrl` in `nexyconfig.py`: Nexy then serves `/sitemap.xml`, which lists every static page
of the project, and a `/robots.txt` that points search engines to it.

## Turn it on with `useSiteUrl`

`useSiteUrl` is the public origin of the site, the one search engines see:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSiteUrl = "https://example.com"
```

`nx dev` and `nx start` then answer both files. Without `useSiteUrl` neither exists, so a project
never publishes the URL of its dev server by mistake.

## What the sitemap lists

The sitemap gives each page as an absolute URL on `useSiteUrl`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/</loc></url><url><loc>https://example.com/about</loc></url></urlset>
```

A route is listed when it answers HTML to a `GET` on a fixed path:

<!-- router:fbr,custom -->
- a page (`.nexy`, `.md`, `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte`) is listed;
- a dynamic page, such as `src/routes/users/[id].nexy`, is left out: Nexy cannot know its values;
- a Python route handler answers JSON, so it is left out.
<!-- /router -->

<!-- router:modular -->
- a controller route that answers HTML, with `@UseResponse(response_class=HTMLResponse)`, is listed;
- a route with a path parameter, such as `/users/{id}`, is left out: Nexy cannot know its values;
- a route that answers JSON is left out.
<!-- /router -->

A route hidden from the API schema (`include_in_schema=False`) is left out too.

## The `robots.txt` it serves

```text
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

## Write your own instead

Your own file always wins, and Nexy never overwrites it:

- `public/robots.txt` or `public/sitemap.xml` is served as it is, the way every file of `public/` is;
- a route of the project at `/robots.txt` or `/sitemap.xml` keeps its path.

Write your own sitemap to list dynamic pages, such as one URL per blog post.

## Next steps

- [Page metadata](../routing/fbr/pages/metadata.md): the title and description search engines show
- [Config](../reference/config.md): every setting of `nexyconfig.py`
- [Deploy](../deployment/README.md): serve the project in production
