# So funktioniert Nexy

Das mentale Modell auf einer Seite: Was Nexy erstellt, was Vite erstellt und was zwischen einer Datei und einer Seite in Ihrem Browser passiert. Lesen Sie es einmal; Der Rest der Dokumentation besteht dann aus einer Reihe von Details.

## Die Nexy-Architektur

Eine Anfrage durchquert fünf Ebenen: Uvicorn akzeptiert sie, Middleware dekoriert sie, der Router wählt eine Datei aus, der Renderer wandelt diese Datei in HTML oder JSON um und die Client-Ebene übernimmt, wenn die Seite über JavaScript verfügt. Nexy besitzt die mittleren drei; Vite und Ihr Framework besitzen den Client; Ihre Anwendung besitzt die Daten, die Authentifizierung und die Autorisierung.

Jede Schicht und was sie nicht tut, befindet sich in der [Architektur](../architecture.md). Informationen zu den Paketen von Nexy selbst finden Sie unter `ARCHITECTURE.md` im Repository-Stammverzeichnis – es ist für Mitwirkende geschrieben.

## Der Anwendungslebenszyklus

`nx dev` führt vor der ersten Anfrage sechs Dinge aus:

1. validiert `nexyconfig.py` und stoppt bei einer ungültigen Konfiguration;
2. stellt sicher, dass die Python-Pakete des Projekts importierbar sind;
3. löst die Ports auf und löscht die veraltete `__nexy__/nexy.prod`-Markierung;
4. generiert die Client-Dateien und kompiliert parallel die Routen;
5. startet Vite und wartet, bis es antwortet;
6. Installiert den Datei-Watcher und lässt dann uvicorn `nexy.modules.routers.app:_server` importieren.

Durch diesen Import wird die Anwendung assembliert – Middleware, Aktionen, Router, Fehlerhandler – und die erste Anfrage wird von dieser Assembly bedient. Wenn Sie speichern, startet der Watcher uvicorn neu. Eine Seite, die angezeigt, verschwunden oder verschoben wurde, generiert auch die Client-Routenliste neu.

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

| Erweiterung | Aktiv, wenn | zusammengestellt von | serviert als |
|---|---|---|---|
| `.nexy` | Servermodus | Nexy: Frontmatter wird zu Python, das Markup wird zu Jinja2 | eine Seite |
| `.md` | immer | Nexy: GitHub-Geschmack Markdown, Überschriften-IDs, Inhaltsverzeichnis | eine Seite, innerhalb des nächstgelegenen Layouts |
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
| Wer erstellt den HTML-Code? | der Server oder der Browser für eine Client-Route | [Rendering](../rendering/README.md) |
| Wann werden die Daten gelesen? | bei jeder Anfrage, bei jeder Regeneration oder im Browser | [SSR](../rendering/ssr.md), [ISR](../rendering/isr.md) |
| Wann kommt JavaScript? | nur für eine Insel oder für das gesamte Dokument | [Inseln](../rendering/islands.md), [CSR](../rendering/csr.md) |

Im Servermodus rendert der Server jede Seite, `revalidate` speichert eine Seite pro URL im Cache und Inseln fügen JavaScript zu einer Komponente hinzu. Im Client-Modus wird das erste Dokument in Node gerendert und die Navigation erfolgt dann im Browser.

`__nexy__/` enthält alles Generierte: kompilierte Seiten, den Client-Eintrag, die Build-Ausgabe. Bearbeiten Sie es niemals, schreiben Sie es niemals fest; Löschen Sie es, um einen sauberen Build zu erzwingen.

## Die Frontend-Integration

**Vite ersetzt Nexy nicht.** Vite bündelt und stellt Client-Code bereit. Es leitet keine Anfrage weiter, rendert keine `.nexy` Seite, führt keine Aktion aus und besitzt keinen Ursprung. Der Browser kommuniziert mit einem Ursprung – Nexys – und in der Entwicklung stellt Nexy Vites Endpunkte darüber als Proxy bereit, sodass kein CORS konfiguriert werden muss.

**Nexy ersetzt nicht React.** Nexy entscheidet, welche Komponente wann und mit welchen Requisiten gerendert wird; Das Framework besitzt das Komponentenmodell, die Reaktivität und das Ökosystem. Eine `.nexy`-Seite importiert eine Komponente als Insel; Im Client-Modus ist eine Route eine Komponente.

Für eine Komponentenroute schreibt Python nur ein Thin-Wrapper-Modul, das auf die Datei zeigt. Die Kompilierung und das serverseitige Rendering sind Aufgabe von Vite.

## Entwicklung und Produktion

| | `nx dev` | `nx build` dann `nx start` |
|---|---|---|
| Seiten | werden beim Speichern zusammengestellt | werden einmalig im Voraus zusammengestellt |
| Client-Code | Vite Entwicklungsserver mit Hot-Reload, hinter Nexys eigenem Ursprungs-|-Bundle in `__nexy__/client/`, vorgerendertes HTML |
| Node.js | läuft neben Python | wird nicht benötigt, um | zu dienen
| Fehler | Einblendung im Browser, Symbolleiste auf jeder Seite | Statusseiten ohne Details |
| Ursprung | ein Hafen, `3000` | ein Hafen |

Was sich nicht ändert: die gleichen Routing-Regeln, die gleichen Auslagerungsdateien, die gleichen `nexyconfig.py`. Eine Seite, die sich bei beiden unterschiedlich verhält, ist ein Fehler, kein Modus.

## Tiefer gehen

- [Projektstruktur](project-structure.md): jeder Ordner eines Projekts
- [Rendering](../rendering/README.md): SSR, ISR, CSR und Inseln
- [Frontend](../guides/frontend.md): Vite, Styling und der Client-Build
- [Routing](../routing/README.md): die dateibasierten, modularen und benutzerdefinierten Router
