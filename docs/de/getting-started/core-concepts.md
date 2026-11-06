# Kernkonzepte

Die Wörter, die in den übrigen Dokumenten verwendet werden – Route, Seite, Ansicht, Komponente, Handler, Endpunkt – jeweils in einer Zeile, mit einem Link zu der Seite, die tiefer geht. Neu bei Nexy? Beginnen Sie mit [Was ist Nexy?](what-is-nexy.md).

## So lesen Sie diese Dokumente

| Ebene | Die Frage, die es beantwortet | Beginnen Sie mit |
|---|---|---|
| Anwendungsarchitektur | welche Schicht eine Anfrage beantwortet und was sie ablehnt | [Wie Nexy funktioniert](how-nexy-works.md) |
| Anwendungsstruktur | wo sich der Code befindet und was aus einer Datei wird | [Projektstruktur](project-structure.md) |
| Präsentation und Rendering | was der Leser sieht und wer den HTML-Code erstellt | [Ansichten](../views/README.md), [Rendering](../rendering/README.md) |
| Anwendungsinteraktion | was der Leser tut und was als Reaktion darauf ausgeführt wird | [Aktionen](../guides/actions.md) |

Die Level werden in dieser Reihenfolge einmal gelesen. Danach handelt es sich bei der Seite, die Sie benötigen, um eine Nachschlageseite und nicht um einen Kurs.

## Anwendungsarchitektur

Drei Möglichkeiten, um zu entscheiden, welcher Code auf eine URL antwortet. Es handelt sich um Alternativen, nicht um Schichten:

- **Dateibasiertes Routing (FBR)**: Eine Datei unter `src/routes/` ist eine Route. Die Standardeinstellung.
- **Modularer Router**: Controller und Module unter `src/apps/`, deklariert mit Dekoratoren, für eine Codebasis im NestJS-Stil.
- **Benutzerdefinierter Router**: ein vorhandener FastAPI `APIRouter`, der in der Anwendung enthalten ist.

Die Auswahl ist eine Zeile der Klasse `NexyConfig` in `nexyconfig.py`.

<!-- router:fbr -->
Dateibasiertes Routing benötigt keine Zeile: Ohne `useRouter` liest Nexy `src/routes/`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    pass  # file-based: no useRouter, the files of src/routes/ are the routes
```
<!-- /router -->

<!-- router:modular -->
Der modulare Router ist das Root-Modul von `src/apps/`:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.apps.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useRouter = AppModule  # modular: the root module of src/apps/
```
<!-- /router -->

<!-- router:custom -->
Ein benutzerdefinierter Router ist ein `APIRouter`, den Sie bereits haben:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel

from src.legacy import api  # an APIRouter you already have


class NexyConfig(NexyConfigModel):
    useRouter = api  # custom: your router, included as it is
```
<!-- /router -->

Sich für einen der drei zu entscheiden, ist eine Entscheidung. Die Auswahl eines Frontend-Frameworks ist eine andere, separate Angelegenheit: siehe [Router auswählen](../routing/README.md) und [Ansichten](../views/README.md).

## Anwendungsstruktur

Fünf Vorstellungen, die ein Leser aus Next.js normalerweise zu einer einzigen vereint. Sie sind nicht dasselbe und der Unterschied erklärt die meisten Fragen zum Thema „Warum wird meine Seite nicht gerendert“.

| Vorstellung | Was es ist | Was es nicht ist |
|---|---|---|
| **Route** | ein URL-Muster, das durch den Pfad einer Datei erzeugt wird | eine Datei: Eine Datei kann auf mehrere URLs antworten (`[slug]`) |
| **Seite** | eine Routendatei, die eine Ansicht rendert: `.nexy`, `.md`, `.mdx`, `.tsx`, `.vue`, `.svelte` | ein Endpunkt: Er antwortet auf ein Dokument, nicht auf Daten |
| **Anzeigen** | Was erzeugt den Hauptteil einer Seite: Jinja2 und Python, Markdown oder eine Client-Komponente | eine Route: Die gleiche Ansicht kann mehrere Seiten bedienen |
| **Komponente** | ein wiederverwendbarer Teil, den eine Seite importiert | eine Route: Im Servermodus wird eine Komponente niemals alleine bedient |
| **Routenhandler** | die Funktion einer `.py`-Routendatei, benannt nach der HTTP-Methode (`GET`, `POST`, …) | eine Seite: Sie gibt JSON, eine Datei oder ein `Response` zurück. |
| **Endpunkt** | das Paar (URL, Methode), auf das ein Handler antwortet | ein Handler: Eine Datei kann mehrere Endpunkte beantworten |

In einem Satz: **Eine Seite ist eine Routendatei, eine Ansicht ist das, was sie rendert, eine Komponente ist das, was eine Seite wiederverwendet, ein Handler antwortet einem Endpunkt.**

<!-- router:fbr -->
Alle fünf in einem kleinen Projekt:

```text
src/
├─ routes/
│  ├─ blog/[slug].nexy    a route (/blog/{slug}) whose file is a page
│  └─ api/posts.py        a route whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```nexy filename="src/routes/blog/[slug].nexy"
---
from "@/components/Like.tsx" import Like

slug: prop[str]
---
<h1>{{ slug }}</h1>
<Like post="{{ slug }}" />
```

