# Nexy-Dokumentation

**Ein Python-Framework für Fullstack-Webanwendungen.**

Bei Nexy geht es um die Nahtstelle zwischen einem Python-Backend und einem Browser-Frontend. Statt zwei Servern zwei
Wenn Sie Systeme und zwei Routentabellen erstellen, erhalten Sie einen Ursprung: FastAPI und Starlette bedienen die Anwendung.
Vite erstellt den Client und eine Datei unter `src/routes/` ist eine Route – `.nexy` ist eine Seite, `.py` ist eine
API-Handler.

- **Python zuerst.** Seiten, Endpunkte, Formulare und Aktionen sind Python und eine vom Server gerenderte Seite ist erforderlich
  kein Frontend-Framework.
- **Drei Router, eine Integration.** Dateibasiert, modular oder eine vorhandene FastAPI `APIRouter`.
- **Ein Frontend, wenn Sie eines wollen.** Reagieren, Vue, Svelte, Solid oder Preact, pro Seite als Inseln oder für
  das gesamte Projekt im Client-Modus.
- **Rendering, ein Modell.** Server-Rendering, zwischengespeicherte Seiten und Inseln werden pro Seite entschieden; Kunde
  Routing ist ein Projektwechsel.
- **Typisierte Aktionen.** Ein Formularbeitrag und ein typisierter Clientaufruf erreichen dieselbe Python-Funktion.

Beginnen Sie mit einer Datei unter `src/routes/` und fügen Sie Struktur hinzu, wenn das Projekt wächst.

## Erste Schritte

### Erste Schritte
| Seite | Was Sie tun werden |
|---|---|
| [Installation](getting-started/installation.md) | Installieren Sie uv und die Nexy-CLI und erstellen Sie dann Ihr erstes Projekt |
| [Schnellstart](getting-started/quick-start.md) | Erstellen Sie ein Projekt, führen Sie es mit Live-Reload aus und erstellen Sie es für die Produktion |
| [Tutorial](getting-started/tutorial.md) | Erstellen Sie eine Notizenseite mit einem Endpunkt, freigegebenen Daten und einem Produktions-Build in 10 Minuten |

### Verstehen Sie das Modell
| Seite | Was Sie tun werden |
|---|---|
| [Kernkonzepte](getting-started/core-concepts.md) | Holen Sie sich das mentale Modell: Route, Seite, Ansicht, Komponente, Handler, Endpunkt |
| [Wie Nexy funktioniert](getting-started/how-nexy-works.md) | Folgen Sie einer Anfrage von der URL zu der Datei, die darauf antwortet |
| [Architektur](architecture.md) | Wissen Sie, welche Schicht was tut und was Nexy Ihrer Anwendung überlässt |
| [Projektstruktur](getting-started/project-structure.md) | Wissen, wozu jeder Ordner und jede Datei in einem Projekt dient |
| [Wählen Sie einen Router](routing/README.md) | Wählen Sie den dateibasierten, modularen oder benutzerdefinierten Router |
| [Wählen Sie ein Ansichtsformat](views/README.md) | Wählen Sie `.nexy`, Markdown oder ein Client-Framework für eine Seite |

### Komme von anderswo
| Seite | Was Sie tun werden |
|---|---|
| [Kommt aus einem anderen Framework](getting-started/coming-from-other-frameworks.md) | Übersetzen Sie FastAPI-, Next.js- und Express-Gewohnheiten in Nexy |

## Weiterleitung

### Dateibasiert {fbr}
| Seite | Was Sie tun werden |
|---|---|
| [Dateibasiertes Routing](routing/fbr/README.md) | Verwandeln Sie einen Dateipfad in eine URL |
| [Seiten](routing/fbr/pages/README.md) | Eine Seite schreiben |
| [Dynamische Routen](routing/fbr/pages/dynamic-routes.md) | Verwenden Sie `[slug]`, `[...path]` und Routengruppen |
| [Seitenmetadaten](routing/fbr/pages/metadata.md) | Legen Sie den Titel, die Beschreibung und das Freigabebild einer Seite fest {new} |
| [Layouts](routing/fbr/layouts/README.md) | Einen Rahmen zwischen Seiten teilen |
| [Vererbung](routing/fbr/inheritance.md) | Lesen Sie die Auflösungsreihenfolge von Layouts, Abhängigkeiten und Fehlerseiten |
| [Servermodus und Clientmodus](routing/fbr/modes.md) | `useCSR` und was jeder Modus ermöglicht |
| [Verknüpfen und Navigieren](routing/fbr/navigation/linking-and-navigating.md) | Seiten verlinken, auf dem Client navigieren, Prefetch |
| [Hooks](routing/fbr/navigation/hooks.md) | Pfad, Abfrage, Cookies und Sitzung lesen |

