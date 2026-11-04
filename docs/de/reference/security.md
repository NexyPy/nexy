# Sicherheit

Wie Nexy die eigene Angriffsfläche klein hält, welche Versionen es benötigt und wie man ein Projekt überprüft.

## Versionsböden

Nexy basiert auf FastAPI, Starlette, Jinja2, Vite und React. Eine Etage ist die niedrigste Version von Nexy
erlaubt; Jeder beantwortet einen veröffentlichten Ratgeber.

| Paket | Boden | Warum |
|---|---|---|
| `starlette` | 1.0.1 | CVE-2026-48710 (BadHost): Ein manipulierter `Host`-Header ändert den Pfad, den Starlette an die Middleware meldet, wodurch die auf `request.url.path` geschriebene Autorisierung umgangen wird. Von CISA als ausgenutzt aufgeführt. |
| `fastapi` | 0.133.0 | die erste Version, die ein festes Starlette akzeptiert |
| `jinja2` | 3.1.6 | Sandbox-Flucht durch den `attr`-Filter (CVE-2025-27516) |
| `vite` (Gerüstprojekte) | 6.4.3 | `server.fs.deny` Umgehung auf alternativen Windows-Pfaden (CVE-2026-53571); Die frühere Umgehung der Abfragezeichenfolge (CVE-2026-39364) betrifft nur Vite 7.1-7.3.1 und 8.0.0-8.0.4 |
| `react`, `react-dom` | 19.2.5 | Die 2026 React Advisorys betreffen die `react-server-dom-*` Pakete, die Nexy nicht verwendet; Der Boden hält die Linie geflickt |

Überprüfen Sie Ihre gelösten Versionen:

```bash
uv pip list | grep -i -E "starlette|fastapi|jinja2"
npm ls vite
```

## Regeln, denen Nexy folgt

- **Vertrauen Sie niemals dem Host-Header für Pfade.** Nexy liest `scope["path"]`, nicht `request.url.path`
  eine eigene Middleware (Verzeichnis-Middleware). Machen Sie dasselbe bei Ihnen.
- **Escape, was HTML erreicht.** An Client-Komponenten übergebene Requisiten, `Link` Attribute, `Image`,
  `Audio`- und `Video`-Attribute, Inhaltsverzeichnis-Anker und `HTTPException`-Details sind alles
  HTML-escaped. `| safe` in einer Vorlage schaltet dies aus: Verwenden Sie es niemals für Benutzereingaben.
- **Entwickler-Endpunkte sind nur Loopback und eng.** Der Dev-Render-Endpunkt
  (`/__nexy__/render`) akzeptiert nur Dateien unter `src/routes/` mit der Erweiterung `.tsx` oder `.jsx` und
  ist nur über den Entwicklungsserver erreichbar, der fremde `Host`-Header ablehnt.
- **Fehlerdetails gehen nicht verloren.** Eine Fehlerseite, die selbst fehlschlägt, zeigt nur den Statuscode an.
- **Produktionsantworten tragen sichere Überschriften.** `X-Content-Type-Options: nosniff` und
  `Referrer-Policy: strict-origin-when-cross-origin`, es sei denn, Ihr Code legt seinen eigenen fest. Die `Server`
  Header wird nicht gesendet. Fügen Sie `Strict-Transport-Security` und ein `Content-Security-Policy` in Ihrem hinzu
  Proxy oder Middleware: Sie hängen von Ihrer Domain ab.
- **Bei einem Absturz wird eine Referenz angezeigt, nicht der Fehler.** Siehe [Fehlerseiten](../routing/fbr/errors/README.md#unhandled-exceptions).
- **Kein `eval` und kein `shell=True` im Python-Code von Nexy.** Externe Programme werden mit einer Argumentliste ausgeführt.

## Durchführung der Audits

```bash
python scripts/audit_dependencies.py        # Python dependencies against the lock
npm audit                                    # in a scaffolded project
uv run bandit -r nexy -c .bandit             # static analysis of Nexy itself
```

Nexys eigenes Repository führt bei seinen Prüfungen den ersten und den dritten aus. Eine neue Beratung in einem Stockwerk darüber erfolgt durch Erhöhung des
Boden in `pyproject.toml` oder im Gerüst `package.json` und regeneriert dann das Schloss.

## Sichere Bereitstellung

- Stellen Sie `useTrustedHost` auf Ihre Domains ein: Es lehnt unerwartete `Host` Header vor jeder Route ab.
- Den Vite-Entwicklungsserver nicht offenlegen: `nx dev`behält ihn im Loopback hinter dem Nexy-Ursprung.
- Legen Sie `useDocs = False` fest, wenn das API-Schema nicht öffentlich sein soll.

Siehe [Middleware und Sicherheit](../guides/middleware-and-security.md).

## Quellen

- [CVE-2026-48710 (BadHost) in Starlette](https://www.penligent.ai/hackinglabs/cve-2026-48710/)
- [Vite-Beratung GHSA-fx2h-pf6j-xcff](https://github.com/advisories/GHSA-fx2h-pf6j-xcff) und
  [GHSA-v2wj-q39q-566r](https://github.com/advisories/GHSA-v2wj-q39q-566r)
- [Jinja2 CVE-2025-27516](https://advisories.gitlab.com/pypi/jinja2/CVE-2025-27516/)
- [React-Serverpakete CVE-2026-44907](https://www.wiz.io/vulnerability-database/cve/cve-2026-44907)

## Nächste Schritte

- [Middleware und Sicherheit](../guides/middleware-and-security.md)
- [Bereitstellen](../deployment/README.md)
- [Config](config.md)