Die Vorderseite und die Vorlage darunter sind die Ansicht der Seite; `Like` ist die Komponente, die es wiederverwendet.

```python filename="src/routes/api/posts.py"
async def GET():  # the endpoint GET /api/posts
    return {"posts": []}


async def POST():  # the endpoint POST /api/posts
    return {"created": True}
```

<!-- /router -->

<!-- router:modular -->
Beim modularen Router ist eine Route der Pfad eines Controllers und ein Handler eine seiner Methoden, benannt nach dem HTTP-Verb:

```text
src/
├─ apps/
│  ├─ app_module.py       the root module: lists the controllers
│  └─ posts_controller.py a route (/api/posts) whose handlers answer two endpoints
└─ components/
   └─ Like.tsx            a component: never served on its own
```

```python filename="src/apps/posts_controller.py"
from nexy.decorators import Controller


@Controller("/api/posts")
class PostsController:
    async def get(self) -> dict:  # the endpoint GET /api/posts
        return {"posts": []}

    async def post(self) -> dict:  # the endpoint POST /api/posts
        return {"created": True}
```

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .posts_controller import PostsController


@Module()
class AppModule:
    controllers = [PostsController]
```

Eine Seite ist immer noch eine Datei von `src/routes/` oder eine Ansicht, die ein Controller mit `useViews` zurückgibt.
<!-- /router -->

<!-- router:custom -->
Bei einem benutzerdefinierten Router ist eine Route ein Pfad Ihres `APIRouter` und ein Handler die Funktion, die sein Dekorator registriert:

```python filename="src/legacy.py"
from fastapi import APIRouter

api = APIRouter()


@api.get("/api/posts")  # the endpoint GET /api/posts
async def list_posts():
    return {"posts": []}


@api.post("/api/posts")  # the endpoint POST /api/posts
async def create_post():
    return {"created": True}
```

Seiten sind immer noch Dateien von `src/routes/`: Eine `.nexy`-Seite antwortet neben den enthaltenen Routen.
<!-- /router -->

Zwei weitere Wörter, die überall wiederkehren:

- **Layout**: eine `layout.*`-Datei, die die Seiten unterhalb ihres Ordners umschließt; Der Root besitzt das HTML-Dokument. Siehe [Layouts](../routing/fbr/layouts/README.md).
- **Abhängigkeit**: eine Funktion, die vor einem Handler ausgeführt wird und pro Route oder pro Ordner angewendet wird. Siehe [Abhängigkeiten](../routing/fbr/dependencies/README.md).

## Präsentation und Rendering

Zwei unabhängige Entscheidungen, oft verwechselt:

- **Das Format** entscheidet, welche Datei die Seite rendert: [Ansichten](../views/README.md).
- **Der Modus** entscheidet, wer wann den HTML-Code produziert: [Rendering](../rendering/README.md).

| Vorstellung | Eine Zeile |
|---|---|
| Servermodus | Der Server rendert die Seiten `.nexy` und `.md`. Komponenten sind Inseln ([Modi](../routing/fbr/modes.md)) |
| Client-Modus | `useCSR = True`: Framework-Dateien sind die Routen, und die Navigation erfolgt im Browser |
| SSR, ISR, CSR, Inseln | vier Rendering-Modi, die pro Seite festgelegt werden, mit Ausnahme von CSR, das pro Projekt gilt ([Rendering](../rendering/README.md)) |
| Flüssigkeitszufuhr | Der Browser fügt ein Framework an HTML an, das der Server bereits gesendet hat ([Inseln](../rendering/islands.md)) |
| Requisiten | die Werte, die ein übergeordnetes Element an eine Komponente übergibt, deklariert als `name: prop[type]` in einer `.nexy`-Datei ([.nexy-Dateien](../views/nexy/README.md)) |

Eine Seite im Servermodus mit einer Insel: Der Server rendert die Seite, der Browser hydriert das Diagramm nur, wenn es in die Ansicht scrollt.

```nexy filename="src/routes/sales.nexy"
---
from "@/components/Chart.tsx" import Chart
---
<h1>Sales</h1>
<Chart directive="client:visible" />
```

## Anwendungsinteraktion

| Vorstellung | Eine Zeile |
|---|---|
| Aktion | eine Python-Funktion mit der Markierung `@Action`, die als `POST` diente und über ein Formular oder als typisierte Funktion ([Aktionen](../guides/actions.md)) aufgerufen werden konnte. |
| Formular | ein HTML-Formular, das an eine Aktion sendet, wobei Validierungsfehler auf die Seite zurückkommen ([Aktionen](../guides/actions.md)) |
| Navigation | Links, die vorab abrufen, und Hooks, die den Pfad, die Abfrage, die Cookies und die Sitzung lesen ([Hooks](../routing/fbr/navigation/hooks.md)) |
| Datenabruf | wird von der Seite oder dem Handler erledigt, der es benötigt; Nexy liefert keine Client-Datenschicht ([Handler](../routing/fbr/handlers/README.md)) |

Eine Aktion und das Formular, das an sie sendet und das funktioniert, bevor ein Skript geladen wird:

```python filename="src/actions/newsletter.py"
from nexy.decorators import Action


