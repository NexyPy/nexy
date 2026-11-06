# Nexy-Dokumentation

**Ein Python Framework für Fullstack-Webanwendungen.**

Nexy fügt Ihre Seiten und Ihre API in einem Python Projekt zusammen, das von einem Server bedient wird. Version 2.2 basiert auf FastAPI: Jede API-Route ist eine FastAPI-Route, aufgelistet in einem OpenAPI-Schema, das Scalar unter `/docs` anzeigt.

- **Python zuerst.** Seiten, Endpunkte, Formulare und Aktionen sind Python, und eine Seite benötigt kein JavaScript.
- **Ein Frontend, wenn Sie eines wollen.** React, Vue, Svelte, Solid oder Preact, für eine Komponente oder für die gesamte Site.
- **Eine Datei, eine URL.** Eine Datei unter `src/routes/` ist eine Route: `.nexy` ist eine Seite, `.py` ist ein API-Endpunkt.
- **Raum zum Wachsen.** Beginnen Sie mit einer Datei; Wechseln Sie zu Modulen oder schließen Sie einen vorhandenen FastAPI Router an, wenn das Projekt wächst.

Neu hier? Lesen Sie [Was ist Nexy?](getting-started/what-is-nexy.md) und dann den [Schnellstart](getting-started/quick-start.md).

## Erste Schritte

### Erste Schritte
| Seite | Was Sie tun werden |
|---|---|
| [Was ist Nexy?](getting-started/what-is-nexy.md) | Erfahren Sie, was Nexy ist, worauf es aufbaut und was Sie bekommen |
| [Installation](getting-started/installation.md) | Installieren Sie uv und die Nexy-CLI und erstellen Sie dann Ihr erstes Projekt |
| [Schnellstart](getting-started/quick-start.md) | Erstellen Sie ein Projekt, führen Sie es per Live-Reload aus und erstellen Sie es für die Produktion |
| [Anleitung](getting-started/tutorial.md) | Erstellen Sie in 10 Minuten eine Notizenseite mit einem Endpunkt, freigegebenen Daten und einem Produktions-Build |

### Verstehen Sie das Modell
| Seite | Was Sie tun werden |
|---|---|
| [Kernkonzepte](getting-started/core-concepts.md) | Holen Sie sich das mentale Modell: Route, Seite, Ansicht, Komponente, Handler, Endpunkt |
| [Projektstruktur](getting-started/project-structure.md) | Wissen Sie, wozu jeder Ordner und jede Datei in einem Projekt dient |
| [Wählen Sie einen Router](routing/README.md) | Wählen Sie den dateibasierten, modularen oder benutzerdefinierten Router |
| [Wählen Sie ein Ansichtsformat](views/README.md) | Wählen Sie `.nexy`, Markdown oder ein Client-Framework für eine Seite |

## Routenführung

### Dateibasiert {fbr}
| Seite | Was Sie tun werden |
|---|---|
| [Dateibasiertes Routing](routing/fbr/README.md) | Verwandeln Sie einen Dateipfad in eine URL |
| [Seiten](routing/fbr/pages/README.md) | Schreiben Sie eine Seite |
| [Dynamische Routen](routing/fbr/pages/dynamic-routes.md) | Verwenden Sie `[slug]`, `[...path]` und Routengruppen |
| [Seitenmetadaten](routing/fbr/pages/metadata.md) | Legen Sie den Titel, die Beschreibung und das Freigabebild einer Seite fest {new} |
| [Layouts](routing/fbr/layouts/README.md) | Teilen Sie einen Rahmen zwischen Seiten |
| [Vererbung](routing/fbr/inheritance.md) | Lesen Sie die Auflösungsreihenfolge von Layouts, Abhängigkeiten und Fehlerseiten |
| [Servermodus und Clientmodus](routing/fbr/modes.md) | `useCSR` und was jeder Modus ermöglicht |
| [Verknüpfen und Navigieren](routing/fbr/navigation/linking-and-navigating.md) | Seiten verlinken, auf dem Client navigieren, Prefetch |
| [Haken](routing/fbr/navigation/hooks.md) | Lesen Sie den Pfad, die Abfrage, die Cookies und die Sitzung |

