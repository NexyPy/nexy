# Routenführung

Nexy verfügt über zwei native Router. Sie können eine pro Funktion auswählen. Sie können in derselben Anwendung koexistieren.

**Nicht sicher? Verwenden Sie dateibasiertes Routing.** Es deckt Seiten und API-Endpunkte ohne Einrichtung ab. Fügen Sie den modularen Router hinzu, wenn ein Backend Controller, injizierte Dienste oder Wachen benötigt.

| Sie bauen | und verwenden |
|---|---|
| Seiten, Inhalte, eine Site mit einigen Endpunkten | Dateibasiert |
| Eine große API mit Diensten, die über mehrere Routen hinweg gemeinsam genutzt werden | Modular |
| Beides: Seiten für Menschen, eine strukturierte API für Maschinen | Dateibasiert und modular zusammen |

```diagram filename="Der dateibasierte Router auf einen Blick"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```

| Router | Quelle | Aktiviert durch |
|---|---|---|
| [Dateibasiert (FBR)](fbr/README.md) | jede Datei unter `src/routes/` | das Verzeichnis existiert |
| [Modulare](modular/README.md) | Controller und Module | `useRouter = AppModule` in `nexyconfig.py` |

FBR wird immer dann gescannt, wenn `src/routes/` vorhanden ist, auch wenn ein modularer Router montiert ist.

## Zusammenleben und Prioritäten

Sie können FBR, Modular und benutzerdefinierte Integration kombinieren. Nexy registriert diese Routen in der Reihenfolge, in der sie entdeckt werden. Wenn zwei Router denselben URL-Pfad definieren, gewinnt der zuerst registrierte. 

*Hinweis: Nexy bietet derzeit keine Diagnose für URL-Kollisionen; Die erste Route, die einen Pfad beansprucht, überschattet einfach die anderen.*

## Dateibasiertes Routing

Eine Route ist eine Datei. Die URL ist der Pfad unter `src/routes/`, abzüglich der Erweiterung. Wie Next.js befindet sich ein Projekt in einem von zwei Modi, ausgewählt mit `useCSR`:

| | `useCSR = False` (Standard) | `useCSR = True` |
|---|---|---|
| Seiten | `.nexy`, `.md`, `.mdx` | Dateien Ihres Client-Frameworks |
| Root-Layout | `layout.nexy` | `layout.tsx` (React) |
| Client-Komponenten | erlaubt, als Inseln innerhalb von Seiten | die Seiten selbst |
| API-Routen | `.py` | `.py` |

Siehe [Servermodus und Clientmodus](fbr/modes.md).

| Abschnitt | Was es umfasst |
|---|---|
| [fbr/pages](fbr/pages/README.md) | Seiten, [dynamische Routen](fbr/pages/dynamic-routes.md) und Routengruppen |
| [fbr/layouts](fbr/layouts/README.md) | `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` |
| [fbr/handlers](fbr/handlers/README.md) | `.py` Routenhandler, [Validierung und Fehler](fbr/handlers/validation-and-errors.md) |
| [fbr/dependencies](fbr/dependencies/README.md) | `dependencies.py` und Guards, geerbt von Verzeichnis |
| [fbr/middleware](fbr/middleware/README.md) | `middleware.py`, geerbt von Verzeichnis |
| [fbr/errors](fbr/errors/README.md) | `notfound.nexy`, `errors.nexy`, JSON-Fehler |
| [fbr/navigation](fbr/navigation/linking-and-navigating.md) | Verlinkung, Client-Navigation, [Hooks](fbr/navigation/hooks.md) |
| [fbr/realtime](fbr/realtime/websocket.md) | WebSocket Handler |
| [fbr/inheritance](fbr/inheritance.md) | wie Layouts, Abhängigkeiten und Fehlerseiten erben |

## Modulares Routing

Controller, Module und Abhängigkeitsinjektion im Stil von NestJS. Siehe [Modulares Routing](modular/README.md) und [Nexy und NestJS](modular/vs-nestjs.md).

## Benutzerdefinierte Integration

Sie können auch einen vorhandenen FastAPI Router in Ihr Nexy-Projekt integrieren. Siehe [Benutzerdefinierte Routing-Integration](custom/README.md).

## Nächste Schritte

- [Dateibasiertes Routing](fbr/README.md)
- [Rendering](../rendering/README.md)
- [Ansichten](../views/README.md): was in den Dateien enthalten ist
