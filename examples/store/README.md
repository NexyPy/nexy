# Store: a Vue shop whose cart lives on the server

Good Stock is a small shop written in Vue, with a cart, a checkout and the orders of each browser.
Every page is a Vue component the browser routes between, and every read or change is a Nexy action:
a Python function the page calls like a TypeScript one, typed from its signature. The products, the
carts and the orders are tables of SQLite, made by Alembic migrations.

![The shop page of the Store](../../docs/assets/examples/store.png)

## What it shows

| Nexy feature | Where |
|---|---|
| Client mode: Vue pages, a client router, one document rendered on the server | `nexyconfig.py`, `src/routes/layout.vue` |
| Actions called from Vue, with their TypeScript types | `src/actions/`, `src/lib/cart.ts` |
| `useAction`: pending and failure states without glue code | `src/routes/checkout.vue` |
| An action that reads and sets a cookie through `request` and `response` | `src/actions/cart.py` |
| A 404 from an action with `notFound()`, shown by the page | `src/actions/shop.py`, `src/routes/products/[slug].vue` |
| A dynamic route whose parameter arrives as a prop | `src/routes/products/[slug].vue`, `src/routes/orders/[number].vue` |
| SQLAlchemy tables and Alembic migrations, with `nexy migrate` | `src/models/`, `alembic/versions/` |
| Tailwind with the tokens of the starter, light and dark | `src/globale.css` |
| Tests of every action over HTTP, on the migrated database | `tests/` |

## Run it

You need Python 3.12 or newer, [uv](https://docs.astral.sh/uv/), and Node.js with npm, pnpm or
bun.

```bash
git clone https://github.com/NexyPy/nexy
cd nexy/examples/store
cp .env.example .env
uv sync
npm install                     # or pnpm install, bun install
uv run nexy migrate --upgrade   # creates the tables and stocks the shelves
uv run nexy dev
```

Open the address `nexy dev` prints.

## How a cart works here

The cart is not in the browser. Adding a product calls the `add_to_cart` action; the first time,
the action sets an `HttpOnly` cookie holding a random token, and the lines of the cart are rows of
`cart_lines` under that token. The page shows the cart the server answers with, totals and delivery
included, so the price on screen is always the one the order will have.

Placing an order checks the shelves and takes the products off them in one statement per line: two
checkouts at the same moment can never both buy the last field bag. The order keeps the name and the
price of the day, so a later price change leaves a past order as it was.

The shop takes no payment and has no accounts: an order is a row in SQLite, readable only from the
browser that placed it.

## Change the shelves

Products are rows, so they change through a migration, the way a real shop would ship them:

```bash
uv run nexy migrate -m "add a teapot"   # writes alembic/versions/..._add_a_teapot.py
```

Write the new rows in its `upgrade()`, as `alembic/versions/0e7f77b297b2_stock_the_shop.py` does,
put the picture in `public/products/<slug>.svg`, and run `uv run nexy migrate --upgrade`.

## Test it

```bash
uv run pytest
```

The tests run the migrations once, give each test a fresh copy of that database, and call the
actions over HTTP the way the pages do, cookie included.

## Files

```text
alembic/versions/            the tables, then the products on the shelves
src/
  models/                    the tables: products, cart lines, orders and their lines
  services/                  every query, one service per table
  actions/                   what the pages call: shop.py, cart.py, orders.py
  lib/cart.ts                the cart shared by the header and the pages
  lib/money.ts               cents to dollars, dates, stock in words
  components/                the header, a product card, the quantity, the totals
  routes/layout.vue          the document around every page
  routes/index.vue           the shelves, by category or by search
  routes/products/[slug].vue one product
  routes/cart.vue            the cart
  routes/checkout.vue        the delivery form
  routes/orders/             the orders of this browser, and one order
  globale.css                the tokens of the theme
tests/                       the services and the actions, on a migrated database
```
