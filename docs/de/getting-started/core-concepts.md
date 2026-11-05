# Kernkonzepte

Die Wörter, die in den übrigen Dokumenten verwendet werden – Route, Seite, Ansicht, Komponente, Handler, Endpunkt – jeweils in einer Zeile, mit einem Link zu der Seite, die tiefer geht. Neu bei Nexy? Beginnen Sie mit [Was ist Nexy?](what-is-nexy.md).

## So lesen Sie diese Dokumente

| Ebene | Die Frage, die es beantwortet | Beginnen Sie mit |
|---|---|---|
| Anwendungsarchitektur | welche Schicht eine Anfrage beantwortet und was sie ablehnt | [Wie Nexy funktioniert](how-nexy-works.md) |
| Anwendungsstruktur | wo sich der Code befindet und was aus einer Datei wird | [Projektstruktur](project-structure.md) |
| Präsentation und Rendering | was der Leser sieht und wer den HTML-Code erstellt | [Ansichten](../views/README.md), [Rendering](../rendering/README.md) |
| Anwendungsinteraktion | was der Leser tut und was als Reaktion darauf ausgeführt wird | [Aktionen](../guides/actions.md) |

Die Level werden in dieser Reihenfolge einmal gelesen. Danach handelt es sich bei der Seite, die Sie benötigen, um eine Nachschlageseite und nicht um einen Kurs.

## Anwendungsarchitektur

Drei Möglichkeiten, um zu entscheiden, welcher Code auf eine URL antwortet. Es handelt sich um Alternativen, nicht um Schichten:

- **Dateibasiertes Routing (FBR)**: Eine Datei unter `src/routes/` ist eine Route. Die Standardeinstellung.
- **Modularer Router**: Controller und Module unter `src/apps/`, deklariert mit Dekoratoren, für eine Codebasis im NestJS-Stil.
- **Benutzerdefinierter Router**: ein vorhandener FastAPI `APIRouter`, der in der Anwendung enthalten ist.

Sich für einen der drei zu entscheiden, ist eine Entscheidung. Die Auswahl eines Frontend-Frameworks ist eine andere, separate Angelegenheit: siehe [Router auswählen](../routing/README.md) und [Ansichten](../views/README.md).

## Anwendungsstruktur

Fünf Vorstellungen, die ein Leser aus Next.js normalerweise zu einer einzigen vereint. Sie sind nicht dasselbe und der Unterschied erklärt die meisten Fragen zum Thema „Warum wird meine Seite nicht gerendert“.

| Vorstellung | Was es ist | Was es nicht ist |
|---|---|---|
| **Route** | ein URL-Muster, das durch den Pfad einer Datei erzeugt wird | eine Datei: Eine Datei kann auf mehrere URLs antworten (`[slug]`) |
| **Seite** | eine Routendatei, die eine Ansicht rendert: `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | ein Endpunkt: Er antwortet auf ein Dokument, nicht auf Daten |
| **Anzeigen** | Was erzeugt den Hauptteil einer Seite: Jinja2 und Python, Markdown oder eine Client-Komponente | eine Route: Die gleiche Ansicht kann mehrere Seiten bedienen |
| **Komponente** | ein wiederverwendbarer Teil, den eine Seite importiert | eine Route: Im Servermodus wird eine Komponente niemals alleine bedient |
| **Routenhandler** | die Funktion einer `.py`-Routendatei, benannt nach der HTTP-Methode (`GET`, `POST`, …) | eine Seite: Sie gibt JSON, eine Datei oder ein `Response` zurück. |
| **Endpunkt** | das Paar (URL, Methode), auf das ein Handler antwortet | ein Handler: Eine Datei kann mehrere Endpunkte beantworten |

In einem Satz: **Eine Seite ist eine Routendatei, eine Ansicht ist das, was sie rendert, eine Komponente ist das, was eine Seite wiederverwendet, ein Handler antwortet einem Endpunkt.**

Zwei weitere Wörter, die überall wiederkehren:

- **Layout**: eine `layout.*`-Datei, die die Seiten unterhalb ihres Ordners umschließt; Der Root besitzt das HTML-Dokument. Siehe [Layouts](../routing/fbr/layouts/README.md).
- **Abhängigkeit**: eine Funktion, die vor einem Handler ausgeführt wird und pro Route oder pro Ordner angewendet wird. Siehe [Abhängigkeiten](../routing/fbr/dependencies/README.md).

## Präsentation und Rendering

Zwei unabhängige Entscheidungen, oft verwechselt:

- **Das Format** entscheidet, welche Datei die Seite rendert: [Ansichten](../views/README.md).
- **Der Modus** entscheidet, wer wann den HTML-Code produziert: [Rendering](../rendering/README.md).

| Vorstellung | Eine Zeile |
|---|---|
| Servermodus | Der Server rendert die Seiten `.nexy` und `.md`. Komponenten sind Inseln ([Modi](../routing/fbr/modes.md)) |
| Client-Modus | `useCSR = True`: Framework-Dateien sind die Routen, und die Navigation erfolgt im Browser |
| SSR, ISR, CSR, Inseln | vier Rendering-Modi, die pro Seite festgelegt werden, mit Ausnahme von CSR, das pro Projekt gilt ([Rendering](../rendering/README.md)) |
| Flüssigkeitszufuhr | Der Browser fügt ein Framework an HTML an, das der Server bereits gesendet hat ([Inseln](../rendering/islands.md)) |
| Requisiten | die Werte, die ein übergeordnetes Element an eine Komponente übergibt, deklariert `name: prop[type]` in einer `.nexy`-Datei ([.nexy-Dateien](../views/nexy/README.md)) |

## Anwendungsinteraktion

| Vorstellung | Eine Zeile |
|---|---|
| Aktion | eine Python-Funktion mit der Markierung `@Action`, die als `POST` diente und über ein Formular oder als typisierte Funktion aufgerufen werden konnte ([Aktionen](../guides/actions.md)) |
| Formular | ein HTML-Formular, das an eine Aktion sendet, wobei Validierungsfehler auf die Seite zurückkommen ([Aktionen](../guides/actions.md)) |
| Navigation | Links, die vorab abrufen, und Hooks, die den Pfad, die Abfrage, die Cookies und die Sitzung lesen ([Hooks](../routing/fbr/navigation/hooks.md)) |
| Datenabruf | wird von der Seite oder dem Handler erledigt, der es benötigt; Nexy liefert keine Client-Datenschicht ([Handler](../routing/fbr/handlers/README.md)) |

## Was Nexy nicht macht

Authentifizierung, Autorisierung, Datenbank, Internationalisierung, Hintergrundjobs, E-Mail, Zahlungen und Suche liegen **in der Verantwortung Ihrer Anwendung**, nicht in der des Frameworks. Nexy gibt die Erweiterungspunkte an und sagt, wo sie jeweils angeschlossen werden müssen: siehe [Was Nexy Ihnen hinterlässt](how-nexy-works.md#what-nexy-leaves-to-you).

Der Grund dafür ist nicht Minimalismus an sich: Ein Framework, das Ihr ORM oder Ihre Authentifizierungsbibliothek auswählt, hat etwas entschieden, über das nur Ihre Anwendung entscheiden kann.

## Nächste Schritte

- [Projektstruktur](project-structure.md): jeder Ordner und jede Datei eines Projekts
- [Glossar](../reference/glossary.md): dieselben Wörter in einem alphabetischen Index
- [Wie Nexy funktioniert](how-nexy-works.md): die Schichten, wer was baut und was Nexy Ihnen überlässt
