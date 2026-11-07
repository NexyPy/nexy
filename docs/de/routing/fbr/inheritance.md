# Vererbung

Mehrere Dateien in `src/routes/` gelten für alles unterhalb ihres Verzeichnisses. Sie lösen sich alle auf die gleiche Weise auf: Nexy beginnt beim Routenverzeichnis und geht bis zu `src/routes/`.

```text
src/routes/
├─ layout.nexy               1. outermost
├─ dependencies.py           1. runs first
├─ middleware.py             1. wraps first
├─ notfound.nexy             fallback for every URL
├─ (shop)/                   a group is a directory: it takes part, it is not in the URL
│  ├─ layout.nexy            2.
│  ├─ dependencies.py        2.
│  └─ cart/
│     ├─ layout.nexy         3. innermost
│     ├─ dependencies.py     3. runs last
│     └─ index.nexy          the page
```

| Datei | Regel |
|---|---|
| `layout.nexy`, `layout.tsx`, `layout.vue`, `layout.svelte` | Jedes Layout vom Stamm bis zur Seite umschließt es, **äußerstes zuerst** |
| `middleware.py` | Jede Datei vom Stammverzeichnis bis zur Route umschließt die Anfrage **äußerst zuerst** vor Abhängigkeiten |
| `dependencies.py` | Jede Datei vom Stammverzeichnis bis zur Route wird ausgeführt, **die äußerste zuerst**, dann die eigenen Wachen des Handlers |
| `notfound.nexy`, `errors.nexy` | Der **Nächste** gewinnt, je Statuscode |

Für die Seite oben werden die Layouts als `root layout > (shop) layout > cart layout > page` verschachtelt und die Abhängigkeiten werden als `root > (shop) > cart > handler guards` ausgeführt.

## Warum das Äußerste zuerst?

Ein äußeres Layout bildet den Rahmen und eine äußere Abhängigkeit entscheidet darüber, wer überhaupt reinkommen darf. Wenn man sie an die erste Stelle setzt, können sich die inneren auf sie verlassen: Ein Verzeichnis, das eine Authentifizierung erfordert, wird vor einem Handler ausgeführt, der den Benutzer liest.

Die `(shop)`-Abhängigkeit des Baums überprüft das Warenkorb-Cookie, sodass die darunter liegende Warenkorb-Abhängigkeit den Warenkorb lesen kann, ohne eine erneute Überprüfung durchzuführen:

```python filename="src/routes/(shop)/dependencies.py"
from nexy.http import HTTPException, Request


def require_cart(request: Request) -> None:
    if "cart" not in request.cookies:
        raise HTTPException(status_code=400, detail="No cart")


dependencies = [require_cart]
```

## Layouts

Alle Layoutdateien eines Ordnerfamilienstapels: siehe [Layouts](layouts/README.md). Verschiedene Familien vermischen sich nicht: Ein `layout.vue` umschließt niemals eine `.tsx`-Seite, und ein Projekt hat entweder `layout.nexy` oder Client-Layouts, niemals beides ([Modi](modes.md)).

Das innerste Layout des Baums fügt nur seinen eigenen Rahmen hinzu: Das Root-Layout um ihn herum zeichnet weiterhin das Dokument.

```nexy filename="src/routes/(shop)/cart/layout.nexy"
---
children: prop[NexyElement]
---
<section class="cart">
  <h2>Your cart</h2>
  {{ children | safe }}
</section>
```

## Middleware-Dateien

Siehe [Middleware-Dateien](middleware/README.md): Sie werden vor Abhängigkeiten ausgeführt und können antworten, ohne die Route zu erreichen.

Eine Wurzel `middleware.py` umschließt jede Route des Baums, der Wagen enthält:

```python filename="src/routes/middleware.py"
import time

from nexy.http import Request


async def middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["x-time-ms"] = f"{(time.perf_counter() - start) * 1000:.1f}"
    return response
```

## Abhängigkeiten

Siehe [Abhängigkeiten](dependencies/README.md) für die Reihenfolge in einer Handlerdatei, einschließlich `@UseGuard` und `@Middleware`.

## Fehlerseiten

`notfound.nexy` und `errors.nexy` werden einmal im Routenstamm installiert; Eine Kopie in einem Unterverzeichnis verfeinert die Seite für dieses Präfix. Siehe [Fehlerseiten](errors/README.md).

Eine Kopie in `cart/` beantwortet die 404er unter `/cart`, und die Wurzelkopie behält den Rest:

```nexy filename="src/routes/(shop)/cart/notfound.nexy"
<h1>This product is gone</h1>
<p><a href="/cart">Back to your cart</a></p>
```

## Nächste Schritte

- [Layouts](layouts/README.md)
- [Abhängigkeiten](dependencies/README.md)
- [Fehlerseiten](errors/README.md)
