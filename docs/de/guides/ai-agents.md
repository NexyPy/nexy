# Kodiermittel

Ein mit `nx new` erstelltes Projekt enthält die Regeln, die ein Programmieragent benötigt, um Nexy-Code auf Ihre Weise zu schreiben: die Arbeitsreihenfolge, die Code- und Schreibregeln und eine Fähigkeit pro Thema. Auf dieser Seite erfahren Sie, was Sie erhalten, wohin es geht und wie Sie es auf dem neuesten Stand halten. Die Arbeit an Nexy selbst ist eine andere Aufgabe: Lesen Sie das Stammverzeichnis des Repositorys `AGENTS.md`.

## Was `nx new` hinzufügt

| Datei | Gelesen von | Enthält |
|---|---|---|
| `AGENTS.md` | Codex, OpenCode | der Stapel des Projekts, die Reihenfolge der Arbeit, die Regeln, die Liste der Fähigkeiten |
| `CLAUDE.md` | Claude Code | eine Zeile, `@AGENTS.md`, also lesen beide den gleichen Text |
| `.agents/skills/` | Codex, OpenCode | die Fähigkeiten |
| `.claude/skills/` | Claude Code, OpenCode | die gleichen Fähigkeiten |

`AGENTS.md` ist kurz und maßgeschneidert. Ein vom Client weitergeleitetes Vue-Projekt lautet „client-routed, Vue, styled with Tailwind“; Einem API-Projekt wird mitgeteilt, dass es keine Ansichten gibt. Es werden nur die passenden Skills kopiert: Ein React-Projekt bekommt `nexy-react` und keinen Vue-Skill, ein Serverprojekt bekommt die `.nexy`- und Markdown-Skills, ein API-Projekt bekommt keinen Skill über Ansichten.

Um alles zu überspringen, erstellen Sie das Projekt mit `nx new --no-agents`.

## Die Fähigkeiten

| Fertigkeit | Deckt | ab
|---|---|
| `nexy-principles` | Arbeitsreihenfolge, Coderegeln, Schreibregeln |
| `nexy-ux-audit` | Das Erfahrungs- und Informationsarchitektur-Audit, das vor jeder Ansicht durchgeführt werden muss |
| `nexy-project` | Modi, Ordner, Dateikonventionen, Konfiguration, Befehle |
| `nexy-file` | `.nexy` Seiten, Requisiten, Haken, Inseln |
| `nexy-markdown` | `.md` und `.mdx` Inhalt |
| `nexy-react`, `nexy-preact`, `nexy-solid`, `nexy-vue`, `nexy-svelte` | Idiomatischer Code für das Client-Framework |
| `nexy-styling` | Tailwind, UnoCSS oder einfaches CSS und die Design-Tokens |
| `nexy-backend` | API-Handler, Aktionen, WebSocket, ISR, Middleware |
| `nexy-modular` | Controller, Module, Injektion und Schutzvorrichtungen des modularen Routers |
| `nexy-security` | Abhängigkeiten, Eingaben, Sitzungen, Autorisierung, Geheimnisse |
| `nexy-testing` | die Test-First-Schleife und die Tore |
| `nexy-framework-dev` | Nexy selbst ändern, anstatt ein mit Nexy erstelltes Projekt |

Die Regeln, die sie durchsetzen: Überprüfen Sie die Erfahrung, bevor Sie eine Ansicht erstellen, schreiben Sie zuerst den fehlgeschlagenen Test, eine Funktion führt eine Behandlung durch, eine Klasse trägt eine Absicht, ein Ordner enthält einen Satz verwandter Absichten, keine Emojis, echte SVG-Symbole, einfacher Text für Personen und keine handgeschriebenen DOM-Skripte in React, Vue, Svelte, Solid oder Preact.

## Fügen Sie sie einem vorhandenen Projekt hinzu

```bash
nx skills
```

Führen Sie es im Stammverzeichnis des Projekts aus. Es liest `nexyconfig.py` und `package.json`, um den Stapel zu finden, kopiert die passenden Fähigkeiten und schreibt `AGENTS.md` und `CLAUDE.md`, wenn sie fehlen.

Eine von Ihnen geschriebene Datei wird niemals überschrieben: Eine vorhandene Datei `AGENTS.md` oder `CLAUDE.md` wird beibehalten, und der Befehl teilt Ihnen dies mit. Fügen Sie die Fertigkeitsliste manuell zu Ihrer eigenen Datei hinzu, wenn Sie sie dort haben möchten. Eine eigene Fertigkeit in `.claude/skills/` oder `.agents/skills/` bleibt unberücksichtigt; Nur die Fertigkeiten `nexy-*` werden aktualisiert.

Führen Sie `nx skills` erneut aus, nachdem Sie Nexy aktualisiert haben, um die Kopien zu aktualisieren, und übermitteln Sie das Ergebnis, damit das gesamte Team es teilt.

## Wie ein Agent sie findet

- `AGENTS.md` (oder `CLAUDE.md`, das es importiert) wird zu Beginn jeder Sitzung gelesen. Es benennt die Fähigkeiten.
- Jeder Skill beginnt mit einem Namen und einer Beschreibung, die angeben, was er abdeckt und wann er geladen werden muss. Der Agent liest diese zuerst und öffnet einen Skill erst, wenn die Aufgabe übereinstimmt.

