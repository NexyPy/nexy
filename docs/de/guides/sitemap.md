# Wie füge ich einer Nexy-Site eine sitemap.xml und eine robots.txt hinzu?

Setzen Sie `useSiteUrl` in `nexyconfig.py`: Nexy stellt dann `/sitemap.xml` bereit, das jede statische Seite des Projekts auflistet, und ein `/robots.txt`, das Suchmaschinen darauf verweist.

## Schalten Sie es mit `useSiteUrl` ein.

`useSiteUrl` ist der öffentliche Ursprung der Website, den Suchmaschinen sehen:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useSiteUrl = "https://example.com"
```

`nx dev` und `nx start` beantworten dann beide Dateien. Ohne `useSiteUrl` gibt es keines davon, sodass ein Projekt niemals versehentlich die URL seines Entwicklungsservers veröffentlicht.

## Was die Sitemap auflistet

Die Sitemap gibt jede Seite als absolute URL auf `useSiteUrl` an:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://example.com/</loc></url><url><loc>https://example.com/about</loc></url></urlset>
```

Eine Route wird aufgelistet, wenn sie HTML auf einen `GET` auf einem festen Pfad antwortet:

<!-- router:fbr,custom -->
- eine Seite (`.nexy`, `.md`, `.mdx`, `.tsx`, `.jsx`, `.vue`, `.svelte`) wird aufgelistet;
- eine dynamische Seite wie `src/routes/users/[id].nexy` wird weggelassen: Nexy kann ihre Werte nicht kennen;
- Ein Python-Routenhandler antwortet JSON, daher wird er weggelassen.
<!-- /router -->

<!-- router:modular -->
- eine Controller-Route, die HTML mit `@UseResponse(response_class=HTMLResponse)` antwortet, wird aufgelistet;
- eine Route mit einem Pfadparameter wie `/users/{id}` wird weggelassen: Nexy kann seine Werte nicht kennen;
- Eine Route, die JSON antwortet, wird weggelassen.
<!-- /router -->

Eine im API-Schema verborgene Route (`include_in_schema=False`) wird ebenfalls weggelassen.

## Dem `robots.txt` dient es

```text
User-agent: *
Allow: /

Sitemap: https://example.com/sitemap.xml
```

## Schreiben Sie stattdessen Ihr eigenes

Ihre eigene Datei gewinnt immer und Nexy überschreibt sie nie:

- `public/robots.txt` oder `public/sitemap.xml` wird so serviert, wie es ist, so wie jede Datei von `public/` ist;
- Eine Route des Projekts bei `/robots.txt` oder `/sitemap.xml` behält ihren Pfad bei.

Schreiben Sie Ihre eigene Sitemap, um dynamische Seiten aufzulisten, beispielsweise eine URL pro Blog-Beitrag.

## Nächste Schritte

- [Seitenmetadaten](../routing/fbr/pages/metadata.md): Die Titel- und Beschreibungssuchmaschinen werden angezeigt
- [Konfiguration](../reference/config.md): jede Einstellung von `nexyconfig.py`
- [Deployment](../deployment/README.md): Bereitstellen des Projekts in der Produktion
