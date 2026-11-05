# CLI

Die Binärdatei ist `nx` (auch als `nexy` installiert). `uvx nexy new` erstellt ein Projekt (`uvx` wird mit uv geliefert). Führen Sie jeden anderen Befehl in der virtuellen Umgebung des Projekts oder über `uv run` aus, zum Beispiel `uv run nexy dev`: Dort befinden sich Ihre eigenen Pakete.

## Befehle

| Befehl | Alias | Was es bewirkt |
|---|---|---|
| `nx dev` | `nx d` | Entwicklungsserver: Bei Änderung kompilieren, Vite, HMR |
| `nx start` | `nx s` | Produktionsserver für die kompilierte Ausgabe |
| `nx build` | `nx b` | Produktionsaufbau |
| `nx new` | `nx n` | ein Projekt aufbauen |
| `nx init` | `nx i` | Nexy zu einem bestehenden Projekt hinzufügen |
| `nx add` | - | Fügen Sie eine UI-Komponente aus der Registrierung oder eine URL zu `src/components/ui` hinzu. |
| `nx migrate` | `nx m` | Datenbankmigrationen mit Alembic oder Aerich erstellen oder anwenden |
| `nx check` | `nx c` | Typprüfung: mypy auf Python, `tsc` auf TypeScript |
| `nx format` | `nx f` | Formatieren Sie Python (Ruff), JS/TS (hübscher), `.nexy` Dateien |
| `nx test` | - | führe pytest aus; `--client` fügt vitest hinzu |
| `nx skills` | - | Fügen Sie die Fähigkeiten `AGENTS.md` und `CLAUDE.md` für Codierungsagenten hinzu oder aktualisieren Sie sie |

## Flaggen

| Befehl | Flagge | Standard |
|---|---|---|
| `dev`, `start` | `--port` | `usePort`, `3000` |
| `dev`, `start` | `--host` | `useHost`, `0.0.0.0` |
| `build` | `--check` | off – führt ruff und mypy nach dem Build aus |
| `format` | `--check` | aus – melden statt umschreiben |
| `test` | `--client` | off - Führen Sie auch vitest anstelle von pytest allein aus |
| `test` | `--no-server` | on – Überspringen Sie pytest, wenn Sie nur Clienttests wünschen |
| `new` | `--template`, `-t` | none – Klonen Sie eine registrierte Vorlage ohne Eingabeaufforderungen |
| `new` | `--no-agents` | Agenten ein – überspringen Sie `AGENTS.md` und die Agentenfähigkeiten |
| `add` | `--ui`, `--url` | off – erzwingt einen Registrierungsnamen oder eine URL, wenn diese nicht eindeutig ist |
| `add` | `--all`, `-a` | off – Fügen Sie alle Komponenten der Registrierung hinzu |
| `add` | `--sha256` | keine – erwarteter Digest einer Remote-Komponente; eine Nichtübereinstimmung bricht ab |
| `migrate` | `--init` | off - Schreiben Sie das Alembic- oder Aerich-Setup |
| `migrate` | `--upgrade`, `-u` | off – Wenden Sie die Migrationen an, anstatt eine neue zu schreiben |
| `migrate` | `--message`, `-m` | leer – Name der neuen Revision |

## Ausgabe

Bei langen Schritten (Pakete installieren, kompilieren, bündeln) wird ein Kreisel mit der verstrichenen Zeit angezeigt, dann bleibt eine Zeile übrig: `✔ uv sync .venv  1.4s`. Eine Gruppe von Schritten (die Installationen von `nx new`) zeigt einen Fortschrittsbalken mit der Anzahl der abgeschlossenen Schritte an, `━━━━────  2/5`; Ein einzelner Schritt (`nx add`) zeigt einen Balken an, der während der Ausführung pulsiert. Entwicklungsprotokolle lauten `GET » /about 200 in 12ms` für Anfragen und `vite » ...` für Vite. Ein fehlgeschlagener Schritt druckt die letzten Zeilen der Befehlsausgabe, anstatt sie auszublenden. Terminals, die Unicode nicht rendern können, erhalten `+` und `x`.

## Fehler beim Ausführen von `nx dev`

Das Speichern einer beschädigten Datei stoppt niemals den Server. Eine `.py`-Datei mit einem Syntaxfehler wird mit ihrer Datei und Zeile gemeldet und der Server stellt weiterhin die letzte funktionierende Version bereit, bis Sie den Fehler beheben:

```text
  nexy » error  src/routes/users.py:3
  SyntaxError: invalid syntax

    1 | import json
    2 |
  > 3 | def GET(:
                ^
    4 |     x = 1
    5 |     return {"v": 2}

  Fix it and save: the server keeps its last working version.
```

Eine Datei, die analysiert wird, aber beim Laden der Anwendung fehlschlägt (ein fehlender Import, ein Fehler auf Modulebene), wird auf die gleiche Weise gemeldet und `nx dev` wartet auf Ihre nächste Speicherung; Es wird nichts bereitgestellt, bis die Anwendung erneut geladen wird. Ein gültiger Speicher lautet `nexy » update <file>`, während der Server neu lädt. Markdown-Dateien außerhalb von `src/routes`, wie etwa `README.md`, sind keine Seiten und lösen nichts aus. `nx start` ist strenger: Es wird mit Code 1 beendet und startet nichts, wenn eine Routendatei nicht geladen werden kann.

