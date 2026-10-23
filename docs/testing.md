# Testing

`nx test` runs the server tests with pytest, and the client tests with vitest when you ask for them.

```bash
nx test                       # pytest
nx test -k create_user        # extra arguments go to pytest
nx test --client              # pytest, then vitest
nx test --no-server --client  # vitest only
```

## What runs

| Part | Command | Condition |
|---|---|---|
| Server | `pytest` | runs on `tests/` when it exists, otherwise on the project root; skipped with a warning when pytest is not installed |
| Client | `npx vitest run` | only with `--client`, and only when `vitest.config.ts` exists or `vitest` appears in `package.json` |

There is no built-in end-to-end runner. Drive the server with `TestClient` and add Playwright or
Cypress yourself for browser behaviour.

## Test the server

The test client talks to the ASGI app in-process: no server to start, no port to pick.

```python filename="tests/test_pages.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_home_renders():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
```

`nexy.app.app` is the assembled application, built when the module is imported. It reads
`nexyconfig.py` from the working directory, so run pytest from the project root.

When a test changes configuration, routes or locale state, build a fresh application instead of
reusing the module-level one:

```python
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer


def test_api_hello():
    with TestClient(AppServer().run()) as client:
        response = client.get("/api/hello")
    assert response.json() == {"message": "Hello"}
```

`AppServer().run()` reassembles routes, middleware, sessions and translations, so each call starts
from the current state of the project directory.

## What to assert

A page returns HTML. Assert the status, then the content you care about:

```python
def test_blog_page_renders_slug(client):
    response = client.get("/blog/post-1")
    assert "post-1" in response.text
```

An API handler returns JSON. A validation failure is a `422`, and a missing route is a `404`
answered by `notfound.nexy` when that file exists:

```python
def test_create_item_validates_body(client):
    assert client.post("/api/items", json={}).status_code == 422
```

For an action, test the function directly - it is a normal function - and test the HTTP endpoint by
reading its generated path from the page that exposes it:

```python
from src.actions.user import create_user


async def test_create_user_returns_name():
    assert await create_user("Ada") == {"name": "Ada"}
```

```python
def test_form_posts_to_action(client):
    html = client.get("/").text
    action = html.split('action="')[1].split('"')[0]
    assert client.post(action, data={"name": "Ada"}).status_code == 200
```

> **Good to know**: action paths are deterministic but generated. Never hardcode `/_nx_<hash>` in a
> test.

## Test the client

`nx test --client` expects your own vitest setup. A minimal component test:

```tsx filename="src/components/counter.test.tsx"
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Counter from "./counter";

describe("Counter", () => {
  it("starts at zero", () => {
    const { getByText } = render(<Counter start={0} />);
    expect(getByText("0")).toBeTruthy();
  });
});
```

`vitest` and the testing library are project dependencies: `nexy new` does not install a test stack.
Add `vitest.config.ts` with the environment you need (jsdom or happy-dom for components).

## Continuous integration

Two commands are enough for a project pipeline:

```bash
nx build
nx test
```

`nx build` fails on a compilation error; `nx test` fails on a failing assertion and exits non-zero.
`nx check` adds mypy and `tsc` to the run.

Working on Nexy itself uses different commands: see [CONTRIBUTING](../CONTRIBUTING.md).

## Next steps

- [CLI](cli.md): every flag of `nx test`
- [API](api.md): what an endpoint returns
- [Deploy](deploy.md): build before you test in CI
