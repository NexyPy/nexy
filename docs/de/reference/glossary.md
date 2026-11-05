# Glossar

Die in diesen Dokumenten verwendeten Wörter, jeweils eine Zeile, in alphabetischer Reihenfolge. Ein Begriff, der mehr als eine Zeile benötigt, hat eine Seite: Folgen Sie dem Link. Informationen dazu, wie die Begriffe zusammenpassen, finden Sie unter [Kernkonzepte](../getting-started/core-concepts.md).

## Bedingungen

| Begriff | In einer Zeile |
|---|---|
| Aktion | eine Python-Funktion mit der Markierung `@Action`, die als `POST` diente und vom Client aus aufrufbar war ([Aktionen](../guides/actions.md)) |
| ASGI | die Schnittstelle Uvicorn spricht, implementiert durch FastAPI und Starlette |
| Client-Modus | `useCSR = True`: Framework-Dateien sind die Routen und der Browser navigiert ([Modi](../routing/fbr/modes.md)) |
| Komponente | ein wiederverwendbarer UI-Baustein, der zum Erstellen einer Ansicht verwendet wird ([Ansichten](../views/README.md)) |
| CSR | Clientseitiges Rendering: Der Browser rendert Seiten nach dem ersten Dokument ([CSR](../rendering/csr.md)) |
| Abhängigkeit | Eine Funktion FastAPI wird vor einem Handler, pro Route oder pro Ordner ausgeführt ([Abhängigkeiten](../routing/fbr/dependencies/README.md)) |
| Dokumentenhülle | die `<html>`, `<head>` und `<body>` um eine Seite herum, Eigentum des nächstgelegenen Layouts oder von Nexy ([Layouts](../routing/fbr/layouts/README.md)) |
| Endpunkt | die einzigartige Kombination einer URL und einer HTTP-Methode ([Ansichten](../views/README.md)) |
| FBR | Dateibasiertes Routing: Eine Datei unter `src/routes/` ist eine Route ([Routing](../routing/fbr/README.md)) |
| Frontmatter | der Python-Block zwischen den beiden `---`-Zeilen einer `.nexy`- oder `.md`-Datei ([.nexy-Dateien](../views/nexy/README.md)) |
| Wache | eine Abhängigkeit, die eine Anfrage ablehnt, indem sie `HTTPException` ([Guards](../routing/modular/guards-and-metadata.md)) auslöst |
| Handler | eine Python-Funktion, die eine HTTP-Anfrage für eine bestimmte Methode verarbeitet ([Ansichten](../views/README.md)) |
| HMR | Hot-Modul-Austausch: Der Entwicklungsserver tauscht die geänderten Module aus, ohne einen vollständigen Neuladen ([Frontend](../guides/frontend.md)) |
| Flüssigkeitszufuhr | Der Browser fügt ein Framework an HTML an, das der Server bereits gesendet hat ([Inseln](../rendering/islands.md)) |
| Insel | eine Client-Komponente, die in einer vom Server gerenderten Seite eingebunden ist ([Inseln](../rendering/islands.md)) |
| ISR | inkrementelle statische Regeneration: eine zwischengespeicherte Seite pro Pfad, im Hintergrund aktualisiert ([ISR](../rendering/isr.md)) |
| Layout | eine `layout.*`-Datei, die die Seiten unterhalb ihres Ordners umschließt ([Layouts](../routing/fbr/layouts/README.md)) |
| Modularer Router | Routen deklariert mit `@Module` und `@Controller` unter `src/apps/` ([modular](../routing/modular/README.md)) |
| Seite | eine über eine URL adressierbare Ressource, die durch eine Datei unter `src/routes/` definiert wird ([Ansichten](../views/README.md)) |
| Vorabholen | Laden der Seite hinter einem Link, bevor der Leser darauf klickt ([Verlinkung](../routing/fbr/navigation/linking-and-navigating.md)) |
| Requisiten | die Werte, die ein übergeordnetes Element an eine Komponente übergibt ([.nexy-Dateien](../views/nexy/README.md)) |
| Erneut validieren | die Anzahl der Sekunden, nach denen eine ISR-Seite im Hintergrund neu erstellt wird ([ISR](../rendering/isr.md)) |
| Route | ein URL-Muster, erzeugt durch den Pfad einer Routendatei ([Routing](../routing/README.md)) |
| Routengruppe | ein Ordner in Klammern, der Routen gruppiert, ohne ein Segment hinzuzufügen ([dynamische Routen](../routing/fbr/pages/dynamic-routes.md)) |
| Routenhandler | die `GET`, `POST`, … Funktion einer `.py` Routendatei ([Handler](../routing/fbr/handlers/README.md)) |
| Servermodus | `useCSR = False`, die Standardeinstellung: Der Server rendert `.nexy`- und `.md`-Seiten ([Modi](../routing/fbr/modes.md)) |
| Geschicklichkeit | ein Ordner mit einem `SKILL.md`, der einem Codierungsagenten einen Teil von Nexy beibringt ([Codierungsagenten](../guides/ai-agents.md)) |
| SSG | statische Site-Generierung; **kein Nexy-Modus**: Der im Voraus erstellte HTML-Code wird immer vom Server zurückgelesen ([Rendering](../rendering/README.md)) |
| SSR | serverseitiges Rendering: Der Server rendert jede Seite für seine Anfrage, und dies ist die Standardeinstellung ([SSR](../rendering/ssr.md)) |
| Ansicht | der Prozess der Erstellung des Antworttextes für eine Seite ([Ansichten](../views/README.md)) |

## Dateien und Ordner

| Name | In einer Zeile |
|---|---|
| `__nexy__/` | generierte Ausgabe: kompilierte Seiten, der Client-Eintrag und der Aktions-Client; nie bearbeitet, nie festgeschrieben |
| `nexyconfig.py` | die Projektkonfiguration, eine Klasse von `use*` Feldern ([Konfiguration](config.md)) |
| `public/` | Dateien, die im Stammverzeichnis bereitgestellt werden, wie zum Beispiel `public/logo.svg` → `/logo.svg` ([Dateikonventionen](file-conventions.md)) |
| `src/apps/` | Controller und Module des modularen Routers ([modular](../routing/modular/README.md)) |
| `src/components/` | Von Seiten importierte Komponenten; leitet niemals weiter ([Dateikonventionen](file-conventions.md)) |
| `src/routes/` | die Routen der Anwendung ([Dateikonventionen](file-conventions.md)) |

## Nächste Schritte

- [Kernkonzepte](../getting-started/core-concepts.md): das Modell, zu dem diese Wörter gehören
- [Dokumentationsindex](../README.md): die Seite für die jeweilige Aufgabe
- [Dateikonventionen](file-conventions.md): die reservierten Namen hinter diesen Definitionen
- [Für KI-Agenten](../guides/ai-agents.md): dieselben Invarianten, geschrieben für einen Agenten