## Fragen von `nx new`

`nx new` fragt in dieser Reihenfolge: dateibasierter Router, Projekttyp (Web oder API), clientseitiges Routing, Client-Framework, wie die App gestaltet werden soll, Importalias, ORM, Datenbank und Datenbank-URL. Jede Option verfügt über eine kurze Beschreibung und die aktuelle Option ist hervorgehoben. Fragen, die nicht zutreffen, werden übersprungen (ein API-Projekt hat kein Framework oder Stil; wählen Sie **Keine Datenbank**, da der ORM die Datenbank und die URL überspringt). Bewegen Sie sich mit den Pfeiltasten (oder `j`/`k` oder einer Zahl), bestätigen Sie mit `enter`, gehen Sie mit `←` oder `esc` zur vorherigen Frage zurück, beenden Sie mit `ctrl+c`.

| Frage | Auswahlmöglichkeiten |
|---|---|
| Alias importieren | `@` (`@/components/...` zeigt auf `src/`) oder ein anderes Präfix wie `~` oder `#app` |
| Stil | Tailwind CSS, UnoCSS, Vanilla CSS, Andere (kein CSS-Tool, dasselbe einfache Stylesheet wie Vanilla) |
| ORM | SQLModel, SQLAlchemy, Tortoise-ORM, Keine Datenbank |
| Datenbank (mit einem ORM) | SQLite, PostgreSQL, Neon, MySQL / MariaDB, Andere (Sie geben die URL ein) |

Der Datenbanktreiber für das ausgewählte ORM wird mit installiert (`psycopg`, `pymysql`, `asyncpg` oder `aiomysql`) und die URL wird nach `.env` geschrieben.

Vor der Installation von Paketen prüft `nx new` die Verbindung. Ohne eine werden die Installationen übersprungen und Sie werden aufgefordert, `uv sync` und die Installation Ihres Paketmanagers später auszuführen. Bei einem davon druckt es die Latenz und Download-Geschwindigkeit aus und warnt, wenn die Verbindung langsam ist (über 400 ms oder unter 100 KB/s). Jede Installationszeile benennt das Tool und den Ordner, den es füllt, zum Beispiel `pnpm install node_modules` oder `uv sync .venv`.

## Was `dev`, `build` und `start` erschaffen

Bevor sie ausgeführt werden, erstellen die drei Befehle ein leeres `__init__.py` in `src/` und in jedem Ordner darunter, der eine `.py`- oder `.nexy`-Datei enthält, sodass eine Route wie `src/routes/users.py` in allen auf die gleiche Weise importiert. Vorhandene Dateien werden nie berührt und `nx dev` macht dasselbe noch einmal, wenn Sie einen Ordner hinzufügen. Python-Bytecode geht an `__nexy__/__pycache__`, daher erscheint kein `__pycache__`-Ordner neben Ihren Quellen.

## Sprache

Die Befehlszeile spricht Englisch, Chinesisch, Hindi, Spanisch, Portugiesisch, Französisch, Deutsch, Japanisch, Russisch, Koreanisch, Indonesisch und Arabisch. Es verwendet das erste davon, das es unterstützt:

1. die Umgebungsvariable `NEXY_LANG` (`NEXY_LANG=ja nx dev`);
2. die Gebietsschemavariablen Ihrer Shell (`LC_ALL`, `LC_MESSAGES`, `LANG`, dann `LANGUAGE`);
3. die Sprache Ihres Betriebssystems.

Alles andere ist Englisch, ebenso wie alle Nachrichten, die eine Sprache noch nicht hat. Es wird nur übersetzt, was `nx` ausgibt: Compilerfehler, Tracebacks und die Ausgabe der von ihm ausgeführten Tools bleiben unverändert. Die Übersetzungen wurden noch nicht von Muttersprachlern überprüft: Korrekturen sind als Pull-Requests an `nexy/modules/i18n/<language>.json` willkommen.

## Verhalten aufbauen

`nx build` kompiliert die Routen und bündelt dann den Client, wenn `useVite` aktiviert ist.

> [!NOTE]
> Es gibt keine `--static`-Flagge. Statisches Hosting ist eine Bereitstellungsauswahl, kein Build-Modus – siehe [Bereitstellen](../deployment/README.md).

## Arbeite an Nexy selbst

Innerhalb dieses Repositorys sind die Tore:

```bash
python scripts/verify.py             # lint, format, typecheck, tests
python scripts/audit_dependencies.py # supply-chain audit against the lock
```

## Nächste Schritte

- [Erste Schritte](../getting-started/quick-start.md): erstes Projekt
- [Testen](../guides/testing.md): was `nx test` läuft
- [Bereitstellen](../deployment/README.md): `build` und `start` in der Produktion
