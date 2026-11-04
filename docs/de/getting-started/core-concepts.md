# Kernkonzepte

Das mentale Modell vor der API: vier Leseebenen, dann die Vorstellungen, die auf jeder zurückkommen
Seite. Jeder Begriff erhält hier eine Zeile und einen Link zu der Seite, die tiefer geht.

## So lesen Sie diese Dokumente

| Level | Die Frage, die es beantwortet | Beginnen Sie mit |
|---|---|---|
| Anwendungsarchitektur | welche Schicht eine Anfrage beantwortet und was sie ablehnt | [Architektur](../architecture.md) |
| Anwendungsstruktur | wo sich der Code befindet und was aus einer Datei wird | [Projektstruktur](project-structure.md) |
| Präsentation und Wiedergabe | was der Leser sieht und wer das HTML erstellt | [Ansichten](../views/README.md), [Wiedergabe](../rendering/README.md) |
| Anwendungsinteraktion | was der Leser tut und was als Antwort ausgeführt wird | [Aktionen](../guides/actions.md) |

Die Level werden in dieser Reihenfolge einmal gelesen. Danach handelt es sich bei der Seite, die Sie benötigen, um eine Nachschlageseite und nicht um einen Kurs.

## Anwendungsarchitektur

Drei Möglichkeiten, um zu entscheiden, welcher Code auf eine URL antwortet. Es handelt sich um Alternativen, nicht um Schichten:

- **Dateibasiertes Routing (FBR)**: Eine Datei unter `src/routes/` ist eine Route. Die Standardeinstellung.
- **Modularer Router**: Controller und Module unter `src/apps/`, deklariert mit Dekoratoren, für a
  Codebasis im NestJS-Stil.
- **Benutzerdefinierter Router**: eine vorhandene FastAPI `APIRouter`, die in der Anwendung enthalten ist.

Sich für einen der drei zu entscheiden, ist eine Entscheidung. Die Wahl eines Frontend-Frameworks ist eine andere, separate Angelegenheit:
siehe [Wählen Sie einen Router](../routing/README.md) und [Ansichten](../views/README.md).

## Anwendungsstruktur

Fünf Vorstellungen, die ein Leser, der von Next.js kommt, normalerweise zu einer vereint. Sie sind nicht dasselbe,
und der Unterschied erklärt die meisten Fragen zum Thema „Warum wird meine Seite nicht gerendert“.

| Begriff | Was es ist | Was es nicht ist |
|---|---|---|
| **Route** | ein URL-Muster, erzeugt durch den Pfad einer Datei | eine Datei: eine Datei kann auf mehrere URLs antworten (`[slug]`) |
| **Seite** | eine Routendatei, die eine Ansicht rendert: `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | ein Endpunkt: Er antwortet auf ein Dokument, nicht auf Daten |
| **Ansicht** | was den Hauptteil einer Seite erzeugt: Jinja2 und Python, Markdown oder eine Client-Komponente | eine Route: die gleiche Ansicht kann mehrere Seiten bedienen |
| **Komponente** | ein wiederverwendbares Stück, eine Seite importiert | eine Route: Im Servermodus wird eine Komponente niemals alleine bereitgestellt |
| **Routenhandler** | die Funktion einer `.py` Routendatei, benannt nach der HTTP-Methode (`GET`, `POST`, …) | eine Seite: Sie gibt JSON, eine Datei oder eine `Response` | zurück
| **Endpunkt** | das Paar (URL, Methode), auf das ein Handler antwortet | ein Handler: Eine Datei kann mehrere Endpunkte beantworten |

In einem Satz: **Eine Seite ist eine Routendatei, eine Ansicht ist das, was sie rendert, eine Komponente ist was eine Seite
Wiederverwendung, ein Handler antwortet auf einen Endpunkt.**

Zwei weitere Wörter, die überall wiederkehren:

- **Layout**: eine `layout.*`-Datei, die die Seiten unter ihrem Ordner umschließt; Der Root besitzt den HTML-Code
  Dokument. Siehe [Layouts](../routing/fbr/layouts/README.md).
- **Abhängigkeit**: eine Funktion, die vor einem Handler ausgeführt wird und pro Route oder pro Ordner angewendet wird. Siehe
  [Abhängigkeiten](../routing/fbr/dependencies/README.md).

## Präsentation und Rendering

Zwei unabhängige Entscheidungen, oft verwechselt:

- **Das Format** entscheidet, welche Datei die Seite rendert: [Ansichten](../views/README.md).
- **Der Modus** entscheidet, wer den HTML-Code wann produziert: [Rendering](../rendering/README.md).

| Begriff | Eine Zeile |
|---|---|
| Servermodus | Der Server rendert `.nexy` und `.md` Seiten; Komponenten sind Inseln ([modes](../routing/fbr/modes.md)) |
| Client-Modus | `useCSR = True`: Framework-Dateien sind die Routen, und die Navigation erfolgt im Browser |
| SSR, ISR, CSR, Inseln | vier Rendering-Modi, entschieden pro Seite, außer CSR, das pro Projekt gilt ([rendering](../rendering/README.md)) |
| Hydration | Der Browser fügt ein Framework an HTML an, das der Server bereits gesendet hat ([islands](../rendering/islands.md)) |
| Props | die Werte, die ein übergeordnetes Element an eine Komponente übergibt, deklariert `name: prop[type]` in einer `.nexy`-Datei ([.nexy-Dateien](../views/nexy/README.md)) |

## Anwendungsinteraktion

| Begriff | Eine Zeile |
|---|---|
| Aktion | eine mit `@Action` gekennzeichnete Python-Funktion, die als `POST` diente und aus einem Formular oder als typisierte Funktion aufgerufen werden konnte ([actions](../guides/actions.md)) |
| Formular | ein HTML-Formular, das an eine Aktion sendet, wobei Validierungsfehler auf die Seite zurückkommen ([actions](../guides/actions.md)) |
| Navigations-| Links zum Vorabrufen und Hooks, die den Pfad, die Abfrage, die Cookies und die Sitzung lesen ([hooks](../routing/fbr/navigation/hooks.md)) |
| Datenabruf | erfolgt durch die Seite oder den Handler, der sie benötigt; Nexy liefert keine Client-Datenschicht ([Handler](../routing/fbr/handlers/README.md)) |

## Was Nexy nicht macht

Authentifizierung, Autorisierung, Datenbank, Internationalisierung, Hintergrundjobs, E-Mail, Zahlungen und
Die Suche liegt **in der Verantwortung Ihrer Anwendung**, nicht in der des Frameworks. Nexy gibt die Verlängerung
zeigt und sagt, wo jedes einzelne eingesteckt werden soll: siehe [die Grenzen](../architecture.md#boundaries).

Der Grund dafür ist nicht Minimalismus als Selbstzweck: ein Framework, das Ihr ORM oder Ihre Authentifizierungsbibliothek auswählt
hat etwas entschieden, über das nur Ihre Bewerbung entscheiden kann.

## Nächste Schritte

- [Architektur](../architecture.md): die Schichten und wer was baut
- [Projektstruktur](project-structure.md): jeder Ordner und jede Datei eines Projekts
- [Glossar](../reference/glossary.md): die gleichen Wörter, in einem alphabetischen Index
- [Wie Nexy funktioniert](how-nexy-works.md): eine Anfrage, Schritt für Schritt