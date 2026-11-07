# Nexy tutorial: build a notes app step by step

The Nexy tutorial builds one notes app from an empty folder to a production build, one part at a
time, and every part ends with an app that runs.

New to Nexy? The [Quick start](quick-start.md) shows it running in three minutes; come back here to
learn how it works.

## How the tutorial works

- **One app that grows.** Each part adds one feature to the notes app of the part before.
- **Your router.** The parts follow the router chosen at the top of the menu: file-based, modular or
  custom. Switch it there, and the files of every part change with it.
- **Code that runs.** Every file with a name above it is a whole file, and the test suite replays
  the parts in order on a fresh project: what you copy is what runs.
- **Stop anywhere.** Each part takes 10 to 20 minutes and ends with what to check in the browser.

## The parts

### Unit 1: the basics

| Part | What you add | What you learn |
|---|---|---|
| [1. Create the project](../tutorial/create-the-project.md) | a project that runs | `nexy new`, `nexy dev` |
| [2. Pages and layouts](../tutorial/pages-and-layouts.md) | the notes page | pages, views, the layout |
| [3. Dynamic routes and an API](../tutorial/dynamic-routes.md) | `/notes/1` and `/api/notes` | URL segments, JSON routes, `notFound` |
| [4. Components](../tutorial/components.md) | a card per note | `.nexy` components and their props |

### Unit 2: data

| Part | What you add | What you learn |
|---|---|---|
| [5. Store the notes in SQLite](../tutorial/store-the-notes.md) | a model, a migration, a seed | SQLModel, `nx migrate` |
| [6. Create a note from a form](../tutorial/create-a-note.md) | a form that saves a note | Actions, forms without JavaScript |
| [7. Show validation errors](../tutorial/validation-errors.md) | a message above the form | rules in an Action, `303`, `useSearchParams` |
| [8. Edit and delete a note](../tutorial/edit-and-delete.md) | the forms of a note | several Actions per page, hidden fields |
| [9. Paginate the notes](../tutorial/paginate-the-notes.md) | five notes per page | `offset` and `limit`, links between pages |

### Unit 3: users

| Part | What you add | What you learn |
|---|---|---|
| [10. Create an account and sign in](../tutorial/accounts.md) | sign up, sign in, sign out | sessions, password hashing |
| [11. Give each user their own notes](../tutorial/own-notes.md) | notes that belong to a user | foreign keys, `redirect`, `401` |
| [12. Reset a forgotten password by email](../tutorial/password-reset.md) | a reset link sent by email | `smtplib`, signed tokens that expire |

### Unit 4: interactivity

| Part | What you add | What you learn |
|---|---|---|
| [13. Search the notes as you type](../tutorial/search-the-notes.md) | a search box that filters as you type | React islands, props from Python |
| [14. Tick a note without reloading the page](../tutorial/tick-a-note.md) | a Done button on each note | progressive enhancement, one Action for a form and for `fetch` |

### Coming next

| Unit | What the app gains |
|---|---|
| 5. Beyond the request | notes shared by email in the background, a daily digest, live updates |
| 6. Ship | tests, error pages and logs, security headers, a Docker build |

## Next steps

- [Part 1: create the project](../tutorial/create-the-project.md)
- [Core concepts](core-concepts.md): the words the tutorial uses
