# Frontend Pages

A **Page** is the basic unit of a Nexy application. It is an URL-addressable resource defined by a file under `src/routes/`. 

Regardless of the client framework used, every page follows the same universal lifecycle and architectural constraints.

## The Page Lifecycle

When a user navigates to a page, Nexy performs the following steps:

1.  **Route Matching**: The router identifies the file corresponding to the URL.
2.  **Data Fetching**: The server runs the page's Python frontmatter to fetch the data it needs.
3.  **Composition**: The page is wrapped in its nearest `layout.nexy` (or framework layout).
4.  **Rendering**: The result is rendered to HTML (via Jinja2, Markdown, or framework SSR).
5.  **Hydration**: If the page uses a client framework, the browser attaches the interactive logic to the static HTML.

Steps 2 to 4 in one server-mode page: the frontmatter fetches, the template renders, and the
root layout wraps the result.

```nexy filename="src/routes/users.nexy"
---
from src.users import all_users

users = all_users()
---
<h1>Users</h1>
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Routing & URLs

Routing is strictly file-based. The URL is determined by the file's path under `src/routes/`, minus the extension.

```text
src/routes/
├─ index.tsx            /
├─ about.tsx            /about
└─ blog/
   ├─ index.tsx         /blog
   └─ [slug].tsx        /blog/hello-world
```

### Dynamic Segments
To create a route that varies by parameter (e.g., a user profile), use square brackets:
- `src/routes/user/[id].tsx` → `/user/123`

The value of the segment (`123`) is available to the page via the `useParams()` hook from `@nexy/client`.

```tsx filename="src/routes/user/[id].tsx"
import { useParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  return <h1>User {id}</h1>;
}
```

### Route Groups
Folders wrapped in parentheses are ignored by the router but allow you to group files for organizational purposes or shared layouts:
- `src/routes/(auth)/login.tsx` → `/login`

```text
src/routes/
├─ layout.tsx
└─ (auth)/
   ├─ layout.tsx        wraps /login and /signup only
   ├─ login.tsx         /login
   └─ signup.tsx        /signup
```

## Page Metadata
Every page can define metadata (title, description, OpenGraph tags) that Nexy injects into the
document shell. A `.nexy` page sets it in its frontmatter, with a literal or with `setMetadata`:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

`setMetadata` is Python: a `.tsx`, `.vue` or `.svelte` page has no `metadata` export, so in client
mode write the title and the meta tags in the root layout. See
[Page metadata](../../routing/fbr/pages/metadata.md) for every field.

## Framework Implementation
The concepts above are universal. To see how to implement a Page in your specific framework, see the **Differences** guide:

- [React Differences](../react/differences.md)
- [Vue Differences](../vue/differences.md)
- [Svelte Differences](../svelte/differences.md)
- [Solid Differences](../solid/differences.md)
- [Preact Differences](../preact/differences.md)
