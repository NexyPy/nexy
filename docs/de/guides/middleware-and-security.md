# Middleware und Sicherheit

Nexy läuft auf FastAPI und Starlette, daher gilt deren Middleware. Die häufigsten sind eine Zeile in
`nexyconfig.py`.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useCORS = {
        "allow_origins": ["https://app.example.com"],
        "allow_methods": ["GET", "POST"],
        "allow_credentials": True,
    }
    useGZip = {"minimum_size": 1000}
    useTrustedHost = {"allowed_hosts": ["example.com", "*.example.com"]}
    useHTTPSRedirect = True
    useSession = {"secret_key": "change-me"}
```

Jedes `use*`-Wörterbuch wird als Schlüsselwortargumente an die passende Starlette-Middleware übergeben:
`CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `SessionMiddleware`.

## Ihre eigene Middleware

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` nimmt ASGI-Middleware-Klassen an.

## HTTPS

Stellen Sie HTTPS direkt mit `useSslKeyfile` und `useSslCertfile` bereit oder beenden Sie TLS an einem Reverse-Proxy
und stellen Sie `useHTTPSRedirect` ein. In der Entwicklung bleibt der Vite-Entwicklungsserver auf Loopback-HTTP hinter dem
Nexy-Ursprung, daher erreicht TLS ihn nie.

## Produktionscheckliste

- `useDocs = False` wenn das OpenAPI-Schema nicht öffentlich sein soll.
- `useTrustedHost` auf Ihre Domains eingestellt, um Host-Header-Angriffe zu blockieren.
- `useCORS` mit expliziter Herkunft, niemals `["*"]` zusammen mit Anmeldeinformationen.
- Ein echtes `secret_key` für Sitzungen, gelesen aus der Umgebung.
- An Client-Komponenten übergebene Requisiten werden von Nexy mit HTML-Escapezeichen versehen. Benutzereingabe nicht markieren `| safe` in
  Vorlagen.

## Schutz und Abhängigkeiten

Der Schutz pro Route nutzt FastAPI-Abhängigkeiten. Ein `dependencies.py` in einem Routenverzeichnis gilt für
alles darunter: siehe [Abhängigkeiten](../routing/fbr/dependencies/README.md). Im modularen Routereinsatz
[`@UseGuard`](../routing/modular/guards-and-metadata.md).

## Nächste Schritte

- [Config](../reference/config.md): jedes Middleware-Feld
- [Bereitstellen](../deployment/README.md)
- [Leistung](../deployment/performance.md)