### Handler und Fehler {fbr}
| Seite | Was Sie tun werden |
|---|---|
| [Routenhandler](routing/fbr/handlers/README.md) | Fügen Sie einen Python-Endpunkt hinzu |
| [Validierung und Fehler](routing/fbr/handlers/validation-and-errors.md) | Beantworten Sie `422` und `404` und erheben Sie eine `HTTPException` |
| [WebSocket Handler](routing/fbr/realtime/websocket.md) | Behandelt eine `SOCKET`-Verbindung |
| [Abhängigkeiten und Wachen](routing/fbr/dependencies/README.md) | Führen Sie `dependencies.py` vor einem Handler aus und erben Sie ihn |
| [Middleware-Dateien](routing/fbr/middleware/README.md) | Anfragen mit `middleware.py` umschließen, geerbt vom Verzeichnis |
| [Fehlerseiten](routing/fbr/errors/README.md) | Antworten Sie mit `notfound.nexy`, `errors.nexy` und JSON-Fehlern |
| [Fehlerseiten pro Ordner](routing/fbr/errors/folder-pages.md) | Randfall: Fehler aus Unterordnern |

### Modularer Router {modular}
Controller und Module.
| Seite | Was Sie tun werden |
|---|---|
| [Modulares Routing](routing/modular/README.md) | Montieren Sie Controller und Module |
| [Abhängigkeitsinjektion](routing/modular/dependency-injection.md) | Definieren Sie Dienste, ihre Bereiche und den Container |
| [Guards und Metadaten](routing/modular/guards-and-metadata.md) | Routen schützen und dokumentieren |
| [Modularer Router vs. NestJS](routing/modular/vs-nestjs.md) | Vergleich mit NestJS |

### Benutzerdefinierte Router-Integration {custom}
| Seite | Was Sie tun werden |
|---|---|
| [Benutzerdefiniertes Routing](routing/custom/README.md) | Fügen Sie eine vorhandene FastAPI-App hinzu |

## Frontend

### Geteilte Verträge
| Seite | Was es definiert |
|---|---|
| [Frontend-Seiten](views/frontend/pages.md) | Eine Datei, eine Route: Requisiten, Rendering, Metadaten |
| [Frontend-Layouts](views/frontend/layouts.md) | Die Dokumenthülle, die Verschachtelung und was ein Layout nicht leisten kann |
| [Aktionen und Navigation](views/frontend/actions-and-navigation.md) | Rufen Sie eine eingegebene Aktion auf, verlinken Sie Seiten und lesen Sie die URL |

### Nexy-Ansichten
| Seite | Was Sie tun werden |
|---|---|
| [.nexy-Dateien](views/nexy/README.md) | Schreiben Sie eine Seite mit Python, Jinja2 und Requisiten |
| [Komponenten](views/nexy/components.md) | Verwenden Sie `Image`, `Link`, `Audio`, `Video` und `Import`. |
| [layout.nexy](views/nexy/layouts.md) | Schreiben Sie das Servermodus-Layout |
| [Markdown und MDX](views/nexy/markdown.md) | Schreiben Sie Inhaltsseiten |

### Rahmenunterschiede
| Seite | Was ändert sich |
|---|---|
| [React Unterschiede](views/react/differences.md) | Komponenten, Haken und `layout.tsx` {new} |
| [Vue Unterschiede](views/vue/differences.md) | SFCs, Refs und `layout.vue` {new} |
| [Svelte Unterschiede](views/svelte/differences.md) | Runen, Geschäfte und `layout.svelte` {new} |
| [Solid Unterschiede](views/solid/differences.md) | Signale, Accessoren und `layout.tsx` {new} |
| [Preact Unterschiede](views/preact/differences.md) | Haken, Signale und `layout.tsx` {new} |

## Rendern

