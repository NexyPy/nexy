# Dev toolbar

`nexy dev` adds a toolbar to every HTML page. It sits in the bottom-left corner, shows the route you
are on and how long the server took, and opens into a panel. It is never part of a production
response.

| Tab | Shows |
|---|---|
| Page | URL, route, handler, the file it comes from (with a link that opens it in your editor), status, server time, first byte, first paint, main content, layout shift (graded green, amber or red), DOM ready |
| Routes | every route of the app with its methods, a filter, and the current one marked; each links to its file |
| Errors | server errors since `nexy dev` started and the errors the browser raised |
| Settings | theme (match the page, dark or light), position, size, hide, reset |

## Move it

Drag the button: it follows the pointer and snaps to the nearest corner when you let go. The panel
opens towards the middle of the screen from wherever the button is. The position is kept in this
browser. You can also pick a corner in **Settings**.

`Shift` + `Alt` + `D` hides and shows the toolbar. `Esc` closes the panel.

## Errors

An uncaught error in the browser opens a dialog over the page with the message and the stack; with
several errors, step through them (1 of 3). A server error answers with a page of the same kind: the
error, where it was raised and the code around it.

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
