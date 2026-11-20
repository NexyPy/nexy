# Dashboard

Ledger, the invoices of a small studio: sign in, see where the money stands, search and page
through the invoices, record a payment. The data is kept in SQLite by Python, the pages are
rendered on the server, and the chart is a Vue component.

![Dashboard](../../docs/assets/examples/dashboard.png)

## What it shows

| Nexy feature | Where |
|---|---|
| Sign-in with a session cookie (`useSession`), a password hashed with scrypt | `src/actions/accounts.py`, `src/services/accounts.py` |
| Pages only a signed-in user sees: one call that redirects everyone else | `signed_in()` in `src/services/accounts.py` |
| Search, filter and pages in the address, so a result can be shared and works without JavaScript | `src/routes/invoices/index.nexy` |
| A form that posts to a server action, then redirects (303) | `src/routes/invoices/[id].nexy`, `src/actions/invoices.py` |
| A Vue component inside a server page, given its data as a prop | `src/components/RevenueChart.vue` in `src/routes/index.nexy` |
| SQLModel with SQLite, demo data written the first time | `src/models/`, `src/services/demo.py` |
| Tests of every query against a real database | `tests/` |

## Run it

```bash
git clone https://github.com/NexyPy/nexy && cd nexy/examples/dashboard
cp .env.example .env    # then put a secret of your own in SESSION_SECRET
uv sync
bun install             # or npm install, pnpm install
uv run nx dev
```

Open the address `nx dev` prints and sign in with `demo@example.com` and `demo-password`. The
first start writes the demo data to `dashboard.db`; delete the file to start again from it.

## Test it

```bash
uv run pytest
```

The tests seed a temporary database on a fixed day, so every figure they check is the same on
every machine.

## Files

```text
src/
  routes/index.nexy           the overview: totals, the chart, the latest invoices
  routes/invoices/index.nexy  search, status filter, pages
  routes/invoices/[id].nexy   one invoice, and "Mark as paid today"
  routes/customers.nexy       what each customer paid and still owes
  routes/signin.nexy          the sign-in form
  actions/                    sign in, sign out, pay an invoice
  services/                   every query, the totals, the demo data, the password hash
  models/                     User, Customer, Invoice
  components/RevenueChart.vue the chart
tests/                        the services against a temporary SQLite file
```
