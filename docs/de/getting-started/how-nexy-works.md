# So funktioniert Nexy

Was passiert zwischen einer Datei, die Sie schreiben, und der Seite im Browser: die Ebenen, die eine Anfrage durchquert, wer was erstellt und was Nexy Ihrer Anwendung überlässt. Sie benötigen diese Seite nicht zum Starten; Es beantwortet später die Fragen „Warum funktioniert das so?“.

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

| Schicht | Verantwortung | Nicht |
|---|---|---|
| Uvicorn | Akzeptieren Sie die Verbindung, sprechen Sie ASGI | wissen, was eine Seite ist |
| Middleware | Dekorieren Sie die Anfrage: Sitzung, CORS, gzip, vertrauenswürdige Hosts, HTTPS-Umleitung, Ihre | Wählen Sie eine Route |
| Router | Ordnen Sie die URL einer Datei mit ihren Layouts, Abhängigkeiten und Fehlerseiten zu | Inhalte produzieren |
| Renderer | Führen Sie die Seite aus und wandeln Sie das Ergebnis in HTML oder JSON um | Rufen Sie Ihre Daten ab |
| Kunde | Vite und Ihr Framework: Bundles, Flüssigkeitszufuhr, Client-Navigation | eine Serveranfrage beantworten |

## Wer baut was?

| Schauspieler | Besitzt | Besitzt nicht |
|---|---|---|
| Nexy | Routing, Server-Rendering, Aktionen, `.nexy` Kompilierung, ein Ursprung | Komponenten, Reaktivität, Daten |
| Vite | Client-Bundles, der Entwicklungsserver, Hot-Reload | Routing, Server-Rendering, Aktionen |
| Ihr Rahmen | Komponenten, Reaktivität, das Ökosystem | Routing, das Dokument (Nexy fragt nach seinem Layout) |
| Ihre Bewerbung | Daten, Authentifizierung, Autorisierung, Geschäftsregeln | Transport, Rendering |

Die Regel hinter der Tabelle: **Nexy erstellt, was es besitzt, und kompiliert niemals, was Vite kompiliert.**

## Das Routing-System

Ein Pfad unter `src/routes/` wird durch vier Regeln zu einer URL:

| Datei | URL |
|---|---|
| `blog/index.nexy` | `/blog` |
| `blog/[slug].nexy` | `/blog/hello` |
| `blog/[...parts].nexy` | `/blog/a/b` |
| `(marketing)/about.nexy` | `/about` |

Die Erweiterung erscheint nie; `index` ist die Route seines Ordners; Ein Ordner in Klammern gruppiert Dateien, ohne ein Segment hinzuzufügen.

Wenn zwei Dinge auf dieselbe URL antworten können, **der zuerst registrierte gewinnt** und Nexy registriert sich immer in dieser Reihenfolge:

1. der Actions-Endpunkt;
2. statische Dateien: `/public`, `/assets`, `/favicon.ico`;
3. ein modulares `APIRouter` (`useRouter`);
4. Dateirouten, die spezifischsten zuerst: statische Pfade, dann dynamische Pfade mit den meisten festen Segmenten, dann Catch-Alls.

Zwei Dateirouten gleicher Spezifität werden in alphabetischer Pfadreihenfolge registriert, sodass `[id].nexy` vor `[slug].nexy` antwortet. Eine modulare Route übertrifft daher eine Seite mit demselben Pfad. Dies ist eine Rangfolge, auf die Sie sich verlassen können, und keine Tie-Break-Regel, mit der Sie spielen können: Geben Sie einer URL eine Datei.

## Das Ansichtssystem

Die Erweiterung einer Datei entscheidet darüber, um was es sich handelt, und die Projektkonfiguration entscheidet, welche Erweiterungen aktiv sind.

| Erweiterung | Aktiv wann | Zusammengestellt von | Serviert als |
|---|---|---|---|
| `.nexy` | Servermodus | Nexy: Frontmatter wird zu Python, das Markup wird zu Jinja2 | eine Seite |
| `.md` | immer | Nexy: GitHub-angepasst Markdown, Überschriften-IDs, Inhaltsverzeichnis | eine Seite, innerhalb des nächstgelegenen Layouts |
| `.mdx` | immer | Vite, mit React oder Preact | eine Komponentenroute |
| `.tsx` | `useFF` ist React, Solid oder Preact | Vite und das Framework | eine Komponentenroute |
| `.vue` | `useFF` ist Vue | Vite und Vue | eine Komponentenroute |
| `.svelte` | `useFF` ist Svelte | Vite und Svelte | eine Komponentenroute |
| `.py` | immer | Python | ein API-Handler: `GET`, `POST`, ... sind die Methoden |

Eine Datei, deren Erweiterung nicht aktiv ist, wird mit einer Warnung übersprungen und nicht bereitgestellt. Im Client-Modus wird `.nexy` abgelehnt, bevor der Server startet. Siehe [Dateikonventionen](../reference/file-conventions.md).

## Der Rendering-Lebenszyklus

Drei Fragen entscheiden über alles, was dem Leser auffällt:

