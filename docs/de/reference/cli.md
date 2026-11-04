# CLI

Die Binärdatei ist `nx` (auch als `nexy` installiert). `uvx nexy new` erstellt ein Projekt (`uvx` wird mitgeliefert
UV). Führen Sie jeden anderen Befehl in der virtuellen Umgebung des Projekts oder über `uv run` aus, z
Beispiel `uv run nexy dev`: Dort befinden sich Ihre eigenen Pakete.

## Befehle

| Befehl | Alias | Was es tut |
|---|---|---|
| `nx dev` | `nx d` | Entwicklungsserver: Bei Änderung kompilieren, Vite, HMR |
| `nx start` | `nx s` | Produktionsserver auf der kompilierten Ausgabe |
| `nx build` | `nx b` | Produktionsaufbau |
| `nx new` | `nx n` | ein Projekt aufbauen |
| `nx init` | `nx i` | Nexy zu einem bestehenden Projekt hinzufügen |
| `nx add` | – | Fügen Sie eine UI-Komponente aus der Registrierung oder eine URL zu `src/components/ui` | hinzu.
| `nx migrate` | `nx m` | Erstellen oder Anwenden von Datenbankmigrationen mit Alembic oder Aerich |
| `nx check` | `nx c` | Typprüfung: mypy auf Python, `tsc` auf TypeScript |
| `nx format` | `nx f` | Format Python (Ruff), JS/TS (hübscher), `.nexy` Dateien |
| `nx test` | - | pytest ausführen; `--client` fügt vitest hinzu |
| `nx skills` | – | die Fähigkeiten hinzufügen oder auffrischen, `AGENTS.md` und `CLAUDE.md` für Codierungsagenten |

## Flaggen

| Befehl | Flag | Standard |
|---|---|---|
| `dev`, `start` | `--port` | `usePort`, `3000` |
| `dev`, `start` | `--host` | `useHost`, `0.0.0.0` |
| `build` | `--check` | off – führt Ruff und Mypy nach dem Build aus |
| `format` | `--check` | aus - melden statt umschreiben |
| `test` | `--client` | aus – Führen Sie auch Vitest anstelle von Pytest allein aus |
| `test` | `--no-server` | on – Pytest überspringen, wenn Sie nur Client-Tests wünschen |
| `new` | `--template`, `-t` | keine – registrierte Vorlage ohne Eingabeaufforderungen klonen |
| `new` | `--no-agents` | Agenten ein – überspringen `AGENTS.md` und die Agentenfähigkeiten |
| `add` | `--ui`, `--url` | aus – einen Registrierungsnamen oder eine URL erzwingen, wenn diese nicht eindeutig ist |
| `add` | `--all`, `-a` | aus – fügen Sie alle Komponenten der Registrierung hinzu |
| `add` | `--sha256` | keine – erwarteter Digest einer Remote-Komponente; eine Nichtübereinstimmung bricht ab |
| `migrate` | `--init` | aus – schreiben Sie das Alembic- oder Aerich-Setup |
| `migrate` | `--upgrade`, `-u` | aus – wenden Sie die Migrationen an, anstatt eine neue zu schreiben |
| `migrate` | `--message`, `-m` | leer – Name der neuen Revision |

## Ausgabe

Bei langen Schritten (Pakete installieren, kompilieren, bündeln) wird dann ein Spinner mit der verstrichenen Zeit angezeigt
Lassen Sie eine Zeile zurück: `✔ uv sync .venv  1.4s`. Eine Gruppe von Schritten (die Installationen von `nx new`) zeigt a
Fortschrittsbalken mit der Anzahl der abgeschlossenen Schritte, `━━━━────  2/5`; Ein einzelner Schritt (`nx add`) zeigt a
Balken, der während des Betriebs pulsiert. Entwicklungsprotokolle lesen `GET » /about 200 in 12ms` für Anfragen und
`vite » ...` für Vite. Ein fehlgeschlagener Schritt druckt den letzten
Zeilen der Befehlsausgabe, anstatt sie auszublenden. Terminals, die Unicode nicht rendern können, erhalten
`+` und `x`.

## Fehler während der Ausführung von `nx dev`

Das Speichern einer beschädigten Datei stoppt niemals den Server. Eine `.py`-Datei mit einem Syntaxfehler wird mit gemeldet
Datei und Zeile, und der Server stellt weiterhin die letzte funktionierende Version bereit, bis Sie das Problem beheben:

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

Eine Datei, die analysiert wird, aber beim Laden der Anwendung fehlschlägt (ein fehlender Import, ein Fehler im Modul).
Level) wird auf die gleiche Weise gemeldet und `nx dev` wartet auf Ihren nächsten Speichervorgang; Bis dahin wird nichts serviert
Die Anwendung wird erneut geladen. Ein gültiger Speicher lautet `nexy » update <file>`, während der Server neu lädt. Markdown-Dateien außerhalb
`src/routes`, wie etwa `README.md`, sind keine Seiten und lösen nichts aus.
`nx start` ist strenger: Es wird mit Code 1 beendet und startet nichts, wenn eine Routendatei nicht geladen werden kann.

