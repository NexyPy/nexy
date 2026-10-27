---
name: nexy-testing
description: Test-first workflow for Nexy projects - red, green, refactor with nx test, TestClient, nexy.testing.render and vitest - and the quality gates to run before reporting done. Load it before writing code.
---

# Testing, test first

## The loop

1. **Red.** Write one test for one behaviour. Run it and watch it fail for the right reason.
2. **Green.** Write the least code that passes.
3. **Refactor.** Clean up while the test stays green.

One assertion per test. Name it `test_<thing>_<scenario>`. A test that cannot fail proves nothing.

## What to use

| You test | With |
|---|---|
| A page or an API route | `TestClient(app)` from `fastapi.testclient`, `from nexy.app import app` |
| A fresh configuration | `TestClient(AppServer().run())` from `nexy.modules.routers.app` |
| A `.nexy` component | `nexy.testing.render("src/components/button.nexy", label="Save")` |
| An action | call the function directly; read the generated path from the page for the HTTP test |
| A client component | vitest with the testing library of the framework |

Run pytest from the project root: `nexyconfig.py` is read from the working directory.

```python
from fastapi.testclient import TestClient

from nexy.app import app


def test_home_shows_the_running_message():
    response = TestClient(app).get("/")
    assert "Your app is running" in response.text
```

Assert what a person would notice: the status, the heading, the message, the link. Not the markup
around it.

## Test the experience, not only the code

For a view, the audit brief ([nexy-ux-audit](../nexy-ux-audit/SKILL.md)) gives the tests: the
empty state, the error message, the primary action, the label of the button. If the brief says an
error explains what to do, assert that sentence.

## Gates

Run them in this order and fix the first failure before moving on.

```bash
nx check                  # mypy and tsc
nx test                   # pytest
nx test --client          # adds vitest
nx build                  # fails on a compile error
```

In the Nexy repository itself use `python scripts/verify.py` (see
[nexy-framework-dev](../nexy-framework-dev/SKILL.md)).

## Reporting

Say what you ran and what it printed. A failing gate is reported with its output, not summarised
away. Something you did not run is reported as not run.