| Frage | Antwort | Seite |
|---|---|---|
| Wer erstellt den HTML-Code? | der Server oder der Browser für eine Client-Route | [Rendern](../rendering/README.md) |
| Wann werden die Daten gelesen? | bei jeder Anfrage, bei jeder Neugenerierung oder im Browser | [SSR](../rendering/ssr.md), [ISR](../rendering/isr.md) |
| Wann kommt JavaScript? | nur für eine Insel oder für das gesamte Dokument | [Inseln](../rendering/islands.md), [CSR](../rendering/csr.md) |

Im Servermodus rendert der Server jede Seite, `revalidate` speichert eine Seite pro URL im Cache und Inseln fügen JavaScript zu einer Komponente hinzu. Im Client-Modus wird das erste Dokument in Node gerendert und die Navigation erfolgt dann im Browser.

`__nexy__/` enthält alles Generierte: kompilierte Seiten, den Client-Eintrag, die Build-Ausgabe. Bearbeiten Sie es niemals, schreiben Sie es niemals fest; Löschen Sie es, um einen sauberen Build zu erzwingen.

## Die Frontend-Integration

**Vite ersetzt Nexy nicht.** Vite bündelt und stellt Client-Code bereit. Es leitet keine Anfrage weiter, rendert keine `.nexy`-Seite, führt keine Aktion aus und besitzt keinen Ursprung. Der Browser kommuniziert mit einem Ursprung – Nexys – und in der Entwicklung stellt Nexy Vites Endpunkte darüber als Proxy bereit, sodass kein CORS konfiguriert werden muss.

**Nexy ersetzt nicht React.** Nexy entscheidet, welche Komponente wann und mit welchen Requisiten gerendert wird; Das Framework besitzt das Komponentenmodell, die Reaktivität und das Ökosystem. Eine `.nexy`-Seite importiert eine Komponente als Insel; Im Client-Modus ist eine Route eine Komponente.

Für eine Komponentenroute schreibt Python nur ein Thin-Wrapper-Modul, das auf die Datei zeigt. Die Kompilierung und das serverseitige Rendering sind Aufgabe von Vite.

## Entwicklung und Produktion

`nx dev` prüft `nexyconfig.py`, kompiliert die Seiten, startet Vite, wenn das Projekt über ein Frontend-Framework verfügt, und startet den Server neu, wenn Sie speichern. `nx build` erledigt die gleiche Arbeit einmal im Voraus und `nx start` liefert das Ergebnis.

| | `nx dev` | `nx build` dann `nx start` |
|---|---|---|
| Seiten | beim Speichern kompiliert | Einmal im Voraus zusammengestellt |
| Kundencode | Vite Entwicklungsserver mit Hot-Reload, hinter Nexys eigenem Ursprung | Bundle in `__nexy__/client/`, vorgerendertes HTML |
| Node.js | läuft neben Python | zum Servieren nicht nötig |
| Fehler | Overlay im Browser, Symbolleiste auf jeder Seite | Statusseiten ohne Details |
| Herkunft | ein Port, `3000` | ein Port |

Was sich nicht ändert: die gleichen Routing-Regeln, die gleichen Auslagerungsdateien, die gleichen `nexyconfig.py`. Eine Seite, die sich bei beiden unterschiedlich verhält, ist ein Fehler, kein Modus.

## Was Nexy Ihnen überlässt

Nexy stoppt absichtlich am Rand Ihrer Anwendung:

| Sorge | Was Nexy bietet | Was du schreibst |
|---|---|---|
| Authentifizierung | Sitzungs-Middleware, `AuthenticationMiddleware`, wenn aktiviert | die Anmeldung, die Benutzersuche, die Cookie-Richtlinie |
| Autorisierung | `dependencies.py`, Wächter, Vererbung pro Ordner | die Regel selbst |
| Datenbank | kein eigenes ORM; `nx new` kann ein Gerüst bilden für SQLModel, SQLAlchemy oder Tortoise, `nx migrate` läuft Alembic oder Aerich | die Modelle und die Abfragen ([Datenbanken](../guides/databases.md)) |
| Internationalisierung | nichts für Ihre Seiten; nur die CLI wird übersetzt | die Bibliothek und die Nachrichten ([i18n](../guides/i18n.md)) |
| Hintergrundjobs | nichts: keine Warteschlange, kein Planer | ein Arbeitsprozess |
| E-Mail, Zahlungen, Suche | nichts | den Service, den Sie wählen |

Der Grund ist für alle sechs derselbe: Ein Framework, das Ihr ORM oder Ihre Authentifizierungsbibliothek auswählt, entscheidet über Dinge, die nur Ihre Anwendung entscheiden kann. Die Kosten liegen auf der Hand: Sie müssen nichts verkabeln, und in den in der Tabelle verlinkten Anleitungen ist angegeben, wo die einzelnen Anschlüsse angeschlossen werden müssen.

## Nächste Schritte

- [Projektstruktur](project-structure.md): Wo jeder Teil in einem Projekt lebt
- [Routing](../routing/README.md): die dateibasierten, modularen und benutzerdefinierten Router
- [Rendering](../rendering/README.md): SSR, ISR, CSR und Inseln
- [Frontend](../guides/frontend.md): Vite, Styling und der Client-Build
