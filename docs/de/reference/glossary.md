# Glossar

Die in diesen Dokumenten verwendeten Wörter, jeweils eine Zeile, in alphabetischer Reihenfolge. Ein Begriff, der mehr als eine Zeile benötigt, hat eine Seite: Folgen Sie dem Link. Informationen dazu, wie die Begriffe zusammenpassen, finden Sie unter [Kernkonzepte](../getting-started/core-concepts.md).

## Bedingungen

| Begriff | In einer Zeile |
|---|---|
| Aktion | eine Python-Funktion mit der Markierung `@Action`, die als `POST` diente und vom Client aus aufrufbar war ([Aktionen](../guides/actions.md)) |
| ASGI | die Schnittstelle Uvicorn spricht, implementiert durch FastAPI und Starlette |
| Client-Modus | `useCSR = True`: Framework-Dateien sind die Routen und der Browser navigiert ([modes](../routing/fbr/modes.md)) |
| Komponente | ein wiederverwendbarer UI-Baustein, der zum Erstellen einer Ansicht verwendet wird ([views](../views/README.md)) |
| CSR | clientseitiges Rendering: Der Browser rendert Seiten nach dem ersten Dokument ([CSR](../rendering/csr.md)) |
| Abhängigkeit | Eine Funktion FastAPI wird vor einem Handler, pro Route oder pro Ordner ausgeführt ([Abhängigkeiten](../routing/fbr/dependencies/README.md)) |
| Dokumenthülle | die `<html>`, `<head>` und `<body>` um eine Seite, Eigentum des nächstgelegenen Layouts oder von Nexy ([layouts](../routing/fbr/layouts/README.md)) |
| Endpunkt | die einzigartige Kombination aus einer URL und einer HTTP-Methode ([views](../views/README.md)) |
| FBR | dateibasiertes Routing: Eine Datei unter `src/routes/` ist eine Route ([routing](../routing/fbr/README.md)) |
| Frontmatter | der Python-Block zwischen den beiden `---`-Zeilen einer `.nexy`- oder `.md`-Datei ([.nexy-Dateien](../views/nexy/README.md)) |
| Bewachen Sie | eine Abhängigkeit, die eine Anfrage ablehnt, indem Sie `HTTPException` ([guards](../routing/modular/guards-and-metadata.md)) | auslösen.
| Handler | eine Python Funktion, die eine HTTP-Anfrage für eine bestimmte Methode verarbeitet ([views](../views/README.md)) |
| HMR | Hot-Modul-Austausch: Der Entwicklungsserver tauscht die geänderten Module aus, ohne einen vollständigen Neuladen ([frontend](../guides/frontend.md)) |
| Hydration | Der Browser fügt ein Framework an HTML an, das der Server bereits gesendet hat ([islands](../rendering/islands.md)) |
| Island | eine Client-Komponente, die in einer vom Server gerenderten Seite eingebunden ist ([islands](../rendering/islands.md)) |
| ISR | inkrementelle statische Regeneration: eine zwischengespeicherte Seite pro Pfad, aktualisiert im Hintergrund ([ISR](../rendering/isr.md)) |
| Layout | eine `layout.*`-Datei, die die Seiten unterhalb ihres Ordners umschließt ([layouts](../routing/fbr/layouts/README.md)) |
| Modulare Router | Routen deklariert mit `@Module` und `@Controller` unter `src/apps/` ([modular](../routing/modular/README.md)) |
| Seite | eine URL-adressierbare Ressource, die durch eine Datei unter `src/routes/` ([views](../views/README.md)) | definiert ist
| Prefetch | lädt die Seite hinter einem Link, bevor der Leser darauf klickt ([linking](../routing/fbr/navigation/linking-and-navigating.md)) |
| Props | die Werte, die ein übergeordnetes Element an eine Komponente übergibt ([.nexy-Dateien](../views/nexy/README.md)) |
| Überprüfen Sie erneut | die Anzahl der Sekunden, nach denen eine ISR-Seite im Hintergrund neu erstellt wird ([ISR](../rendering/isr.md)) |
| Leiten Sie | ein URL-Muster weiter, das durch den Pfad einer Routendatei erzeugt wird ([routing](../routing/README.md)) |
| Routengruppe | ein Ordner in Klammern, der Routen gruppiert, ohne ein Segment hinzuzufügen ([dynamische Routen](../routing/fbr/pages/dynamic-routes.md)) |
| Routenhandler | die `GET`, `POST`, … Funktion einer `.py` Routendatei ([handlers](../routing/fbr/handlers/README.md)) |
| Servermodus | `useCSR = False`, Standard: Der Server rendert `.nexy` und `.md` Seiten ([modes](../routing/fbr/modes.md)) |
| Fertigkeit | einen Ordner mit einem `SKILL.md`, der einem Coding Agent einen Teil von Nexy beibringt ([Coding Agents](../guides/ai-agents.md)) |
| SSG | statische Site-Generierung; **kein Nexy-Modus**: Der im Voraus erstellte HTML-Code wird immer vom Server zurückgelesen ([Rendering](../rendering/README.md)) |
| SSR | serverseitiges Rendering: Der Server rendert jede Seite für seine Anfrage, und dies ist die Standardeinstellung ([SSR](../rendering/ssr.md)) |
| Sehen Sie sich | den Prozess der Erstellung des Antworttexts für eine Seite an ([views](../views/README.md)) |

## Dateien und Ordner

| Name | In einer Zeile |
|---|---|
| `__nexy__/` | generierte Ausgabe: kompilierte Seiten, der Client-Eintrag und der Aktions-Client; nie bearbeitet, nie festgeschrieben |
| `nexyconfig.py` | die Projektkonfiguration, eine Klasse von `use*` Feldern ([config](config.md)) |
| `public/` | Dateien, die im Stammverzeichnis bereitgestellt werden, wie etwa `public/logo.svg` → `/logo.svg` ([Dateikonventionen](file-conventions.md)) |
| `src/apps/` | Controller und Module des modularen Routers ([modular](../routing/modular/README.md)) |
| `src/components/` | Von Seiten importierte Komponenten; leitet niemals weiter ([Dateikonventionen](file-conventions.md)) |
| `src/routes/` | die Wege der Anwendung ([Dateikonventionen](file-conventions.md)) |

## Nächste Schritte

- [Kernkonzepte](../getting-started/core-concepts.md): das Modell, zu dem diese Wörter gehören
- [Dokumentationsindex](../README.md): die Seite für die jeweilige Aufgabe
- [Dateikonventionen](file-conventions.md): die reservierten Namen hinter diesen Definitionen
- [Für KI-Agenten](../guides/ai-agents.md): dieselben Invarianten, geschrieben für einen Agenten
