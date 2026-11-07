# Build a notes app with Nexy, part 1: create the project

Part 1 of the tutorial creates the project you will grow into a notes app, and runs it in your
browser in about five minutes.

**Before you start:** [uv](https://docs.astral.sh/uv/) and Node.js 20 or newer. The tutorial
follows the router chosen at the top of the menu: switch it there and every part shows that
router's files.

## What you will build

By the end of the tutorial, the app has pages and a JSON API for notes, a database, accounts,
notes shared by email, live updates, tests, and a production build. Each part ends with an app that
runs, so you can stop after any of them.

## Create the project

```bash
uvx nexy new notes
```

Answer the questions this way:

| Question | Answer |
|---|---|
| File-based router? | `Yes` for the file-based and custom routers, `No` for the modular one |
| Project type | `Web` |
| Client-side routing | `No`: the server renders the pages |
| Client framework | `React`: it comes back in unit 4, for islands |
| Style | `Tailwind CSS` |
| Import alias | `@` |
| ORM | `No database`: part 5 adds one |

<!-- router:custom -->
The custom router is the file-based one plus an `APIRouter` you already have. The tutorial builds
the app with files; [Include an existing FastAPI router](../routing/custom/README.md) shows how to
mount yours next to them.
<!-- /router -->

## Run it

```bash
cd notes
source .venv/bin/activate    # Windows: .venv\Scripts\activate
nexy dev
```

Open <http://localhost:3000>. You should see the welcome page. Leave `nexy dev` running: from now
on, every file you save reloads the browser.

## What you learned

- `uvx nexy new` creates a project and installs its Python and JavaScript packages.
- `nexy dev` serves it and reloads on save.
<!-- router:fbr,custom -->
- The pages live in `src/routes/`: the next part adds one.
<!-- /router -->
<!-- router:modular -->
- The controllers and their views live in `src/apps/`: the next part adds one.
<!-- /router -->

## Next steps

- [Part 2: pages and layouts](pages-and-layouts.md)
- [Project structure](../getting-started/project-structure.md): what each file of the project is for
