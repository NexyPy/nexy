# Schnellstart

Sie erstellen ein Nexy-Projekt, führen es aus und sehen beim Bearbeiten eine Seitenänderung. Es dauert drei Minuten. Das [Tutorial](tutorial.md) fügt dann einen Endpunkt und einen Produktions-Build hinzu.

## Bevor Sie beginnen

| Sie benötigen | Warum |
|---|---|
| Python 3.12+ | `requires-python` in `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | stellt `uvx` bereit, erstellt das Projekt und installiert seine Pakete |
| Node.js 18+ | nur, wenn Sie ein Client-Framework verwenden (React, Vue, Svelte, Solid, Preact) |

Noch kein uv? Siehe [Installation](installation.md).

## 1. Erstellen Sie das Projekt

```bash
uvx nexy new my-app
```

`uvx` wird mit uv geliefert, also installieren Sie zuerst uv. Es führt Nexy in einer temporären Umgebung aus, die ausreicht, um das Projekt zu **erstellen**. `nexy new` erstellt dann das projekteigene `.venv` und installiert seine Pakete dort. Vier Eingabeaufforderungen entscheiden über die Verkabelung:

| Aufforderung | Wirkung |
|---|---|
| Dateibasierter Router? | `Yes` scannt `src/routes/`; `No` baut den modularen Router in `src/apps/` | auf
| Projekttyp | `Web` fügt ein Layout und Client-Assets hinzu, `API` beginnt ohne Ansichten |
| Client-Komponente? | fügt ein Framework und dessen Vite Setup hinzu |
| ORM / Datenbank | fügt eine Modellebene hinzu oder nichts |

Nicht sicher? Antwort `Yes`, `Web` und keine Client-Komponente. Sie können jedes später hinzufügen.

## 2. Führen Sie es aus

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Öffnen Sie <http://localhost:3000>. Sie sollten die Startseite sehen. Der Port kommt von `usePort` (Standard `3000`); `--port` und `--host` überschreiben es pro Lauf.

> [!NOTE]
> Führen Sie jeden Befehl außer `new` und `init` in der virtuellen Umgebung des Projekts aus oder stellen Sie ihm `uv run` voran, wie in `uv run nexy dev`. Außerhalb davon schlägt ein Projekt, das `sqlmodel` benötigt, mit `No module named 'sqlmodel'` fehl.

## 3. Wechseln Sie eine Seite

<!-- router:fbr,custom -->
Eine Datei unter `src/routes/` ist eine Route. Erstellen Sie `src/routes/hello.nexy`:

```nexy filename="src/routes/hello.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```
<!-- /router -->

<!-- router:modular -->
Ein Controller gibt eine Ansicht zurück. Erstellen Sie `src/apps/hello_view.nexy`:

```nexy filename="src/apps/hello_view.nexy"
---
title: prop[str] = "Hello"
---
<h1>{{ title }}</h1>
```

Dann deklarieren Sie die Seite in `src/apps/app_controller.py` und fügen Sie sie dem Modul hinzu:

```python filename="src/apps/app_controller.py"
@Controller("/hello")
class HelloController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/hello_view.nexy")})
```

```python filename="src/apps/app_module.py"
from .app_controller import AboutController, AppController, HelloController

controllers = [AppController, AboutController, HelloController]
```
<!-- /router -->

Öffnen Sie <http://localhost:3000/hello>. Ändern Sie `"Hello"` in `"Bonjour"` und speichern Sie: Die Seite wird ohne manuelles Neuladen aktualisiert. Wenn der Code falsch ist, zeigt der Browser den Fehler anstelle einer leeren Seite an.

`prop[str]` deklariert eine typisierte Eigenschaft. Das Markup unter der Frontmatter ist Jinja2 – siehe [.nexy-Dateien](../views/nexy/README.md).

## Wohin als nächstes

| Sie möchten | lesen |
|---|---|
| Fügen Sie einen Python Endpunkt hinzu und versenden Sie einen Build | [Tutorial](tutorial.md) |
| Wissen, wo jede Datei hingehört | [Projektstruktur](project-structure.md) |
| Verstehen Sie, wer was baut | [Wie Nexy funktioniert](how-nexy-works.md) |
| Verwenden Sie React, Vue, Svelte, Solid oder Preact | [Ansichten](../views/README.md) |
