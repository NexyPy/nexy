# Frontend Pages

A **Page** is the basic unit of a Nexy application. It is an URL-addressable resource defined by a file under `src/routes/`. 

Regardless of the client framework used, every page follows the same universal lifecycle and architectural constraints.

## The Page Lifecycle

When a user navigates to a page, Nexy performs the following steps:

1.  **Route Matching**: The router identifies the file corresponding to the URL.
2.  **Data Fetching**: The server executes the page's logic (Python frontmatter or framework loader) to fetch the required data.
3.  **Composition**: The page is wrapped in its nearest `layout.nexy` (or framework layout).
4.  **Rendering**: The result is rendered to HTML (via Jinja2, Markdown, or framework SSR).
5.  **Hydration**: If the page uses a client framework, the browser attaches the interactive logic to the static HTML.

## Routing & URLs

Routing is strictly file-based. The URL is determined by the file's path under `src/routes/`, minus the extension.

### Dynamic Segments
To create a route that varies by parameter (e.g., a user profile), use square brackets:
- `src/routes/user/[id].tsx` → `/user/123`

The value of the segment (`123`) is available to the page via the `useParams()` hook from `@nexy/client`.

### Route Groups
Folders wrapped in parentheses are ignored by the router but allow you to group files for organizational purposes or shared layouts:
- `src/routes/(auth)/login.tsx` → `/login`

## Page Metadata
Every page can define metadata (title, description, OpenGraph tags) that Nexy injects into the document shell. In `.nexy` files, this is done in the frontmatter; in framework files, it is provided via a `metadata` export.

## Framework Implementation
The concepts above are universal. To see how to implement a Page in your specific framework, see the **Differences** guide:

- [React Differences](../react/differences.md)
- [Vue Differences](../vue/differences.md)
- [Svelte Differences](../svelte/differences.md)
- [Solid Differences](../solid/differences.md)
- [Preact Differences](../preact/differences.md)