@Action
async def subscribe(email: str) -> bool:
    return True
```

```html filename="src/routes/index.nexy"
<form method="post" action="{{ __actions_path['subscribe'] }}">
  <input name="email" type="email">
  <button type="submit">Subscribe</button>
</form>
```

## Was Nexy nicht macht

Authentifizierung, Autorisierung, Datenbank, Internationalisierung, Hintergrundjobs, E-Mail, Zahlungen und Suche liegen **in der Verantwortung Ihrer Anwendung**, nicht in der des Frameworks. Nexy gibt die Erweiterungspunkte an und sagt, wo sie jeweils angeschlossen werden müssen: siehe [Was Nexy Ihnen hinterlässt](how-nexy-works.md#what-nexy-leaves-to-you).

<!-- router:fbr -->
Die Authentifizierung stellt beispielsweise eine Verbindung zu einer Abhängigkeit des Ordners her, den sie schützt. Nexy führt es vor jeder Route unten aus; Wer der Benutzer ist, bleibt Ihre Entscheidung:

```python filename="src/routes/account/dependencies.py"
from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


dependencies = [require_login]
```
<!-- /router -->

<!-- router:modular -->
Die Authentifizierung wird beispielsweise an einen Schutz auf dem Controller angeschlossen, den sie schützt. Nexy führt es vor jedem Handler der Klasse aus; Wer der Benutzer ist, bleibt Ihre Entscheidung:

```python filename="src/apps/account_controller.py"
from nexy import unauthorized
from nexy.decorators import Controller, UseGuard
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


@Controller("/account")
@UseGuard(require_login)
class AccountController:
    async def get(self) -> dict:
        return {"ok": True}
```
<!-- /router -->

<!-- router:custom -->
Die Authentifizierung ist beispielsweise mit einer Abhängigkeit des Routers verbunden, den sie schützt, wie in FastAPI; Wer der Benutzer ist, bleibt Ihre Entscheidung:

```python filename="src/account.py"
from fastapi import APIRouter, Depends

from nexy import unauthorized
from nexy.http import Request


def require_login(request: Request) -> None:
    if not request.session.get("user"):
        unauthorized(scheme="Bearer")


api = APIRouter(prefix="/account", dependencies=[Depends(require_login)])
```
<!-- /router -->

Der Grund dafür ist nicht Minimalismus an sich: Ein Framework, das Ihr ORM oder Ihre Authentifizierungsbibliothek auswählt, hat etwas entschieden, über das nur Ihre Anwendung entscheiden kann.

## Nächste Schritte

- [Projektstruktur](project-structure.md): jeder Ordner und jede Datei eines Projekts
- [Glossar](../reference/glossary.md): dieselben Wörter in einem alphabetischen Index
- [Wie Nexy funktioniert](how-nexy-works.md): die Schichten, wer was baut und was Nexy Ihnen überlässt
