# Routenführung

Nexy verfügt über zwei native Router. Sie können eine pro Funktion auswählen; Sie können in derselben Anwendung koexistieren.

**Nicht sicher? Verwenden Sie dateibasiertes Routing.** Es deckt Seiten und API-Endpunkte ohne Einrichtung ab. Fügen Sie den modularen Router hinzu, wenn ein Backend Controller, injizierte Dienste oder Wachen benötigt.

| Sie bauen | Benutzen |
|---|---|
| Seiten, Inhalte, eine Site mit einigen Endpunkten | Dateibasiert |
| Eine große API mit Diensten, die auf allen Routen gemeinsam genutzt werden | Modular |
| Beides: Seiten für Menschen, eine strukturierte API für Maschinen | Dateibasiert und modular zusammen |

<!-- router:fbr,custom -->
```diagram filename="Der dateibasierte Router auf einen Blick"
src/routes/index.nexy           →  /
src/routes/about.nexy           →  /about
src/routes/blog/index.nexy      →  /blog
src/routes/blog/[slug].nexy     →  /blog/:slug
src/routes/(app)/dashboard.nexy →  /dashboard
src/routes/api/users.py         →  /api/users  (GET, POST, …)
```
<!-- /router -->

<!-- router:modular -->
```diagram filename="Der modulare Router im Überblick"
@Controller()             class AppController   →  /
@Controller("/about")     class AboutController →  /about/
@Controller("/api/users") class UserController  →  /api/users/  (get, post, …)
@Module()                 class AppModule       →  lists the controllers
useRouter = AppModule     nexyconfig.py         →  mounts the module
```
<!-- /router -->

| Router | Quelle | Aktiviert von |
|---|---|---|
| [Dateibasiert (FBR)](fbr/README.md) | jede Datei unter `src/routes/` | Das Verzeichnis existiert |
| [Modular](modular/README.md) | Controller und Module | `useRouter = AppModule` in `nexyconfig.py` |

FBR wird immer dann gescannt, wenn `src/routes/` vorhanden ist, auch wenn ein modularer Router montiert ist.

## Zusammenleben und Prioritäten

Sie können FBR, Modular und benutzerdefinierte Integration kombinieren. Nexy registriert diese Routen in der Reihenfolge, in der sie entdeckt werden. Wenn zwei Router denselben URL-Pfad definieren, gewinnt der zuerst registrierte. 

*Hinweis: Nexy bietet derzeit keine Diagnose für URL-Kollisionen; Die erste Route, die einen Pfad beansprucht, überschattet einfach die anderen.*

<!-- router:fbr,custom -->
## Dateibasiertes Routing

Eine Route ist eine Datei. Die URL ist der Pfad unter `src/routes/`, abzüglich der Erweiterung. Wie Next.js befindet sich ein Projekt in einem von zwei Modi, ausgewählt mit `useCSR`:

| | `useCSR = False` (Standard) | `useCSR = True` |
|---|---|---|
| Seiten | `.nexy`, `.md`, `.mdx` | Dateien Ihres Client-Frameworks |
| Root-Layout | `layout.nexy` | `layout.tsx` (React) |
| Client-Komponenten | erlaubt, als Inseln innerhalb von Seiten | die Seiten selbst |
| API-Routen | `.py` | `.py` |

Siehe [Servermodus und Clientmodus](fbr/modes.md).

| Abschnitt | Was es abdeckt |
|---|---|
| [fbr/pages](fbr/pages/README.md) | Seiten, [dynamische Routen](fbr/pages/dynamic-routes.md) und Routengruppen |
| [fbr/layouts](fbr/layouts/README.md) | `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` |
| [fbr/handlers](fbr/handlers/README.md) | `.py` Routenhandler, [Validierung und Fehler](fbr/handlers/validation-and-errors.md) |
| [fbr/Abhängigkeiten](fbr/dependencies/README.md) | `dependencies.py` und Wächter, geerbt vom Verzeichnis |
| [fbr/middleware](fbr/middleware/README.md) | `middleware.py`, geerbt vom Verzeichnis |
| [fbr/errors](fbr/errors/README.md) | `notfound.nexy`, `errors.nexy`, JSON-Fehler |
| [fbr/navigation](fbr/navigation/linking-and-navigating.md) | Verlinkung, Client-Navigation, [Hooks](fbr/navigation/hooks.md) |
| [fbr/realtime](fbr/realtime/websocket.md) | WebSocket Handler |
| [fbr/Vererbung](fbr/inheritance.md) | wie Layouts, Abhängigkeiten und Fehlerseiten erben |
<!-- /router -->

## Modulares Routing

Controller, Module und Abhängigkeitsinjektion im Stil von NestJS. Siehe [Modulares Routing](modular/README.md) und [Nexy und NestJS](modular/vs-nestjs.md).

<!-- router:modular -->
| Abschnitt | Was es abdeckt |
|---|---|
| [modular](modular/README.md) | `@Controller`, `@Module`, Importe und Exporte |
| [Modular/Abhängigkeitsinjektion](modular/dependency-injection.md) | `@Injectable`, Bereiche und der Container |
| [modular/guards-and-metadata](modular/guards-and-metadata.md) | `@UseGuard`, `@UseResponse` und die OpenAPI-Metadaten |

Ein Controller gibt eine `.nexy`-Ansicht mit `useViews` zurück und übergibt sie manuell an sein Layout: Es gibt kein `layout.nexy`, das vom Ordner angewendet wird.
<!-- /router -->

## Benutzerdefinierte Integration

Sie können auch einen vorhandenen FastAPI Router in Ihr Nexy-Projekt integrieren. Siehe [Benutzerdefinierte Routing-Integration](custom/README.md).

## Nächste Schritte

<!-- router:fbr,custom -->
- [Dateibasiertes Routing](fbr/README.md)
<!-- /router -->
<!-- router:modular -->
- [Modulares Routing](modular/README.md)
<!-- /router -->
- [Rendern](../rendering/README.md)
- [Ansichten](../views/README.md): was in den Dateien enthalten ist
