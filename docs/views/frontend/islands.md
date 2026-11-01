# Frontend Islands

An **Island** is a unit of client-side interactivity embedded within a server-rendered page. Islands allow you to ship the minimum amount of JavaScript necessary, keeping the rest of the page as static HTML.

## The Boundary

The boundary of an island is the point where Nexy stops rendering static HTML and starts managing a framework component.

- **Static Shell**: The bulk of the page is rendered as HTML on the server.
- **Interactive Hole**: The island is a placeholder that the browser "fills" with an interactive component.

## Hydration Strategy

Nexy uses a "Partial Hydration" strategy. Instead of hydrating the entire page, the browser only hydrates the islands.

1.  **Serialization**: The server renders the component's initial state into the HTML.
2.  **Bootstrapping**: The client-side runtime identifies the island and loads the corresponding framework bundle.
3.  **Hydration**: The framework takes over the static HTML and makes it interactive.

## Props and Serialization

Islands communicate with the server via **Props**. 
- Props must be **serializable** (plain objects, arrays, strings, numbers).
- You cannot pass functions or complex class instances from the server to an island.

## Framework Implementation

Every framework implements islands slightly differently (e.g., using different hooks or wrappers). See the **Differences** guide for details:

- [React Differences](../react/differences.md)
- [Vue Differences](../vue/differences.md)
- [Svelte Differences](../svelte/differences.md)
- [Solid Differences](../solid/differences.md)
- [Preact Differences](../preact/differences.md)
