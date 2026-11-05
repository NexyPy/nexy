# Architektur

## Definition

Nexy besteht aus fünf Schichten, und jede hat eine Aufgabe, die die anderen nicht erledigen. Die Kenntnis der Grenze beantwortet die meisten „Warum funktioniert das so?“-Fragen: Eine langsame Seite ist eine Renderer-Frage, eine falsche Seite ist eine Router-Frage, eine Seite, die nie erscheint, ist eine Client-Frage.

Diese Seite richtet sich an Personen, die eine Bewerbung schreiben. Die Pakete von Nexy selbst und die Mechanismen dahinter werden für Mitwirkende in `ARCHITECTURE.md` im Repository-Stammverzeichnis beschrieben.

## Die Schichten

```diagram filename="Eine Anfrage, fünf Schichten"
Browser
   │
   ▼
Uvicorn ───── ASGI transport
   │
   ▼
Middleware ── sessions, CORS, gzip, trusted hosts, your own
   │
   ▼
Router ────── FBR | Modular | Custom ── picks the file that answers
   │
   ▼
Renderer ──── HTML (Jinja2, Markdown, Node) or JSON
   │
   ▼
Response
```

| Ebene | Verantwortung | Nicht |
|---|---|---|
| Uvicorn | die Verbindung akzeptieren, ASGI sprechen | wissen, was eine Seite ist |
| Middleware | dekoriert die Anfrage: Sitzung, CORS, gzip, vertrauenswürdige Hosts, HTTPS-Umleitung, Ihre | wählen Sie eine Route |
| Router | ordnet die URL einer Datei zu, wobei deren Layouts, Abhängigkeiten und Fehlerseiten | Inhalte erzeugen |
| Der Renderer | führt die Seite aus und wandelt das Ergebnis in HTML oder JSON um | ruft Ihre Daten ab |
| Client | Vite und Ihr Framework: Bundles, Hydratation, Client-Navigation | beantworten eine Serveranfrage |

## Wer baut was?

| Schauspieler | Besitzt | Besitzt nicht |
|---|---|---|
| Nexy | Routing, Server-Rendering, Aktionen, `.nexy` Kompilierung, Komponenten mit einem Ursprung | Reaktivität, Daten |
| Vite | Client-Bundles, der Entwicklungsserver, Hot-Reload | Routing, Server-Rendering, Aktionen |
| Ihr Framework | Komponenten, Reaktivität, das Ökosystem | Routing, das Dokument (Nexy fragt nach seinem Layout) |
| Ihre Anwendungsdaten | Authentifizierung, Autorisierung, Geschäftsregeln | Transport, Rendering |

Die Regel hinter der Tabelle: **Nexy erstellt, was es besitzt, und kompiliert niemals, was Vite kompiliert.** Für eine Komponentenroute schreibt Python ein Thin-Wrapper-Modul, das auf die Datei zeigt.

## Wo über einen Antrag entschieden wird

1. Middleware wird ausgeführt und kann die Anforderung ändern oder stoppen.
2. Der Router wählt eine Datei und die umliegenden Layouts aus.
3. Der Renderer führt diese Datei mit den Daten aus, die er selbst liest.
4. Die Antwort geht zurück und die Client-Ebene übernimmt, wenn die Seite JavaScript hat.

Jeder Schritt mit der genauen Rangfolge zwischen Routern und der Reihenfolge von `nx dev` finden Sie in [Funktionsweise von Nexy](getting-started/how-nexy-works.md). Diese Seite wiederholt es nicht.

## Entwicklung und Produktion

Die gleichen fünf Schichten, zweimal zusammengesetzt:

| Ebene | `nx dev` | `nx build`, dann `nx start` |
|---|---|---|
| Compiler | wird ausgeführt, wenn Sie speichern | wird einmal ausgeführt, vorzeitig |
| Vite | Entwicklungsserver, Hot-Reload, Proxy über Nexys Ursprungs-|-Bundle geschrieben auf `__nexy__/client/`, kein Entwicklungsserver |
| Knoten | rendert Client-Dokumente bei Bedarf | rendert sie beim Build, nicht während der Bereitstellung |
| Beobachter | startet Uvicorn bei Änderung neu | abwesend |
| Ursprung | ein Port | ein Port |

Was sich ändert, ist, *wann* Arbeit stattfindet, nicht, *wer* sie ausführt. Wenn sich eine Seite unterschiedlich verhält, handelt es sich um einen Fehler in der Seite und nicht um eine Eigenschaft des Modus.

## Grenzen

Nexy stoppt absichtlich am Rand Ihrer Anwendung:

| Anliegen | Was Nexy bietet | Was Sie schreiben |
|---|---|---|
| Authentifizierung | Sitzungs-Middleware, `AuthenticationMiddleware` wenn aktiviert | die Anmeldung, die Benutzersuche, die Cookie-Richtlinie |
| Autorisierung | `dependencies.py`, Wächter, Vererbung pro Ordner | die Regel selbst |
| Datenbank | nichts: kein ORM, keine Migrationen | die Modellebene ([Datenbanken](guides/databases.md)) |
| Internationalisierung | nichts für Ihre Seiten; nur die CLI wird übersetzt | die Bibliothek und die Nachrichten ([i18n](guides/i18n.md)) |
| Hintergrundjobs | nichts: keine Warteschlange, kein Scheduler | ein Worker-Prozess |
| E-Mail, Zahlungen, Suche | nichts | der von Ihnen gewählte Dienst |

Der Grund ist für alle sechs derselbe: Ein Framework, das Ihr ORM oder Ihre Authentifizierungsbibliothek auswählt, entscheidet über Dinge, die nur Ihre Anwendung entscheiden kann. Die Kosten liegen auf der Hand: Für Sie ist nichts verkabelt, und auf den Anleitungsseiten oben steht, wo die einzelnen Anschlüsse angeschlossen werden müssen.

## Nächste Schritte

- [Wie Nexy funktioniert](getting-started/how-nexy-works.md): eine Anfrage, Schritt für Schritt
- [Projektstruktur](getting-started/project-structure.md): Wo jede Ebene in einem Projekt lebt
- [Routing](routing/README.md): Die drei Router und wie man sie auswählt
- [Rendering](rendering/README.md): Woher kommt der HTML-Code?