### Modi
| Seite | Was Sie entscheiden werden |
|---|---|
| [Rendern](rendering/README.md) | Welcher Rendering-Modus passt zu einer Seite? |
| [SSR](rendering/ssr.md) | Server-Rendering, die Standardeinstellung |
| [ISR](rendering/isr.md) | Cache-Seiten mit Stale-While-Revalidate |
| [CSR](rendering/csr.md) | Clientseitiges Routing |
| [Inseln](rendering/islands.md) | Hydratisieren bei Leerlauf-, Sichtbarkeits- oder Medienabfrage |

## Führer

### Formulare und Daten
| Seite | Was Sie tun werden |
|---|---|
| [Aktionen](guides/actions.md) | Rufen Sie eine Python-Funktion aus einem Formular oder einer typisierten TypeScript-Funktion auf |
| [Datenbanken](guides/databases.md) | Wählen Sie einen ORM und führen Sie Migrationen aus |

### Sicherheit und Bereitstellung
| Seite | Was Sie tun werden |
|---|---|
| [Middleware und Sicherheit](guides/middleware-and-security.md) | Richten Sie CORS, GZip, vertrauenswürdige Hosts und Sitzungen ein |
| [Bereitstellen](deployment/README.md) | Zusammenstellen, in Behälter füllen und servieren |
| [Leistung](deployment/performance.md) | Messen und optimieren Sie die Standardwerte |

### Bauen und testen
| Seite | Was Sie tun werden |
|---|---|
| [Vite und Styling](guides/frontend.md) | Richten Sie Vite, das Styling und den Client-Build ein |
| [Testen](guides/testing.md) | Testen Sie mit pytest, `TestClient` und vitest |

### Werkzeuge und Hilfe
| Seite | Was Sie tun werden |
|---|---|
| [Dev-Symbolleiste](guides/devtools.md) | Verwenden Sie die Symbolleiste von `nexy dev` und schalten Sie sie aus |
| [Kodiermittel](guides/ai-agents.md) | Geben Sie Claude Code, Codex und OpenCode die Regeln Ihres Projekts an |
| [Fehlerbehebung](guides/troubleshooting.md) | Beheben Sie die ersten Probleme, auf die Menschen stoßen |

## Datenbanken

### SQL-Datenbanken
| Seite | Was Sie tun werden |
|---|---|
| [SQLite](databases/sqlite.md) | Verwenden Sie eine Datei, keinen Server: Engine, Pragmas, Migrationen und Tests |
| [PostgreSQL](databases/postgresql.md) | Verbinden Sie sich mit psycopg, verwenden Sie JSONB, Arrays, Suche und Upserts |
| [Neon](databases/neon.md) | Verwenden Sie serverloses PostgreSQL: gepoolten Host, automatische Suspendierung und Verzweigungen |
| [MySQL und MariaDB](databases/mysql-mariadb.md) | Stellen Sie eine Verbindung mit pymysql her, verwenden Sie utf8mb4, Upserts und die Volltextsuche |

## Kommt von

Die gleichen Aufgaben, geschrieben in dem Ihnen bekannten Framework und dann in Nexy.

### Übersicht
| Seite | Was Sie tun werden |
|---|---|
| [Aus einem anderen Rahmen kommend](getting-started/coming-from-other-frameworks.md) | Übersetzen Sie FastAPI, Next.js und drücken Sie Gewohnheiten in Nexy aus |

### Python Frameworks {fbr}
| Seite | Was Sie tun werden |
|---|---|
| [Von FastAPI](coming-from/fastapi.md) | Behalten Sie Ihren FastAPI-Code: Nur `@app.get` wird zu einer Datei |
| [Von Flask](coming-from/flask.md) | Verwandeln Sie Ansichten, Blaupausen, Vorlagen und Formulare in Nexy-Routen |
| [Von Django](coming-from/django.md) | Ordnen Sie Ansichten, Vorlagen, Modelle, Formulare und Einstellungen Nexy zu |

### JavaScript Backends {fbr}
| Seite | Was Sie tun werden |
|---|---|
| [Von Express](coming-from/express.md) | Übersetzen Sie Routen, Middleware und `req`/`res` in Python-Handler |
| [Von Fastify](coming-from/fastify.md) | Verwandeln Sie Schemata, Plugins und Hooks in Modelle, Ordner und Dateien |
| [Aus Elysia](coming-from/elysia.md) | Ordnen Sie `t` Schemata, Wachen und Eden Pydantic und typisierten Aktionen zu |
| [Von Hono](coming-from/hono.md) | Ordnen Sie Routen, Middleware und den `hc`-Client Nexy zu |

