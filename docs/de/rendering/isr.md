# ISR (stale-while-revalidate)

## Definition

ISR speichert den HTML-Code einer Seite pro URL zwischen und stellt ihn bereit, bis das Fenster abläuft. Die abgelaufene Kopie wird weiterhin bereitgestellt, während eine neue im Hintergrund gerendert wird: das ist *stale-while-revalidate*.

## Wie es funktioniert

`revalidate = N` im Titelblatt einer `.nexy`-Seite schaltet es ein. `N` ist eine Anzahl von Sekunden; Ein fehlender, null oder negativer Wert bedeutet, dass überhaupt kein Cache vorhanden ist.

Der Cache-Schlüssel ist nur der **Anfragepfad** - `request.scope["path"]`. Die Abfragezeichenfolge ist nicht Teil davon.

| Was | Wert |
|---|---|
| Schlüssel | der URL-Pfad (`/blog/hello`) |
| Lagerung | ausgewählt durch `useISRCache`: Speicher standardmäßig, Datei, Redis oder ein benutzerdefinierter Speicher |
| Gebunden | 256 Einträge für den Speicher, zuletzt verwendet, entfernt; file und Redis behalten Einträge, bis sie ungültig werden |
| Antwortheader | `cache-control: public, s-maxage=N, stale-while-revalidate=N` |

Jede ISR-Antwort trägt diesen Header, einschließlich des ersten Renderings und eines Fallback-Renderings, wenn der Store ausgefallen ist. Ein CDN kann damit eine eigene Kopie derselben öffentlichen URL behalten.

## Rendering-Lebenszyklus

1. Es kommt eine Anfrage für eine Seite, die `revalidate` deklariert.
2. Noch kein Eintrag: Die Seite wird gerendert, gespeichert und zurückgegeben.
3. Eintrag jünger als `N` Sekunden: wird unverändert zurückgegeben, die Seite wird nicht gerendert.
4. Eintrag älter als `N` Sekunden: Der **veraltete**-Eintrag wird sofort zurückgegeben und eine Hintergrundaufgabe rendert einen neuen.
5. Wenn das Rendern im Hintergrund fehlschlägt, bleibt der veraltete Eintrag erhalten und die nächste veraltete Anfrage versucht es erneut.
6. Wenn der Speicher fehlschlägt, wird die Seite gerendert und ohne zwischengespeicherten Eintrag zurückgegeben. Die Anfrage ist immer noch erfolgreich.

## Wann zu verwenden

- Der gleiche HTML-Code für jeden Besucher: ein Blog-Beitrag, eine Produktseite, eine Dokumentationsseite.
- Die Seite wird oft gelesen und ändert sich selten.
- Die Daten können einige Sekunden alt sein, ohne dass es jemand merkt.

## Konfiguration

```nexy filename="src/routes/blog/index.nexy"
---
revalidate = 60
---
<h1>Rendered at most once per minute</h1>
```

`N` ist eine einfache Ganzzahl. An anderer Stelle gibt es keine Pro-Route-Überschreibung, und `.py`-Handler sind keine Seiten: Sie gelangen nie in diesen Cache.

## Wählen Sie einen Shop

Stellen Sie `useISRCache` in `nexyconfig.py` ein:

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useISRCache = "file"
```

| Wert | Speichern | Geteilt von |
|---|---|---|
| nicht eingestellt, `None` oder `"memory"` | Prozessspeicher, begrenzt auf 256 Einträge | ein Arbeiter |
| `"file"` | JSON-Dateien in `.nexy/isr` | Arbeiter auf einem Host |
| `{"type": "file", "directory": ".cache/isr"}` | JSON-Dateien im angegebenen Verzeichnis | Arbeiter auf einem Host |
| `"redis"` | Redis bei `redis://localhost:6379/0` | Jeder Worker, der den Server erreicht |
| `{"type": "redis", "url": "redis://cache:6379/0"}` | Redis unter dieser URL | Jeder Worker, der den Server erreicht |
| `{"type": "redis", "client": client}` | der Redis-Client, den Sie übergeben | Jeder Worker, der den Server erreicht |
| ein Objekt mit `get`, `set` und `invalidate` | Ihr eigener Laden | was auch immer es teilt |

Der Redis-Store benötigt das Client-Paket: `uv add redis`. Es wird nicht mit Nexy installiert. Ein benutzerdefinierter Speicher implementiert das `ISRCache`-Protokoll von `nexy.modules.runtime.cache`; Sein `get` gibt ein `CacheEntry` oder `None` zurück.

