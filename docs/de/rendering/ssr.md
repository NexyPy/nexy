# SSR (Server-Rendering)

## Definition

SSR ist die Standardeinstellung: Der Server rendert die Seite für jede Anfrage in HTML. Nichts aktiviert es und kein Flag schaltet es aus – ein Projekt im Servermodus wird bei jeder Anfrage gerendert, es sei denn, eine Seite deklariert `revalidate`.

## Wie es funktioniert

<!-- router:fbr,custom -->
| Routendatei | Was erzeugt den HTML | Wann |
|---|---|---|
| `.nexy` | das kompilierte Python-Modul, bis Jinja2 | jede Anfrage |
| `.md` | Markdown, dann das nächstgelegene Layout | jede Anfrage |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | das Framework, gerendert in Node | beim Build, wenn die Route kein Layout hat, andernfalls im Browser |
| `.py` | nichts: Es gibt JSON oder ein `Response` zurück. | - |

Eine Markdown-Seite und ein Handler nebeneinander im selben Projekt:

```md filename="src/routes/changelog.md"
# Changelog

Rendered to HTML on every request, then wrapped in the nearest layout.
```

```python filename="src/routes/api/health.py"
async def GET():
    return {"status": "ok"}
```

Eine Komponentenroute ist der einzige Fall, der einen zweiten Satz benötigt. In der Produktion wird eine Komponentenroute **ohne** ein Layout mit dem beim Build erzeugten HTML bereitgestellt und die Komponente hydratisiert es. Bei einem Layout oder in der Entwicklung ist der Container leer und die Komponente wird im Browser gerendert – die Seite ist dann eine Hülle, die sich selbst füllt.

Die Komponentenroute der Tabelle ohne Layout, sodass die Produktion ihren HTML-Code aus dem Build bereitstellt:

```tsx filename="src/routes/pricing.tsx"
export default function Pricing() {
  return <h1>Pricing</h1>;
}
```
<!-- /router -->

<!-- router:modular -->
| Ein Controller kehrt zurück | Was erzeugt den HTML | Wann |
|---|---|---|
| `useViews("....nexy")` | das kompilierte Python Modul, bis Jinja2 | jede Anfrage |
| ein `dict`, eine Liste, ein Modell | nichts: FastAPI antwortet JSON | - |

Eine Ansicht und ein JSON-Endpunkt nebeneinander im selben Modul:

```nexy filename="src/apps/changelog_view.nexy"
<h1>Changelog</h1>
<p>Rendered to HTML on every request.</p>
```

```python filename="src/apps/site_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/changelog")
class ChangelogController:
    async def get(self):
        return useViews("src/apps/changelog_view.nexy")


@Controller("/api/health")
class HealthController:
    async def get(self):
        return {"status": "ok"}
```
<!-- /router -->

## Rendering-Lebenszyklus

<!-- router:fbr,custom -->
1. Die Anfrage erreicht den dateibasierten Router. Der Pfad wird abgeglichen und dynamische Segmente werden in die von der Komponente deklarierten Typen umgewandelt.

   ```nexy filename="src/routes/orders/[id].nexy"
   ---
   id: prop[int]
   ---
   <h1>Order #{{ id + 1000 }}</h1>
   ```

   `/orders/42` rendert `Order #1042`; `/orders/abc` antwortet `404`.
2. Die Komponente läuft. Eines, das auf Node wartet – ein Clientdokument – ​​wird in einem Thread-Pool ausgeführt, sodass die Ereignisschleife nicht blockiert wird.
3. Der Körper wird als `text/html` gestreamt. Eine Komponente, die Chunks erzeugt, streamt diese, während sie sie erstellt.
4. Der Browser empfängt HTML. Inseln hydratisieren gemäß ihrer [Richtlinie](islands.md).

Ein beim Rendern ausgelöster Fehler wird von `errors.nexy` in eine Seite umgewandelt, wenn das Projekt einen solchen hat: siehe [Fehlerseiten](../routing/fbr/errors/README.md).
<!-- /router -->

<!-- router:modular -->
1. Die Anfrage erreicht den Controller. Seine Pfadparameter werden in die von der Methode deklarierten Typen umgewandelt und an die Ansicht übergeben:

   ```python filename="src/apps/order_controller.py"
   from nexy.decorators import Controller
   from nexy.hooks import useViews


   @Controller("/orders/{id}")
   class OrderController:
       async def get(self, id: int):
           return useViews("src/apps/order_view.nexy", context={"id": id})
   ```

   ```nexy filename="src/apps/order_view.nexy"
   ---
   id: prop[int]
   ---
   <h1>Order #{{ id + 1000 }}</h1>
   ```

   `/orders/42/` rendert `Order #1042`; `/orders/abc/` antwortet `404`.
