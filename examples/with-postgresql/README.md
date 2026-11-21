# With PostgreSQL: SQLModel, and the database chosen by DATABASE_URL

A bookmark list kept in PostgreSQL with SQLModel. The database is one environment variable:

```bash
DATABASE_URL=postgresql+psycopg://nexy:nexy-dev-only@localhost:5432/bookmarks
```

Without it the sample uses SQLite in `dev.db`, so it runs with no server at all, and the tests run on
SQLite in CI and on PostgreSQL on a machine that has one. The page says which database it uses.

| File | What it does |
|---|---|
| `src/configs/db.py` | the engine, from `DATABASE_URL`; `create_tables()` |
| `src/models/bookmark.py` | the `Bookmark` table |
| `src/services/bookmarks.py` | every query: add, search, and what makes a bookmark valid |
| `src/actions/bookmarks.py` | the Action the form posts to |
| `src/routes/index.nexy` | the list, the search and the form |
| `compose.yaml` | a PostgreSQL 17 for local work |

This is the layout `nx new` writes when you pick SQLModel ([the databases guide](../../docs/guides/databases.md)):
pages and actions call the service, never the engine.

## Run it on PostgreSQL

You need Python 3.12 or newer, [uv](https://docs.astral.sh/uv/), Node.js with npm, pnpm or bun,
and a PostgreSQL: the one in `compose.yaml`, or any other.

```bash
git clone https://github.com/NexyPy/nexy
cd nexy/examples/with-postgresql
docker compose up -d          # skip it to stay on SQLite
cp .env.example .env
uv sync
npm install                   # or pnpm install, bun install
uv run nexy dev
```

The tables are created at the first start. Once a table changes, move to migrations:
`nx new` sets up Alembic for that, see the guide.

**MySQL or MariaDB** is the same code with another URL and driver: `uv add pymysql`, then
`DATABASE_URL=mysql+pymysql://user:password@localhost:3306/bookmarks`.

## Safe by default

- An address must be `http://` or `https://`: a `javascript:` link would run code when clicked.
- Titles and addresses are printed with `| e`.
- The search escapes `%` and `_`, so `100%` finds a title with `100%` in it, not every title.
- Queries go through SQLModel with bound parameters: no SQL is built from text.

## Test it

```bash
uv run pytest                                          # on SQLite
DATABASE_URL=postgresql+psycopg://... uv run pytest     # on your PostgreSQL
```

Each test starts with empty tables. The tests add from the form, search in any case, refuse
`javascript:` and an empty title, and check that a title with HTML is printed as text.
