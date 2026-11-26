# Middleware und Sicherheit

Nexy läuft auf FastAPI und Starlette, daher gilt deren Middleware. Die häufigsten sind eine Zeile in `nexyconfig.py`.

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

Jedes `use*`-Wörterbuch wird als Schlüsselwortargumente an die passende Starlette-Middleware übergeben: `CORSMiddleware`, `GZipMiddleware`, `TrustedHostMiddleware`, `SessionMiddleware`.

## Ihre eigene Middleware

```python filename="nexyconfig.py"
from my_app.middleware import RequestIdMiddleware


class NexyConfig(NexyConfigModel):
    useMiddlewares = [RequestIdMiddleware]
```

`useMiddlewares` nimmt ASGI-Middleware-Klassen an.

## Ratenbegrenzung

`useRateLimit` antwortet `429 Too Many Requests` auf eine Client-Adresse, die mehr als `requests` Anfragen in einem Fenster von `per` Sekunden sendet.

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useRateLimit = {"requests": 60, "per": 60, "paths": ["/api/", "/_nx_"]}
```

Nexy garantiert, dass eine Anfrage, die das Limit überschreitet, einen `429` mit einem `Retry-After`-Header erhält, die verbleibenden Sekunden im Fenster, und niemals Ihre Routen, Aktionen oder Middleware erreicht.

Nexy garantiert, dass ohne `useRateLimit` keine Rate-Limit-Middleware hinzugefügt wird.

Nexy garantiert, dass die `useHealth`-Sonden niemals begrenzt sind.

`paths` ist optional: Ohne es ist jeder Pfad begrenzt. Serveraktionen werden unter `/_nx_` bereitgestellt, sodass das Präfix sie alle einschränkt.

Das Fenster ist fest und wird von allen Clients gemeinsam genutzt: Die Zählungen beginnen bei jedem Vielfachen von `per` Sekunden erneut. Ein Client kann daher bis zu zweimal `requests` über den Rand eines Fensters senden.

Die Zählungen bleiben jedem Arbeiter im Gedächtnis erhalten. Wenn `useWorkers` über eins liegt, kann ein Client `requests` an jeden Worker senden und die Zählungen beginnen erneut, wenn der Server neu startet.

Die Kundenadresse ist diejenige, die uvicorn bei der Anfrage angibt. Hinter einem Reverse-Proxy auf demselben Computer liest uvicorn es von `X-Forwarded-For`; Geben Sie für einen Proxy auf einem anderen Computer seine Adresse in der Umgebungsvariablen `FORWARDED_ALLOW_IPS` an, oder jeder Client teilt die Adresse des Proxys.

Ihre Anwendung ist für ein Limit verantwortlich, das von mehreren Workern oder Servern gemeinsam genutzt wird: einem Reverse-Proxy oder einem Store wie Redis.

## HTTPS

Stellen Sie HTTPS direkt mit `useSslKeyfile` und `useSslCertfile` bereit oder beenden Sie TLS an einem Reverse-Proxy und legen Sie `useHTTPSRedirect` fest. In der Entwicklung bleibt der Vite-Entwicklungsserver auf Loopback-HTTP hinter dem Nexy-Ursprung, sodass TLS ihn nie erreicht.

## Checkliste für die Produktion

- `useDocs = False`, wenn das OpenAPI-Schema nicht öffentlich sein soll.
- `useTrustedHost` auf Ihre Domains eingestellt, um Host-Header-Angriffe zu blockieren.
- `useCORS` mit expliziter Herkunft, niemals `["*"]` zusammen mit Anmeldeinformationen.
- Ein echter `secret_key` für Sitzungen, gelesen aus der Umgebung.
- Props an Client-Komponenten übergebene Komponenten werden von Nexy mit HTML-Escapezeichen versehen. Markieren Sie Benutzereingaben nicht als `| safe` in Vorlagen.

## Wachen und Abhängigkeiten

Der Schutz pro Route verwendet FastAPI Abhängigkeiten. Ein `dependencies.py` in einem Routenverzeichnis gilt für alles darunter: siehe [Abhängigkeiten](../routing/fbr/dependencies/README.md). Verwenden Sie im modularen Router [`@UseGuard`](../routing/modular/guards-and-metadata.md).

## Nächste Schritte

- [Konfiguration](../reference/config.md): jedes Middleware-Feld
- [Bereitstellen](../deployment/README.md)
- [Leistung](../deployment/performance.md)
