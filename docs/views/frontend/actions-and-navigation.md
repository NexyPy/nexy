# Actions and Navigation

Interaction in Nexy is handled through a unified system of **Actions** and **Navigation**, ensuring that the frontend and backend remain in sync without manual API glue code.

## The Action Contract

An **Action** is a server-side function that handles a mutation (e.g., updating a database). 

1.  **Typed Input**: Actions are defined in Python with type hints. Nexy generates a matching TypeScript client, so you get autocomplete and validation in your IDE.
2.  **Atomic Execution**: An action is a single `POST` request.
3.  **Result Handling**: Actions return a typed result that the client can use to update the UI.

## Client-Side Navigation

Navigation in Nexy is "intelligent." Instead of a full browser reload, Nexy swaps the content of the current page while keeping the active layouts mounted.

- **The `Link` Component**: Use the framework-specific `Link` component to perform client-side transitions.
- **Programmatic Navigation**: Use the `navigate()` function from `@nexy/client` to change pages in response to logic (e.g., after a successful login).

## Coordination: Action → Navigation

The most common pattern is to perform an action and then navigate the user to a new page.

**The Revalidation Flow:**
1.  The client calls an Action.
2.  The Action executes on the server and calls `revalidate("/path")`.
3.  The server returns the result along with a signal to refresh the specified path.
4.  The client updates the page content to reflect the new state.

## Framework Implementation

The API for calling actions and navigating varies by framework. See the **Differences** guide for your chosen technology:

- [React Differences](../react/differences.md)
- [Vue Differences](../vue/differences.md)
- [Svelte Differences](../svelte/differences.md)
- [Solid Differences](../solid/differences.md)
- [Preact Differences](../preact/differences.md)