### Fullstack-Frameworks {fbr}
| Seite | Was Sie tun werden |
|---|---|
| [Von Next.js](coming-from/nextjs.md) | Behalten Sie Ihre React-Seiten und verschieben Sie den Servercode nach Python |
| [Von Remix](coming-from/remix.md) | Verwandeln Sie Loader und Aktionen in Python Handler und Aktionen |
| [Von Nuxt](coming-from/nuxt.md) | Behalten Sie Ihre Vue-Seiten und verschieben Sie `server/` nach Python |
| [Von SvelteKit](coming-from/sveltekit.md) | Behalten Sie Ihre Svelte-Seiten und verschieben Sie Lasten, Aktionen und Hooks nach Python |
| [Von Astro](coming-from/astro.md) | Schreiben Sie Astro Seiten als `.nexy` Seiten mit denselben Inseln |
| [Von Laravel](coming-from/laravel.md) | Ordnen Sie Routen, Controller, Blade, Eloquent und Warteschlangen Nexy zu |
| [Von Ruby on Rails](coming-from/rails.md) | Ordnen Sie Routen, Controller, ERB, Active Record und Jobs Nexy zu |

### Controller-Frameworks {modular}
| Seite | Was Sie tun werden |
|---|---|
| [Von NestJS](coming-from/nestjs.md) | Verschieben Sie Controller, Module, Provider und Guards auf den modularen Router |
| [Von Spring Boot](coming-from/spring-boot.md) | Verschieben Sie Controller, Dienste und Filter auf den modularen Router |

## Referenz

### Befehle und Konfiguration
| Seite | Was darin aufgeführt ist |
|---|---|
| [CLI](reference/cli.md) | Befehle, Flags, Eingabeaufforderungen und Exit-Codes |
| [Konfig](reference/config.md) | Jedes `nexyconfig.py`-Feld und seine Standardeinstellung |

### Python API und Fehler
| Seite | Was darin aufgeführt ist |
|---|---|
| [Python-API](reference/python-api.md) | Jeder Name, den Nexy exportiert, nach Modul |
| [Ausnahmen und Fehler](reference/exceptions.md) | Jeder Fehler, sein Status und die Datei, die ihn beantwortet |

### Konventionen und Konzepte
| Seite | Was Sie tun werden |
|---|---|
| [Dateikonventionen](reference/file-conventions.md) | Reservierte Dateien und Routing-Regeln |
| [Glossar](reference/glossary.md) | Die in diesen Dokumenten verwendeten Wörter |
| [Sicherheit](reference/security.md) | Versionsebenen, Regeln, denen Nexy folgt, Audits |

## Layout
```text
docs/
├─ README.md
├─ getting-started/     what is Nexy, installation, quick start, tutorial, core concepts,
│                       project structure, how Nexy works, migration
├─ coming-from/         one page per framework: FastAPI, Django, Express, Next.js...
├─ databases/           one page per database: SQLite, PostgreSQL, Neon, MySQL
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

## Fortgeschritten

### Erweitert {advanced}

| Seite | Was Sie tun werden |
|---|---|
| [Wie Nexy funktioniert](getting-started/how-nexy-works.md) | Sehen Sie, was zwischen einer Datei und einer Seite passiert und was Nexy Ihnen hinterlässt |
| [Upgrade auf 2.2](getting-started/upgrading.md) | Von 2.1 auf 2.2 migrieren |
| [Internationalisierung (i18n)](guides/i18n.md) | Fügen Sie Übersetzungen mit der Bibliothek Ihrer Wahl hinzu |
| [Rezepte](guides/recipes.md) | Beispiele und Muster, kein Tutorial |

*Diese Seiten sind nicht Teil des Standardlesepfads. Über den Link „Alle Dokumentationen“ können Sie alles sehen.*