Dateieinträge werden atomar geschrieben, sodass ein Mitarbeiter niemals eine halb geschriebene Seite liest. Worker, die dasselbe Verzeichnis oder denselben Redis-Server verwenden, lesen denselben Eintrag. Ein kaputter Store kostet nur einen Rendervorgang: Er beantwortet die Anfrage nie mit einem Fehler.

## Beispiel

Ein Blogbeitrag, der eine Datenbank liest:

```nexy filename="src/routes/blog/[slug].nexy"
---
revalidate = 300
slug: prop[str] = "untitled"
posts = {"hello": {"title": "Hello"}, "other": {"title": "Other"}}
post = posts.get(slug, {"title": "Untitled"})
---
<h1>{{ post.title }}</h1>
```

Die erste Anfrage an `/blog/hello` wird gerendert und gespeichert. Die nächsten 300 Sekunden werden vom ausgewählten Store bedient. `/blog/other` ist ein separater Eintrag, der eigenständig gerendert und gespeichert wird. In einem realen Projekt stammt `posts` aus einer Datenbank oder einem Dienst, der einmal pro Regeneration aufgerufen wird.

## Was ein CDN teilen kann und was nicht

Ein CDN, das `cache-control` berücksichtigt, kann eine Kopie von `/blog/hello` für `s-maxage` Sekunden behalten und sie während der erneuten Validierung bereitstellen. Diese Kopie wird zwischen Besuchern und Mitarbeitern geteilt, da in der Antwort `public` steht.

Ein CDN kennt den Nexy-Store nicht. `revalidate()` in einer [Aktion](../guides/actions.md) entfernt den Eintrag aus dem konfigurierten Nexy-Speicher, löscht jedoch kein CDN. Das CDN behält seine Kopie, bis sein eigenes Fenster endet oder bis Sie seine Bereinigung konfigurieren.

Geben Sie einem CDN keine Seite, deren HTML von einem Besucher abhängt. Die Antwort lautet `public`, und Nexys Schlüssel ist allein der Pfad: Zwei Abfragezeichenfolgen auf einem Pfad teilen sich einen Eintrag. Eine Sitzung, ein Cookie oder eine Benutzer-ID im HTML kann einem anderen Besucher bereitgestellt werden.

## Einschränkungen

**Nexy garantiert**, dass der Cache-Schlüssel der Pfad ist, die veraltete Kopie während der Neugenerierung bereitgestellt wird und ein Speicherfehler auf ein Rendern zurückfällt.

**Laut Konvention** ist eine Seite, die `revalidate` deklariert, öffentlicher Inhalt. Schreiben Sie es so, als würde jeder Besucher den gleichen HTML-Code sehen.

**Ihre Bewerbung ist für** alles Weitere verantwortlich:

| Begrenzen | Was es bedeutet |
|---|---|
| Abfragezeichenfolge ignoriert | `/search?q=a` und `/search?q=b` teilen sich einen Eintrag. Speichern Sie keine Suchseite im Cache. |
| Sitzung nicht isoliert | Die Antwort lautet `public` und der HTML-Code des ersten Besuchers wird allen bereitgestellt. Lesen Sie die Sitzung niemals auf einer Seite mit `revalidate`. |
| CDN nicht gelöscht | `revalidate()` löscht den Nexy-Store, nicht ein CDN oder einen anderen Proxy davor. |
| Keine TTL in Datei- und Redis-Stores | Einträge bleiben bestehen, bis `revalidate()` oder Ihre eigene Bereinigung sie entfernt. Der Speicher löscht den zuletzt verwendeten Eintrag nach 256. |
| Gleichzeitige Regenerationen | Nichts dedupliziert sie: Zehn veraltete Anfragen können zehn Renderings starten. |
| Fehler schweigen | Ein fehlgeschlagener Regenerierungs- oder Speichervorgang stellt die Seite weiterhin bereit. Der Fehler wird nicht zurückgegeben. |

## Nächste Schritte

- [SSR](ssr.md): wie die Seite gerendert wird, bevor sie zwischengespeichert wird
- [Aktionen](../guides/actions.md): der Header `revalidate` und die Speicherungültigmachung
- [Konfiguration](../reference/config.md#server): `useISRCache`
- [Leistung](../deployment/performance.md)
- [Seiten](../routing/fbr/pages/README.md): Layouts und dynamische Segmente
