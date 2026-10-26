# Dev toolbar

`nexy dev` adds a toolbar to every HTML page: a small "Nexy" pill at the bottom of the window. It
is never part of a production response.

| Tab | Shows |
|---|---|
| Page | URL, matched route, handler, status, server time, time to first byte, DOM ready, islands |
| Routes | every route of the app with its methods; the current one is marked |
| Errors | server errors since `nexy dev` started and the errors the browser raised |
| Config | the configuration in use (`useCSR`, `useVite`, `useFF`, `useBadge`, aliases...) |

An uncaught error in the browser opens a dialog over the page with the message and the stack, like
the Next.js overlay. A server error answers with a page of the same kind: the error, where it was
raised and the code around it. Press `Esc` to dismiss the dialog.

`Hide` removes the toolbar for this browser; `Shift`+`Alt`+`D` brings it back.

## Turn it off

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useDevTools = False
```

The toolbar is a style block and a script added before `</body>`: no external request, no
dependency. JSON, files and every response that is not HTML are left alone.

## Next steps

- [Config](../reference/config.md): every option
- [Testing](testing.md): test a page or a component
