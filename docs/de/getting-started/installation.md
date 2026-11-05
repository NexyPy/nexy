# Installation

## Anforderungen

| Anforderung | Warum |
|---|---|
| Python 3.12+ | `requires-python` in `pyproject.toml` |
| [uv](https://docs.astral.sh/uv/) | erstellt das Projekt, installiert seine Pakete und führt Nexy aus |
| Node.js 18+ | nur für ein Client-Framework (React, Vue, Svelte, Solid, Preact) |

Ein Projekt ohne Client-Framework benötigt überhaupt kein Node.js.

## Installieren Sie zuerst uv.

`uvx` ist kein separates Tool: Es wird mit uv geliefert, also installieren Sie uv vor allem anderen.

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Überprüfen Sie es mit `uv --version` und `uvx --version`.

## Erstellen Sie ein Projekt

```bash
uvx nexy new my-app
```

`uvx` führt Nexy in einer temporären Umgebung aus und hinterlässt nichts. Das reicht aus, um ein Projekt (`new`, `init`) **zu erstellen** und nichts weiter: Die temporäre Umgebung enthält Nexy und kein anderes Paket. `nexy new` erstellt die eigene virtuelle Umgebung des Projekts, `.venv`, und installiert dort seine Pakete.

`nexy new my-app` stellt vier Fragen: Router (dateibasiert oder modular), Projekttyp (Web oder API), Client-Framework, ORM. Die Installation von Python und Node-Abhängigkeiten läuft dann mit einer Zeile pro Schritt und deren Dauer. Siehe [CLI](../reference/cli.md).

Überspringen Sie die Eingabeaufforderungen mit einer registrierten Vorlage:

```bash
uvx nexy new my-app --template <name>
```

## Arbeiten Sie in der virtuellen Umgebung des Projekts

Jeder andere Befehl (`nexy dev`, `nexy build`, `nexy migrate`...) muss **in der virtuellen Umgebung des Projekts** ausgeführt werden. Dort leben Ihre eigenen Pakete: Ihr ORM, Ihre Bibliotheken und der Nexy, mit dem das Projekt erstellt wurde. Außerhalb davon scheitert ein Projekt, das `sqlmodel` benötigt, mit `ModuleNotFoundError: No module named 'sqlmodel'`.

Aktivieren Sie es einmal pro Terminal aus dem Projektordner:

| Shell | Befehl |
|---|---|
| PowerShell, cmd (Windows) | `.venv\Scripts\activate` |
| macOS, Linux | `source .venv/bin/activate` |

Die Eingabeaufforderung beginnt dann mit `(.venv)`. Von dort:

```bash
cd my-app
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Öffnen Sie <http://localhost:3000>.

Um die Aktivierung zu überspringen, lassen Sie uv dies für einen Befehl tun: `uv run nexy dev`.

> [!NOTE]
> `nexy` und `nx` sind dieselbe Binärdatei. Eine mit `uv tool install nexy` installierte Kopie befindet sich in einer eigenen Umgebung, wie `uvx`, also verwenden Sie sie, um Projekte zu erstellen und alles andere in der Projektumgebung auszuführen.

## Fügen Sie Nexy zu einem vorhandenen Projekt hinzu

Führen Sie es in der virtuellen Umgebung des Projekts aus, mit Nexy unter seinen Paketen (`uv add nexy`):

```bash
nexy init
```

## Nächste Schritte

- [Schnellstart](quick-start.md)
- [Tutorial](tutorial.md)
- [Projektstruktur](project-structure.md)
- [Fehlerbehebung](../guides/troubleshooting.md)