Die Fertigkeiten folgen dem offenen [Agent-Fähigkeitenformat](https://agentskills.io/specification), sodass andere Agenten, die `SKILL.md`-Ordner lesen, sie auch verwenden können.

## Was sie nicht tun

Fähigkeiten sagen einem Agenten, wie er arbeiten soll; Sie machen die Ausgabe nicht korrekt. Bewahren Sie Ihre eigenen Schecks auf:

- Lesen Sie, was der Agent geändert hat.
- Führen Sie `nx check`, `nx test` und `nx build` aus. Die Fähigkeiten verlangen dies und verlangen, dass die Ergebnisse gemeldet und nicht zusammengefasst werden.
- Überwachen Sie Abhängigkeiten, die der Agent hinzufügt (`nexy-security` erklärt, wie).

Die Beispiele in den Fertigkeiten werden durch Nexys eigene Tests überprüft: Die Importe existieren, die Konfigurationsfelder existieren, die Befehle existieren, die Python-Analysen. Das fängt Abdrift auf, keine Fehleinschätzung.

## Karte

Ein Agent antwortet schneller, wenn er weiß, auf welcher Seite sich die Antwort befindet.

| Sie benötigen | Lesen Sie |
|---|---|
| das Produkt, auf einer Seite | [README](../README.md) |
| ein Projekt ausführen | [erste Schritte](../getting-started/quick-start.md) |
| die URL einer Datei | [routing](../routing/README.md) |
| dynamische Segmente, Layouts, Fehlerseiten | [Seiten](../routing/fbr/pages/README.md) |
| der aktuelle Pfad, Abfrage, Cookies, Sitzung | [Hooks](../routing/fbr/navigation/hooks.md) |
| um eine Seite zu bearbeiten | [.nexy-Dateien](../views/nexy/README.md) oder [Ansichten](../views/README.md) |
| Markdown oder MDX | [Abschlag](../views/nexy/markdown.md) |
| integrierte HTML-Helfer | [components](../views/nexy/components.md) |
| Rendering-Modus | [SSR](../rendering/ssr.md), [CSR](../rendering/csr.md), [ISR](../rendering/isr.md) |
| a WebSocket | [websocket](../routing/fbr/realtime/websocket.md) |
| Controller und Module | [modular](../routing/modular/README.md) |
| um einen Endpunkt hinzuzufügen | [API](../routing/fbr/handlers/README.md) |
| ein Formular, das von einer Seite | [Aktionen](actions.md) | gepostet wurde
| Warum eine Anfrage fehlgeschlagen ist und welche Seite darauf antwortet | [Ausnahmen](../reference/exceptions.md) |
| Übersetzungen | [i18n](i18n.md) |
| ein Konfigurationsfeld | [config](../reference/config.md) |
| um die App zu testen | [testing](testing.md) |
| der Client-Build | [Frontend](frontend.md) |

## Projektinvarianten

1. `__nexy__/` wird generiert. Bearbeiten Sie es niemals, schreiben Sie es niemals fest. Löschen Sie es, um einen sauberen Build zu erzwingen.
2. Eine Datei pro URL. `index.nexy` und `index.py` für denselben Pfad ist ein Fehler, keine Prioritätsregel.
3. Reservierte Namen in `src/routes/`: `layout.nexy`, `loading.nexy`, `errors.nexy`, `notfound.nexy`, `dependencies.py`, `__init__.py`. Verwenden Sie sie nicht für Inhalte.
4. `.nexy` Frontmatter ist Python, das pro Anfrage ausgeführt wird. Keine Nebenwirkungen auf Modulebene: keine Datei-Handles, keine Datenbankverbindungen, keine Netzwerkaufrufe beim Import.
5. `.py` in `src/routes/` ist ein API-Handler. Methoden sind Funktionsnamen (`GET`, `POST`, ...).
6. Die Konfiguration lebt in `nexyconfig.py`, nicht in Umgebungsvariablen und nicht in verstreuten Konstanten.
7. Autoescaping ist in `.nexy`-Vorlagen deaktiviert: Nicht vertrauenswürdige Werte mit `| e` maskieren.

```bash
nx dev      # development
nx build    # production build
nx start    # production server
nx test     # pytest, --client adds vitest
```

Wenn die Dokumente und der Code nicht übereinstimmen, vertrauen Sie dem Code und sagen Sie Folgendes: `nexy/core/config.py` enthält alle Optionen, `nexy/modules/routers/fbrouter/` die Routing-Regeln, `nexy/modules/compiler/` wie `.nexy` Dateien zu Modulen werden.

## Nächste Schritte

- [CLI](../reference/cli.md): `nx new` und `nx skills`
- [Dateikonventionen](../reference/file-conventions.md): reservierte Namen und Routing-Regeln
- [Glossar](../reference/glossary.md): die Wörter, auf denen diese Regeln basieren
- [Sicherheit](../reference/security.md): Die Version legt die Sicherheitsfähigkeitspunkte fest