## Fragen von `nx new`

`nx new` fragt in dieser Reihenfolge: dateibasierter Router, Projekttyp (Web oder API), clientseitiges Routing,
Client-Framework, Stil der App, Importalias, ORM, Datenbank und Datenbank-URL. Jede Option hat einen Kurzschluss
Beschreibung und die aktuelle wird hervorgehoben. Fragen, die nicht zutreffen, werden übersprungen (eine API
Projekt hat keinen Rahmen oder Stil; Wählen Sie **Keine Datenbank**, da der ORM die Datenbank und die URL überspringt.
Bewegen Sie sich mit den Pfeiltasten (oder `j`/`k` oder einer Zahl), bestätigen Sie mit `enter` und kehren Sie zum vorherigen zurück
Frage mit `←` oder `esc`, beenden mit `ctrl+c`.

| Frage | Auswahlmöglichkeiten |
|---|---|
| Importalias | `@` (`@/components/...` zeigt auf `src/`) oder ein anderes Präfix wie `~` oder `#app` |
| Stil | Tailwind CSS, UnoCSS, Vanilla CSS, Andere (kein CSS-Tool, dasselbe einfache Stylesheet wie Vanilla) |
| ORM | SQLModel, SQLAlchemy, Tortoise-ORM, Keine Datenbank |
| Datenbank (mit einem ORM) | SQLite, PostgreSQL, Neon, MySQL / MariaDB, Andere (Sie geben die URL ein) |

Der Datenbanktreiber für das gewählte ORM wird mit installiert (`psycopg`, `pymysql`, `asyncpg` oder
`aiomysql`) und die URL wird nach `.env` geschrieben.

Vor der Installation von Paketen prüft `nx new` die Verbindung. Ohne eine werden die Installationen übersprungen und
fordert Sie auf, `uv sync` und die Installation Ihres Paketmanagers später auszuführen. Mit einem druckt es das
Latenz und Download-Geschwindigkeit und warnt, wenn die Verbindung langsam ist (über 400 ms oder weniger).
100 KB/s). Jede Installationszeile benennt beispielsweise das Tool und den Ordner, den es füllt
`pnpm install node_modules` oder `uv sync .venv`.

## Was `dev`, `build` und `start` erschaffen

Bevor sie ausgeführt werden, erstellen die drei Befehle ein leeres `__init__.py` in `src/` und in jedem Ordner
Darunter befindet sich eine `.py`- oder `.nexy`-Datei, sodass eine Route wie `src/routes/users.py` die Datei importiert
bei allen gleich. Vorhandene Dateien werden nie berührt und `nx dev` macht das Gleiche noch einmal, wenn
Sie fügen einen Ordner hinzu. Der Python-Bytecode geht an `__nexy__/__pycache__`, also keinen Ordner `__pycache__`.
erscheint neben Ihren Quellen.

## Sprache

Die Befehlszeile spricht Englisch, Chinesisch, Hindi, Spanisch, Portugiesisch, Französisch, Deutsch, Japanisch,
Russisch, Koreanisch, Indonesisch und Arabisch. Es verwendet das erste davon, das es unterstützt:

1. die `NEXY_LANG` Umgebungsvariable (`NEXY_LANG=ja nx dev`);
2. die Gebietsschemavariablen Ihrer Shell (`LC_ALL`, `LC_MESSAGES`, `LANG`, dann `LANGUAGE`);
3. die Sprache Ihres Betriebssystems.

Alles andere ist Englisch, ebenso wie alle Nachrichten, die eine Sprache noch nicht hat. Nur was `nx`
prints wird übersetzt: Compilerfehler, Tracebacks und die Ausgabe der von ihm ausgeführten Tools bleiben unverändert
sind. Die Übersetzungen wurden noch nicht von Muttersprachlern überprüft:
Korrekturen sind als Pull-Requests an `nexy/modules/i18n/<language>.json` willkommen.

## Build-Verhalten

`nx build` kompiliert die Routen und bündelt dann den Client, wenn `useVite` aktiviert ist.

> [!NOTE]
> es gibt keine `--static` Flagge. Statisches Hosting ist eine Bereitstellungsauswahl, kein Build
> Modus – siehe [Bereitstellen](../deployment/README.md).

## Arbeiten an Nexy selbst

Innerhalb dieses Repositorys sind die Tore:

```bash
python scripts/verify.py             # lint, format, typecheck, tests
python scripts/audit_dependencies.py # supply-chain audit against the lock
```

## Nächste Schritte

- [Erste Schritte](../getting-started/quick-start.md): erstes Projekt
- [Testen](../guides/testing.md): was `nx test` läuft
- [Bereitstellen](../deployment/README.md): `build` und `start` in der Produktion