### Handler und Fehler {fbr}
| Seite | Was Sie tun werden |
|---|---|
| [Routenhandler](routing/fbr/handlers/README.md) | Einen Python-Endpunkt hinzufügen |
| [Validierung und Fehler](routing/fbr/handlers/validation-and-errors.md) | Beantworten Sie `422` und `404` und lösen Sie eine `HTTPException` | aus.
| [WebSocket-Handler](routing/fbr/realtime/websocket.md) | Verarbeiten einer `SOCKET` Verbindung |
| [Abhängigkeiten und Wächter](routing/fbr/dependencies/README.md) | Führen Sie `dependencies.py` vor einem Handler aus und erben Sie ihn |
| [Middleware-Dateien](routing/fbr/middleware/README.md) | Wrap-Anfragen mit `middleware.py`, geerbt von Verzeichnis |
| [Fehlerseiten](routing/fbr/errors/README.md) | Antwort mit `notfound.nexy`, `errors.nexy` und JSON-Fehlern |
| [Fehlerseiten pro Ordner](routing/fbr/errors/folder-pages.md) | Randfall: Fehler aus Unterordnern |

### Modularer Router {modular}
Controller und Module.
| Seite | Was Sie tun werden |
|---|---|
| [Modulares Routing](routing/modular/README.md) | Controller und Module montieren |
| [Abhängigkeitsinjektion](routing/modular/dependency-injection.md) | Definieren Sie Dienste, ihre Bereiche und den Container |
| [Schutz und Metadaten](routing/modular/guards-and-metadata.md) | Routen schützen und dokumentieren |
| [Modularer Router vs. NestJS](routing/modular/vs-nestjs.md) | Vergleich mit NestJS |

### Benutzerdefinierte Router-Integration {custom}
| Seite | Was Sie tun werden |
|---|---|
| [Benutzerdefiniertes Routing](routing/custom/README.md) | Eine vorhandene FastAPI-App einschließen |

## Frontend

### Gemeinsame Verträge
| Seite | Was es definiert |
|---|---|
| [Frontend-Seiten](views/frontend/pages.md) | Eine Datei, eine Route: Requisiten, Rendering, Metadaten |
| [Frontend-Layouts](views/frontend/layouts.md) | Die Dokumenthülle, die Verschachtelung und was ein Layout nicht kann |
| [Aktionen und Navigation](views/frontend/actions-and-navigation.md) | Rufen Sie eine eingegebene Aktion auf, verlinken Sie Seiten, lesen Sie die URL |

### Nexy-Ansichten
| Seite | Was Sie tun werden |
|---|---|
| [.nexy-Dateien](views/nexy/README.md) | Schreiben Sie eine Seite mit Python, Jinja2 und Requisiten |
| [Komponenten](views/nexy/components.md) | Verwenden Sie `Image`, `Link`, `Audio`, `Video` und `Import` |
| [layout.nexy](views/nexy/layouts.md) | Schreiben Sie das Servermodus-Layout |
| [Markdown und MDX](views/nexy/markdown.md) | Inhaltsseiten schreiben |

### Framework-Unterschiede
| Seite | Was ändert sich |
|---|---|
| [Unterschiede reagieren](views/react/differences.md) | Komponenten, Haken und `layout.tsx` {new} |
| [Vue-Unterschiede](views/vue/differences.md) | SFCs, Refs und `layout.vue` {new} |
| [Geringe Unterschiede](views/svelte/differences.md) | Runen, Geschäfte und `layout.svelte` {new} |
| [Feste Unterschiede](views/solid/differences.md) | Signale, Accessoren und `layout.tsx` {new} |
| [Präakte Unterschiede](views/preact/differences.md) | Haken, Signale und `layout.tsx` {new} |

## Rendering

### Modi
| Seite | Was Sie entscheiden werden |
|---|---|
| [Rendering](rendering/README.md) | Welcher Rendering-Modus passt zu einer Seite |
| [SSR](rendering/ssr.md) | Server-Rendering, die Standardeinstellung |
| [ISR](rendering/isr.md) | Cache-Seiten mit Stale-While-Revalidate |
| [CSR](rendering/csr.md) | Clientseitiges Routing |
| [Inseln](rendering/islands.md) | Hydratisierung bei Leerlauf-, sichtbarer oder Medienabfrage |

## Anleitungen

