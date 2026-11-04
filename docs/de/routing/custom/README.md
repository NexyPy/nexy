# Benutzerdefinierte Routing-Integration

Mit Nexy können Sie eine vorhandene FastAPI-App als Router in Ihr Projekt einbinden. Dies ist nützlich, wenn Sie die Backend-Logik eines anderen Dienstes wiederverwenden, mit APIs von Drittanbietern integrieren oder eine Verbundanwendung mit mehreren Routing-Anliegen erstellen möchten.

Im Gegensatz zu dateibasierten und modularen Routern, die in Nexy integriert sind, ist ein benutzerdefinierter Router einfach ein `APIRouter`, den Sie in Ihre Anwendung einbinden.

## Wann sollte ein benutzerdefinierter Router verwendet werden?

- **Drittanbieterdienste**: Sie verfügen über eine bestehende FastAPI-App, die Sie über den Nexy-Client verfügbar machen möchten.
- **Code-Wiederverwendung**: Backend-Logik aus einem anderen Projekt in einen Router extrahieren und in ein neues einbinden.
- **Multi-Tenant- oder Micro-Frontend-Muster**: Jeder Mandant oder jedes Modul stellt seinen eigenen Router bereit.
- **Schrittweise Migration**: Beginnen Sie mit einem `APIRouter` und entwickeln Sie es später zu einem vollständigen Nexy-Modul weiter.

## Wie es funktioniert

```python
from fastapi import APIRouter
from nexy import useRouter

# An existing FastAPI router (from another service)
third_party = APIRouter()
@third_party.get("/info")
async def info():
    return {"name": "Foo"}

# In your nexyconfig.py:
useRouter = third_party
```

Der Router wird automatisch vom Router-Resolver von Nexy gemountet. Die Routen sind unter demselben URL-Muster wie in der Original-App verfügbar. Es ist keine zusätzliche Konfiguration erforderlich.

## Einen benutzerdefinierten Router erstellen

1. **Erstellen Sie den Router**
   „Python
   aus Fastapi-Import APIRouter

   api = APIRouter()
   @api.get("/status")
   async def status():
       return {"status": "ok"}
   „

2. **Verweisen Sie darauf in `nexyconfig.py`**
   „Python
   von .my_backend Import-API

   useRouter = api
   „

3. **Zufahrtswege**
   - Dateibasierte Seiten (`.nexy`, `.md`) und modulare Handler können wie jede andere Route auf `/status` verweisen.
   - Der Router läuft im gleichen Prozess, sodass Abhängigkeiten, Datenbankverbindungen und Authentifizierung genau wie in der Original-App funktionieren.

## Integration mit anderen Routern

Ein Nexy-Projekt kann Folgendes kombinieren:

- **Dateibasiertes Routing** (`src/routes/`) für Seiten und einfache Endpunkte
- **Modulares Routing** (`useRouter = AppModule`) für strukturierte Backends
- **Benutzerdefiniertes Routing** (`useRouter = APIRouter`) für Code von Drittanbietern

Alle drei existieren nebeneinander; Jede Route wird nur einmal registriert. Der dateibasierte Router wird immer gescannt, wenn `src/routes/` vorhanden ist.

## CLI-Zugriff auf die enthaltene App

Die Befehle `nexy dev` und `nx` funktionieren auf dem gemounteten Router genau wie bei einem integrierten Router. Sie erhalten:

- Hot-Reload für Endpunkte, die im benutzerdefinierten Router definiert sind (wenn dieser `nexy` oder die üblichen Entwicklungsserverfunktionen von FastAPI verwendet)
- Validierung in `nexyconfig.py` (alle `APIRouter` Werke)
- Automatisch generierte Dokumente für die enthaltenen Routen (sofern Sie sie aktivieren)

## Sicherheit und Isolation

Da der Router im Lieferumfang enthalten und nicht über `app.mount` gemountet ist, gibt es keine zusätzliche ASGI-Schicht. Der Router befindet sich im selben Anwendungsobjekt wie Ihre dateibasierten und modularen Routen. Das bedeutet:

- Die vom benutzerdefinierten Router hinzugefügte Middleware gilt für alle Anfragen.
- Im benutzerdefinierten Router definierte Schutzvorrichtungen und Abhängigkeitsinjektionen können auf denselben Container wie Ihr eigener Code zugreifen (wenn Sie modulare Injektion verwenden).
- Es gibt kein anderes URL-Präfix als das, was der Router selbst definiert.

Wenn Sie eine Isolierung benötigen, binden Sie den Router in eine Unteranwendung ein, bevor Sie ihn einbinden, oder verwenden Sie Standard-FastAPI-Techniken.

## Beispiel: Einbinden eines vorhandenen FastAPI-Projekts

Angenommen, Sie haben `auth.py` in einem anderen Paket:

```python
from fastapi import FastAPI, APIRouter

auth = FastAPI(title="Auth service")
api = APIRouter()

@api.get("/login")
async def login():
    return {"msg": "Login"}

auth.include_router(api)
```

In `nexyconfig.py`:

```python
from other_package.auth import api

useRouter = api
```

Der `/login`-Endpunkt ist jetzt von Ihrer Nexy-Site aus erreichbar, ohne eine Codezeile verschieben zu müssen.

## Wie man anfängt

1. Erstellen Sie Ihr `APIRouter` (oder suchen Sie eines in einem vorhandenen Paket).
2. Zeigen Sie `useRouter` darauf in `nexyconfig.py`.
3. Greifen Sie über Ihre Seiten, Handler oder Client-Frameworks auf seine Routen zu.
4. Wenn Sie mehr Kontrolle benötigen, wandeln Sie den benutzerdefinierten Router mit `AppModule` in einen modularen Router um.

## Nächste Schritte

- [Dateibasiertes Routing](../fbr/README.md) – Erstellen Sie Seiten und einfache Handler aus Dateien.
- [Modulares Routing](../modular/README.md) – Strukturierte Backends mit Injektion und Wachen.
- [Routenhandler](../fbr/handlers/README.md) – Definieren Sie Python-Endpunkte.

Der benutzerdefinierte Router bietet Ihnen die Flexibilität, vorhandenen FastAPI-Code wiederzuverwenden und gleichzeitig die Einfachheit dateibasierter Seiten und die modulare Struktur beizubehalten.