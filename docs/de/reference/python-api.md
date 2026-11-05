# Python API

Jeder Name, den Nexy modulweise in Ihren Python-Code exportiert. Ein Test prüft diese Seite anhand des Codes in beide Richtungen: Ein hier aufgeführter Name muss vorhanden sein, und ein Name, den der Code exportiert, muss hier aufgeführt sein.

## `nexy`

Komponenten für `.nexy`-Vorlagen und die Anforderungs-Hooks.

| Name | Was es ist |
|---|---|
| `Audio`, `Video` | native `<audio>` und `<video>` Spieler, siehe [components](../views/nexy/components.md) |
| `Image` | ein `<img>`, das standardmäßig langsam lädt |
| `Link` | eine Client-Seite `<a>` mit optionalem Prefetch |
| `Import` | eine Client-Komponente in eine `.nexy` Seite importieren |
| `Template` | rendern Jinja2 und Markdown Vorlagen |
| `Vite` | das Vite Client-Tag, das jede Seite benötigt |
| `Form` | ein Platzhalter ohne Verhalten: Verwenden Sie ein einfaches `<form>` mit einer [Aktion](../guides/actions.md) |
| `usePathname` | der Pfad der aktuellen Anfrage |
| `useSearchParams` | die Abfragezeichenfolge als Diktat |
| `useParams` | die dynamischen Pfadparameter als Diktat, wie `useParams()` auf dem Client |
| `useQuery` | der ursprüngliche Name von `useParams`, der für vorhandene Seiten beibehalten wird (die Abfragezeichenfolge wird nicht gelesen) |
| `useRequest` | die aktuelle Anfrage, für das, was die anderen Hooks nicht abdecken |
| `useHeaders` | die Anforderungsheader als Diktat mit Namen in Kleinbuchstaben |
| `useUrl` | die vollständige URL: `.scheme`, `.hostname`, `.path`, `.query` |
| `useIsActive` | ob ein Link auf die aktuelle Seite oder eine ihrer übergeordneten Seiten verweist, für eine Navigationsleiste |
| `useRouter` | `path`, `base_url` und `url_for` der aktuellen Anfrage |
| `useSession` | das Sitzungsdikt, leer, wenn Sitzungen ausgeschaltet sind |
| `useCookies` | die Anforderungscookies als Diktat |
| `useToc` | das Inhaltsverzeichnis der aktuellen Seite, als HTML |
| `useViews` | rendert eine Ansichtsdatei wie `about.tsx` von einem Handler |
| `setMetadata`, `useMetadata` | Benennen Sie die Titel- und Head-Tags einer Seite und schreiben Sie sie in das Layout |
| `redirect`, `permanentRedirect` | Schicken Sie den Besucher woanders hin (307, 308) und stoppen Sie die Anfrage |
| `notFound`, `forbidden`, `unauthorized` | Antworte 404, 403 oder 401 von überall aus |

Die Hooks funktionieren nur innerhalb einer Anfrage: siehe [Hooks](../routing/fbr/navigation/hooks.md).

## `nexy.http`

Das HTTP-Vokabular eines Handlers. Importieren Sie von hier und nicht von FastAPI, sodass Ihre Handler auf Nexys Vertrag angewiesen sind.

| Name | Was es ist |
|---|---|
| `Request`, `Response` | die eingehende Anfrage und eine ausgehende Antwort |
| `HTTPException` | Stoppen Sie den Handler mit einem Status und einem `detail` |
| `status` | benannte Statuscodes, wie zum Beispiel `status.HTTP_404_NOT_FOUND` |
| `Depends` | führt zuerst eine Funktion aus und übergibt ihr Ergebnis in |
| `Header`, `Cookie`, `Query`, `Path`, `Body` | wobei ein Parameter von | kommt
| `Form`, `File`, `UploadFile` | Formularfelder und Uploads (benötigt `python-multipart`) |
| `BackgroundTasks` | Arbeit, die nach dem Senden der Antwort ausgeführt wird |
| `JSONResponse`, `HTMLResponse`, `PlainTextResponse` | Antworten mit einem festen Inhaltstyp |
| `RedirectResponse` | eine HTTP-Weiterleitung |
| `redirect`, `permanentRedirect` | lösen eine Weiterleitung (307, 308) von einer Seite, einem Handler, einem Controller oder einem Guard aus |
| `notFound`, `forbidden`, `unauthorized` | Erhöhe einen 404, 403 oder 401 an denselben Stellen |
| `FileResponse`, `StreamingResponse` | mit einer Datei oder einem Stream antworten |

## `nexy.decorators`

| Name | Was es ist |
|---|---|
| `Action` | Verwandeln Sie eine Funktion in einen `POST` Endpunkt, siehe [Aktionen](../guides/actions.md) |
| `revalidate` | Teilen Sie dem Browser mit, welche Seiten durch eine Aktion veraltet sind |
| `Module`, `Controller` | deklarieren ein Modul und einen Controller im [modularen Router](../routing/modular/README.md) |
| `Injectable`, `Container`, `Scope` | [Abhängigkeitsinjektion](../routing/modular/dependency-injection.md) und ihre Lebensdauer |
| `UseGuard`, `Middleware` | einen Handler bewachen oder einwickeln, siehe [guards](../routing/modular/guards-and-metadata.md) |
| `UseRoute`, `useRoute`, `RouteMeta` | benennen Sie eine Route und beschreiben Sie sie für OpenAPI |
| `UseResponse`, `ResponseMeta` | beschreiben die Antwort einer Route |
| `HTTP_METHODS` | die HTTP-Methoden, die eine Handlerdatei definieren kann |
| `ACTIONS_STORE` | das Aktionsregister für Werkzeuge und Tests |

## `nexy.testing`

| Name | Was es ist |
|---|---|
| `render` | der HTML-Code einer `.nexy` Komponente für bestimmte Requisiten, ohne Server, siehe [Testen](../guides/testing.md) |

## Wohin als nächstes

- [Config](config.md): die `use*`-Felder hinter diesen Namen
- [Ausnahmen und Fehler](exceptions.md): Was jeder Fehler beantwortet
- [Dokumentationsindex](../README.md): die Seite für das, was Sie erstellen
