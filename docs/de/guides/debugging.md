# Wie debugge ich Servercode in Nexy?

Debuggen Sie den Servercode von `nx dev` mit `breakpoint()` im Terminal oder mit VS-Code und `debugpy`: Der Entwicklungsserver führt Ihr Python in seinem eigenen Prozess aus, sodass ein damit verbundener Debugger in Ihren Seiten, API-Handlern und Aktionen stoppt.

## Wie `nx dev` Ihren Code ausführt

`nx dev` startet uvicorn in einem eigenen Prozess, ohne einen separaten Worker. Wenn sich eine Python-Datei oder eine `.nexy`-Seite ändert, vergisst es die Module Ihres Projekts und importiert sie im selben Prozess erneut. Ein an `nx dev` angehängter Debugger bleibt daher über einen Neuladevorgang hinweg angehängt, und ein in einer Datei festgelegter Haltepunkt behält seinen Platz im neuen Code.

Eine `.nexy`-Datei wird in ein Python-Modul unter `__nexy__/` im gleichen Pfad kompiliert, was Folgendes ausführt:

<!-- router:fbr,custom -->
| Du schreibst | Nexy rennt |
|---|---|
| `src/routes/about.nexy` | `__nexy__/src/routes/about.py`, Funktion `About()` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/routes/api/users.py` | die Datei selbst |
<!-- /router -->

<!-- router:modular -->
| Du schreibst | Nexy rennt |
|---|---|
| `src/apps/users/user_view.nexy` | `__nexy__/src/apps/users/user_view.py` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/apps/users/user_controller.py` | die Datei selbst |
<!-- /router -->

Der Titel einer `.nexy`-Datei (der Python zwischen den beiden `---`-Zeilen) wird zum Hauptteil einer Funktion dieses Moduls. `__nexy__/` wird bei jeder Änderung erneut geschrieben: Niemals bearbeiten.

## Stoppen Sie im Terminal mit `breakpoint()`

Platzieren Sie `breakpoint()` an der Stelle, an der Sie aufhören möchten, in einer `.py`-Datei oder im Titelblatt einer `.nexy`-Datei:

<!-- router:fbr,custom -->
```nexy filename="src/routes/about.nexy"
---
from nexy import useSearchParams

page = useSearchParams().get("page", "1")
breakpoint()
---
<p>Page {{ page }}</p>
```

Öffnen Sie die Seite. Die Anfrage wartet und das Terminal von `nx dev` zeigt pdb im kompilierten Modul an:

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

Öffnen Sie `/users`. Die Anfrage wartet und das Terminal von `nx dev` zeigt pdb in dieser Zeile an. Im Vordergrund einer Ansicht zeigt pdb das kompilierte Modul unter `__nexy__/src/apps/`.
<!-- /router -->

Geben Sie `p page` ein, um einen Wert auszugeben, `n` für die nächste Zeile und `c`, um die Anfrage fortzusetzen. Entfernen Sie die Zeile, wenn Sie fertig sind: Die nächste Anfrage stoppt dort wieder.

## Debuggen Sie mit VS-Code

Installieren Sie `debugpy` in der Projektumgebung:

```bash
uv add --dev debugpy
```

Fügen Sie dann eine Startkonfiguration hinzu. `nexy.modules.cli` ist das Modul hinter dem Befehl `nx`, daher funktioniert dies unter Linux, macOS und Windows gleich:

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

Drücken Sie F5. Legen Sie Haltepunkte in Ihren `.py`-Dateien und im kompilierten Modul unter `__nexy__/` für eine `.nexy`-Datei fest: VS-Code kann in einer `.nexy`-Datei nicht anhalten, da sie erst nach der Kompilierung Python ist. Die Zeilennummern des kompilierten Moduls folgen der Frontmatter, sodass ein Haltepunkt dort möglicherweise verschoben wird, nachdem Sie die Seite bearbeitet haben. `breakpoint()` in der Einleitung nicht.

## Von einem anderen Terminal aus anschließen

So starten Sie den Entwicklungsserver selbst und fügen später einen Debugger hinzu:

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m nexy.modules.cli dev
```

`--wait-for-client` hält den Start, bis ein Debugger angehängt wird; Lassen Sie es weg, um sofort zu beginnen. Hängen Sie in VS Code eine Konfiguration von `"request": "attach"` und `"connect": { "host": "127.0.0.1", "port": 5678 }` an.

debugpy warnt möglicherweise, dass „eingefrorene Module verwendet werden“. Beginnen Sie Python mit `-Xfrozen_modules=off` (`python -Xfrozen_modules=off -m debugpy ...`), wenn ein Haltepunkt in der Standardbibliothek fehlt; Haltepunkte in Ihrem eigenen Code sind nicht betroffen.

## Nächste Schritte

- [Fehlerbehebung](troubleshooting.md): Die ersten Probleme, auf die Menschen stoßen
- [Testen](testing.md): Reproduzieren Sie den Fehler in einem Test, sobald Sie ihn gefunden haben
- [.nexy-Dateien](../views/nexy/README.md): Frontmatter, Requisiten und Vorlagen
