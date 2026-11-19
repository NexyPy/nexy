# How do I debug server code in Nexy?

Debug the server code of `nx dev` with `breakpoint()` in the terminal, or with VS Code and
`debugpy`: the dev server runs your Python in its own process, so a debugger attached to it stops in
your pages, API handlers and actions.

## How `nx dev` runs your code

`nx dev` starts uvicorn in its own process, without a separate worker. When a Python file or a
`.nexy` page changes, it forgets the modules of your project and imports them again in that same
process. A debugger attached to `nx dev` therefore stays attached across a reload, and a breakpoint
set in a file keeps its place in the new code.

A `.nexy` file is compiled to a Python module under `__nexy__/`, at the same path, which is what
runs:

<!-- router:fbr,custom -->
| You write | Nexy runs |
|---|---|
| `src/routes/about.nexy` | `__nexy__/src/routes/about.py`, function `About()` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/routes/api/users.py` | the file itself |
<!-- /router -->

<!-- router:modular -->
| You write | Nexy runs |
|---|---|
| `src/apps/users/user_view.nexy` | `__nexy__/src/apps/users/user_view.py` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/apps/users/user_controller.py` | the file itself |
<!-- /router -->

The frontmatter of a `.nexy` file (the Python between the two `---` lines) becomes the body of a
function of that module. `__nexy__/` is written again on every change: never edit it.

## Stop in the terminal with `breakpoint()`

Put `breakpoint()` where you want to stop, in a `.py` file or in the frontmatter of a `.nexy` file:

<!-- router:fbr,custom -->
```nexy filename="src/routes/about.nexy"
---
from nexy import useSearchParams

page = useSearchParams().get("page", "1")
breakpoint()
---
<p>Page {{ page }}</p>
```

Open the page. The request waits and the terminal of `nx dev` shows pdb, in the compiled module:

```text
> /path/to/app/__nexy__/src/routes/about.py(21)About()
-> breakpoint()
(Pdb)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users")
class UserController:
    async def get(self):
        page = "1"
        breakpoint()
        return {"page": page}
```

Open `/users`. The request waits and the terminal of `nx dev` shows pdb on that line. In the
frontmatter of a view, pdb shows the compiled module under `__nexy__/src/apps/`.
<!-- /router -->

Type `p page` to print a value, `n` for the next line, `c` to let the request go on. Remove the line
when you are done: the next request stops there again.

## Debug with VS Code

Install `debugpy` in the project's environment:

```bash
uv add --dev debugpy
```

Then add a launch configuration. `nexy.modules.cli` is the module behind the `nx` command, so this
works the same on Linux, macOS and Windows:

```json filename=".vscode/launch.json"
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "nx dev",
      "type": "debugpy",
      "request": "launch",
      "module": "nexy.modules.cli",
      "args": ["dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

Press F5. Set breakpoints in your `.py` files, and in the compiled module under `__nexy__/` for a
`.nexy` file: VS Code cannot stop in a `.nexy` file, because it is not Python until it is compiled. Line numbers
of the compiled module follow the frontmatter, so a breakpoint there may move after you edit the
page; `breakpoint()` in the frontmatter does not.

## Attach from another terminal

To start the dev server yourself and attach a debugger later:

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m nexy.modules.cli dev
```

`--wait-for-client` holds the start until a debugger attaches; leave it out to start at once. In
VS Code, attach with a configuration of `"request": "attach"` and
`"connect": { "host": "127.0.0.1", "port": 5678 }`.

debugpy may warn that "frozen modules are being used". Start Python with `-Xfrozen_modules=off`
(`python -Xfrozen_modules=off -m debugpy ...`) if a breakpoint in the standard library is missed;
breakpoints in your own code are not affected.

## Next steps

- [Troubleshooting](troubleshooting.md): the first problems people hit
- [Testing](testing.md): reproduce the bug in a test once you have found it
- [.nexy files](../views/nexy/README.md): frontmatter, props and templates
