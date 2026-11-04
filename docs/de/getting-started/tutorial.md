# Tutorial: Erstellen Sie eine Notizenseite in 10 Minuten

Sie erstellen ein Projekt, fügen eine Seite hinzu, fügen einen Python-Endpunkt hinzu, tauschen Daten zwischen ihnen aus und erstellen
für die Produktion. Sie enden mit einer Liste von Notizen, die als Seite und als JSON bereitgestellt werden.

Neu bei Nexy? Führen Sie zuerst den [Schnellstart](quick-start.md) durch: Es dauert drei Minuten.

```diagram filename="Das ganze Tutorial in einer Zeile"
uvx nexy new notes ──► edit layout ──► add page ──► add endpoint ──► share data ──► nx build ──► nx start
```

## 1. Erstellen Sie das Projekt

```bash
uvx nexy new notes
cd notes
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

`uvx` kommt mit [uv](https://docs.astral.sh/uv/) und erstellt nur das Projekt. Jeder Befehl danach
es läuft in der virtuellen Umgebung des Projekts (oder als `uv run nexy dev`).

Wählen Sie den dateibasierten Router, ein Webprojekt und ein beliebiges Client-Framework (oder keines) aus. Offen
<http://localhost:3000>. Lange Schritte geben jeweils eine Zeile mit ihrer Dauer aus, wie es `uv` tut.

<!-- router:modular -->
Beantworten Sie `No` auf die dateibasierte Router-Eingabeaufforderung: `nx new` baut den modularen Router in `src/apps/` auf.
statt `src/routes/`.
<!-- /router -->

<!-- router:custom -->
Beantworten Sie `Yes` die dateibasierte Router-Eingabeaufforderung für die Seiten und mounten Sie dann Ihre vorhandene `APIRouter`
in `nexyconfig.py`: Die beiden Router existieren nebeneinander.
<!-- /router -->

## 2. Bearbeiten Sie das Layout

<!-- router:fbr,custom -->
`src/routes/layout.nexy` besitzt das HTML-Dokument (mit React-Client-Routing ist es `layout.tsx`). Ändern Sie `<title>`:

```nexy
<title>Notes</title>
```

Speichern: Der Browser wird neu geladen. Siehe [Layouts](../routing/fbr/layouts/README.md).
<!-- /router -->

<!-- router:modular -->
Der Controller rendert `src/apps/layout.nexy` um die Ansicht herum, und diese Datei besitzt den HTML-Code
Dokument. Ändern Sie `<title>`:

```nexy
<title>Notes</title>
```

Speichern: Der Browser wird neu geladen. Siehe [Ansichten von einem Controller](../routing/modular/README.md#views-from-a-controller).
<!-- /router -->

## 3. Fügen Sie eine Seite hinzu

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Öffnen Sie <http://localhost:3000/notes>: Sie sollten zwei Aufzählungszeichen sehen. Es wird um `/notes` serviert. Der Teil zwischen `---` ist Python, der Rest ist Jinja2.
<!-- /router -->

<!-- router:modular -->
Ein Controller gibt eine Ansicht zurück. Erstellen Sie `src/apps/notes_view.nexy`:

```nexy filename="src/apps/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Deklarieren Sie die Route in `src/apps/app_controller.py` und fügen Sie den Controller zum Modul hinzu:

```python filename="src/apps/app_controller.py"
@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/notes_view.nexy"),
        })
```

```python filename="src/apps/app_module.py"
from .app_controller import AppController, NotesController

controllers = [AppController, NotesController]
```

Öffnen Sie <http://localhost:3000/notes>: Sie sollten zwei Aufzählungszeichen sehen. Der Teil zwischen `---` ist Python,
der Rest ist Jinja2.
<!-- /router -->

## 4. Fügen Sie einen Endpunkt hinzu

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes.py"
async def GET():
    return [{"id": 1, "text": "Buy milk"}]
```

```bash
curl http://localhost:3000/api/notes
```

Sie sollten `[{"id":1,"text":"Buy milk"}]` erhalten. Der Funktionsname ist die HTTP-Methode. Interaktive API-Dokumente finden Sie unter `/docs`.
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/app_controller.py"
@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": 1, "text": "Buy milk"}]
```

Fügen Sie `NotesApiController` zu `controllers` in `src/apps/app_module.py` hinzu und führen Sie dann Folgendes aus:

```bash
curl http://localhost:3000/api/notes
```

Sie sollten `[{"id":1,"text":"Buy milk"}]` erhalten. Der Methodenname ist die HTTP-Methode. Interaktive API-Dokumente finden Sie unter `/docs`.
<!-- /router -->

## 5. Teilen Sie die Daten

Verschieben Sie die Liste in ein Python-Modul und verwenden Sie sie in beiden Dateien:

```python filename="src/notes.py"
NOTES = ["Buy milk", "Ship Nexy"]
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes_view.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/apps/app_controller.py"
from src.notes import NOTES


@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

## 6. Zusammenbauen und servieren

```bash
nx build
nx start
```

`nx build` gibt jede Phase mit ihrer Dauer aus. `nx start` stellt die kompilierte Ausgabe bereit
Uvicorn: kein Node-Prozess zur Laufzeit.

## Wie geht es weiter?

- [Routing](../routing/README.md): dynamische Segmente und Gruppen
- [Aktionen](../guides/actions.md): Rufen Sie Python von einem Formular oder vom Client aus auf
- [Testen](../guides/testing.md): Testseiten und Endpunkte
- [Bereitstellen](../deployment/README.md): Container und Reverse-Proxys