# Python API

Jeder Name, den Nexy modulweise in Ihren Python-Code exportiert. Ein Test prüft diese Seite anhand des Codes in beide Richtungen: Ein hier aufgeführter Name muss vorhanden sein, und ein Name, den der Code exportiert, muss hier aufgeführt sein.

## `nexy`

Komponenten für `.nexy`-Vorlagen und die Anforderungs-Hooks.

| Name | Was es ist |
|---|---|
| `Audio`, `Video` | Native `<audio>` und `<video>` Player, siehe [Komponenten](../views/nexy/components.md) |
| `Image` | ein `<img>`, das standardmäßig langsam lädt |
| `Link` | ein clientseitiger `<a>` mit optionalem Prefetch |
| `Import` | Importieren Sie eine Client-Komponente in eine `.nexy`-Seite |
| `Template` | Rendern Sie die Vorlagen Jinja2 und Markdown. |
| `Vite` | das Vite-Client-Tag, das jede Seite benötigt |
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
| `useToc` | Das Inhaltsverzeichnis der aktuellen Seite als HTML |
| `useViews` | Rendern Sie eine Ansichtsdatei wie `about.tsx` von einem Handler |
| `setMetadata`, `useMetadata` | Benennen Sie die Titel- und Kopf-Tags einer Seite und schreiben Sie sie in das Layout |
| `redirect`, `permanentRedirect` | Schicken Sie den Besucher woanders hin (307, 308) und stoppen Sie die Anfrage |
| `notFound`, `forbidden`, `unauthorized` | Antworten Sie von überall aus auf die Nummern 404, 403 oder 401 |

Die Hooks funktionieren nur innerhalb einer Anfrage: siehe [Hooks](../routing/fbr/navigation/hooks.md).

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from nexy import useCookies, usePathname, useSearchParams

pathname = usePathname()
page = useSearchParams().get("page", "1")
theme = useCookies().get("theme", "light")
---
<p>{{ pathname }} - page {{ page }} - {{ theme }} theme</p>
```
<!-- /router -->

## `nexy.http`

Das HTTP-Vokabular eines Handlers. Importieren Sie von hier und nicht von FastAPI, sodass Ihre Handler auf Nexys Vertrag angewiesen sind.

| Name | Was es ist |
|---|---|
| `Request`, `Response` | die eingehende Anfrage und eine ausgehende Antwort |
| `HTTPException` | Stoppen Sie den Handler mit einem Status und einem `detail` |
| `status` | benannte Statuscodes, wie zum Beispiel `status.HTTP_404_NOT_FOUND` |
| `Depends` | Führen Sie zuerst eine Funktion aus und übergeben Sie das Ergebnis |
| `Header`, `Cookie`, `Query`, `Path`, `Body` | woher ein Parameter kommt |
| `Form`, `File`, `UploadFile` | Formularfelder und Uploads (`python-multipart` nur für `multipart/form-data`) |
| `BackgroundTasks` | Arbeit, die ausgeführt wird, nachdem die Antwort gesendet wurde |
| `JSONResponse`, `HTMLResponse`, `PlainTextResponse` | Antworten mit einem festen Inhaltstyp |
| `RedirectResponse` | eine HTTP-Weiterleitung |
| `redirect`, `permanentRedirect` | eine Weiterleitung (307, 308) von einer Seite, einem Handler, einem Controller oder einem Guard auslösen |
| `notFound`, `forbidden`, `unauthorized` | Erhöhen Sie eine 404, 403 oder 401 an denselben Stellen |
| `FileResponse`, `StreamingResponse` | mit einer Datei oder einem Stream antworten |

<!-- router:fbr,custom -->
```python filename="src/routes/api/items/[id].py"
from nexy.http import Depends, Header, HTTPException, status


def api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad key")
    return x_api_key


async def GET(id: int, key: str = Depends(api_key)):
    return {"id": id}
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/items/items_by_id_api_controller.py"
from nexy.decorators import Controller
from nexy.http import Depends, Header, HTTPException, status


def api_key(x_api_key: str = Header(...)) -> str:
    if x_api_key != "secret":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad key")
    return x_api_key


@Controller("/api/items/{id}")
class ItemsByIdApiController:
    async def get(self, id: int, key: str = Depends(api_key)):
        return {"id": id}
```

Listen Sie den Controller im `controllers` des Root-Moduls auf.
<!-- /router -->

## `nexy.decorators`

| Name | Was es ist |
|---|---|
| `Action` | Verwandeln Sie eine Funktion in einen `POST` Endpunkt, siehe [Aktionen](../guides/actions.md) |
| `revalidate` | Teilen Sie dem Browser mit, welche Seiten durch eine Aktion veraltet sind |
| `Module`, `Controller` | Deklarieren Sie ein Modul und einen Controller im [modularen Router](../routing/modular/README.md) |
| `Injectable`, `Container`, `Scope` | [Abhängigkeitsinjektion](../routing/modular/dependency-injection.md) und ihre Lebensdauer |
| `UseGuard`, `Middleware` | einen Handler bewachen oder einwickeln, siehe [Guards](../routing/modular/guards-and-metadata.md) |
| `UseRoute`, `useRoute`, `RouteMeta` | Benennen Sie eine Route und beschreiben Sie sie für OpenAPI |
| `UseResponse`, `ResponseMeta` | Beschreiben Sie die Antwort einer Route |
| `HTTP_METHODS` | die HTTP-Methoden, die eine Handlerdatei definieren kann |
| `ACTIONS_STORE` | das Aktionsregister für Werkzeuge und Tests |

```python filename="src/actions/posts.py"
from nexy.decorators import Action, revalidate


@Action
async def publish(post_id: int) -> bool:
    revalidate("/blog")
    return True
```

## `nexy.testing`

| Name | Was es ist |
|---|---|
| `render` | Der HTML-Code einer `.nexy`-Komponente für bestimmte Requisiten, ohne Server, siehe [Testen](../guides/testing.md) |

```python filename="tests/test_button.py"
from nexy.testing import render


def test_the_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

## Wohin als nächstes

- [Konfiguration](config.md): die `use*`-Felder hinter diesen Namen
- [Ausnahmen und Fehler](exceptions.md): Was jeder Fehler beantwortet
- [Dokumentationsindex](../README.md): die Seite für das, was Sie erstellen