2. Die Ansicht wird ausgeführt und `useViews` gibt ihren HTML-Code als Antwort zurück.
3. Der Browser empfängt HTML. Inseln hydratisieren gemäß ihrer [Richtlinie](islands.md).

Ein beim Rendern auftretender Fehler wird mit der Standardfehlerseite beantwortet.
<!-- /router -->

## Wann zu verwenden

- Die Seite zeigt etwas, das der Leser besitzt: eine Sitzung, ein Konto, einen Warenkorb.
- Die Daten müssen bei jedem Ladevorgang aktuell sein.
- Der Inhalt muss im HTML für Crawler vorliegen, die nicht JavaScript ausführen.
- Die Seite ist kostengünstig zu rendern: eine Abfrage, eine Vorlage.

Der erste Fall ist eine Seite, die den Leser aus der Sitzung begrüßt. `useSession` liest die Sitzung von `useSession` in `nexyconfig.py`, ohne die es fehlschlägt:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSession = {"secret_key": "change-me"}
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/account.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/account_view.nexy"
---
from nexy import useSession

user = useSession().get("user", "guest")
---
<h1>Signed in as {{ user }}</h1>
```
<!-- /router -->

## Konfiguration

<!-- router:fbr,custom -->
Keine. Zwei Auswege, und sie haben nicht die gleiche Körnung:

| SSR verlassen für | Tun Sie dies | Getreide |
|---|---|---|
| eine Seite, mit Cache | `revalidate = 60` im Vorwort → [ISR](isr.md) | Seite |
| das gesamte Projekt, vom Kunden weitergeleitet | `useCSR = True` in `nexyconfig.py` → [CSR](csr.md) | Projekt |

Der projektweite Schalter, in `nexyconfig.py`. Der Client-Modus benötigt ein Client-Framework:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```
<!-- /router -->

<!-- router:modular -->
Keine. Jede von einem Controller zurückgegebene Ansicht wird bei jeder Anfrage gerendert: [ISR](isr.md) und [CSR](csr.md) sind Modi des dateibasierten Routers.
<!-- /router -->

## Beispiel

<!-- router:fbr,custom -->
```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` führt diese Vorlage einmal aus, wobei `slug` auf `hello` gesetzt ist. Eine zweite Anfrage führt es erneut aus: Zwischen den beiden bleibt nichts bestehen. Die Abfragezeichenfolge ist keine Requisite – lesen Sie sie mit den Hooks in [Navigation](../routing/fbr/navigation/hooks.md).
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/blog_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews


@Controller("/blog/{slug}")
class PostController:
    async def get(self, slug: str):
        return useViews("src/apps/post_view.nexy", context={"slug": slug})
```

```nexy filename="src/apps/post_view.nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello/` führt diese Ansicht einmal aus, wobei `slug` auf `hello` gesetzt ist. Eine zweite Anfrage führt es erneut aus: Zwischen den beiden bleibt nichts bestehen. Die Abfragezeichenfolge ist keine Requisite – lesen Sie sie mit `useSearchParams`.
<!-- /router -->

## Einschränkungen

- **Ein Rendering pro Anfrage.** Zwei Besucher in derselben Sekunde zahlen jeweils für das Rendering und die dahinter stehenden Abfragen.
- **Kein Cache.** Es gibt keinen gemeinsamen Antwort-Cache zum Warmmachen: Bei Dateirouten fügt [ISR](isr.md) einen pro URL hinzu.
- **Streaming hilft nur einer Komponente, die nachgibt.** Eine langsame Abfrage oben auf der Seite verzögert immer noch das erste Byte.
- **Keine statische Ausgabe.** Im Servermodus wird beim Erstellen nichts eingefroren: Es gibt keinen SSG-Modus und keinen Exportbefehl. Siehe [Rendering](README.md).
- **Autoescaping ist in `.nexy` Vorlagen deaktiviert**. Entkommen Sie nicht vertrauenswürdigen Werten mit `| e`.

<!-- router:fbr,custom -->
```nexy filename="src/routes/search.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/search_view.nexy"
---
from nexy import useSearchParams

q = useSearchParams().get("q", "")
---
<p>Results for {{ q | e }}</p>
```
<!-- /router -->

## Nächste Schritte

<!-- router:fbr,custom -->
- [ISR](isr.md): Diese Seite pro URL zwischenspeichern
<!-- /router -->
- [Inseln](islands.md): SSR beibehalten und ein Widget interaktiv machen
<!-- router:fbr,custom -->
- [CSR](csr.md): Handnavigation zum Browser
<!-- /router -->
- [Leistung](../deployment/performance.md)