### Formulare und Daten
| Seite | Was Sie tun werden |
|---|---|
| [Aktionen](guides/actions.md) | Rufen Sie eine Python-Funktion aus einem Formular oder einer typisierten TypeScript-Funktion auf |
| [Datenbanken](guides/databases.md) | Wählen Sie einen ORM und führen Sie Migrationen aus |

### Sicherheit und Bereitstellung
| Seite | Was Sie tun werden |
|---|---|
| [Middleware und Sicherheit](guides/middleware-and-security.md) | CORS, GZip, vertrauenswürdige Hosts und Sitzungen einrichten |
| [Bereitstellen](deployment/README.md) | Erstellen, Containerisieren und Bereitstellen |
| [Leistung](deployment/performance.md) | Messen und optimieren Sie die Standardwerte |

### Erstellen und testen
| Seite | Was Sie tun werden |
|---|---|
| [Vite und Styling](guides/frontend.md) | Vite, Styling und den Client-Build einrichten |
| [Testen](guides/testing.md) | Test mit Pytest, `TestClient` und Vitest |

### Werkzeuge und Hilfe
| Seite | Was Sie tun werden |
|---|---|
| [Dev-Symbolleiste](guides/devtools.md) | Verwenden Sie die Symbolleiste von `nexy dev` und schalten Sie sie aus |
| [Codierungsagenten](guides/ai-agents.md) | Geben Sie Claude Code, Codex und OpenCode die Regeln Ihres Projekts |
| [Fehlerbehebung](guides/troubleshooting.md) | Beheben Sie die ersten Probleme, auf die Leute stoßen |

## Referenz

### Befehle und Konfiguration
| Seite | Was darin aufgeführt ist |
|---|---|
| [CLI](reference/cli.md) | Befehle, Flags, Eingabeaufforderungen und Exit-Codes |
| [Config](reference/config.md) | Jedes `nexyconfig.py` Feld und seine Standardeinstellung |

### Python-API und Fehler
| Seite | Was darin aufgeführt ist |
|---|---|
| [Python-API](reference/python-api.md) | Jeder Name, den Nexy exportiert, nach Modul |
| [Ausnahmen und Fehler](reference/exceptions.md) | Jeder Fehler, sein Status und die Datei, die ihn beantwortet |

### Konventionen und Konzepte
| Seite | Was Sie tun werden |
|---|---|
| [Dateikonventionen](reference/file-conventions.md) | Reservierte Dateien und Routing-Regeln |
| [Glossar](reference/glossary.md) | Die in diesen Dokumenten verwendeten Wörter |
| [Sicherheit](reference/security.md) | Versionsuntergrenzen, Regeln, denen Nexy folgt, Audits |

## Layout
```text
docs/
├─ README.md
├─ architecture.md       the layers, and what Nexy leaves to the application
├─ getting-started/     installation, quick start, tutorial, core concepts, project structure,
│                       migration
├─ routing/             FBR Router, Modular Router, Custom Router
│  ├─ fbr/              file-based routing
│  │  ├─ modes.md       server mode and client mode
│  │  ├─ inheritance.md layouts, dependencies, error pages
│  │  ├─ pages/         pages, dynamic routes, route groups, metadata
│  │  ├─ layouts/       layout resolution, layout.tsx, layout.vue, layout.svelte
│  │  ├─ handlers/      .py route handlers, validation and errors
│  │  ├─ dependencies/  dependencies.py, guards
│  │  ├─ middleware/    middleware.py
│  │  ├─ errors/        not-found and error pages
│  │  ├─ navigation/    links, hooks
│  │  └─ realtime/    WebSocket
│  ├─ modular/          controllers, injection, guards, NestJS comparison
│  └─ custom/           include an existing FastAPI router
├─ rendering/           SSR, ISR, CSR, islands
├─ views/               choose a format, one page per client framework
│  ├─ frontend/         the four contracts every framework shares
│  └─ nexy/             .nexy files, components, layouts, Markdown and MDX
├─ guides/              actions, i18n, databases, middleware, frontend, testing
├─ deployment/          deploy, performance
└─ reference/           CLI, config, Python API, exceptions, file conventions, glossary,
                        security, agents
```

## Erweitert

### Fortgeschritten {advanced}

| Seite | Was Sie tun werden |
|---|---|
| [Upgrade auf 2.2](getting-started/upgrading.md) | Migration von 2.1 auf 2.2 |
| [Internationalisierung (i18n)](guides/i18n.md) | Fügen Sie Übersetzungen mit der Bibliothek Ihrer Wahl hinzu |
| [Rezepte](guides/recipes.md) | Beispiele und Muster, kein Tutorial |

*Diese Seiten sind nicht Teil des Standardlesepfads. Über den Link „Alle Dokumentationen“ können Sie alles sehen.*