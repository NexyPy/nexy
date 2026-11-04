# ISR (stale-while-revalidate)

## Definition

ISR speichert den HTML-Code einer Seite pro URL zwischen und stellt ihn bereit, bis das Fenster abläuft. Die abgelaufene Kopie
wird weiterhin bereitgestellt, während im Hintergrund ein neues gerendert wird: das ist *stale-while-revalidate*.

## Wie es funktioniert

`revalidate = N` im Titelblatt einer `.nexy`-Seite schaltet es ein. `N` ist eine Anzahl von Sekunden; a
Ein fehlender, null oder negativer Wert bedeutet, dass überhaupt kein Cache vorhanden ist.

Der Cache-Schlüssel ist nur der **Anfragepfad** - `request.scope["path"]`. Die Abfragezeichenfolge ist kein Teil
davon.

| Was | Wert |
|---|---|
| Schlüssel | der URL-Pfad (`/blog/hello`) |
| Speicherung | im Speicher, im Prozess, der die Seite rendert |
| Gebunden | 256 Einträge pro Prozess, zuletzt verwendet entfernt |
| Antwortheader | `cache-control: public, s-maxage=N, stale-while-revalidate=N` |

## Rendering-Lebenszyklus

1. Es kommt eine Anfrage für eine Seite, die `revalidate` deklariert.
2. Noch kein Eintrag: Die Seite wird gerendert, gespeichert und zurückgegeben.
3. Eintrag jünger als `N` Sekunden: Wird unverändert zurückgegeben, die Seite wird nicht gerendert.
4. Eintrag älter als `N` Sekunden: Der **veraltete**-Eintrag wird sofort und eine Hintergrundaufgabe zurückgegeben
   rendert ein neues.
5. Wenn das Hintergrund-Rendering ansteigt, bleibt der veraltete Eintrag bestehen und die nächste veraltete Anfrage versucht es erneut.

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

`N` ist eine einfache Ganzzahl. An anderer Stelle gibt es keine Überschreibung pro Route, und `.py`-Handler sind keine Seiten:
Sie betreten diesen Cache niemals.

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

Die erste Anfrage an `/blog/hello` wird gerendert und gespeichert. Die nächsten 300 Sekunden werden aus dem Speicher bereitgestellt.
`/blog/other` ist ein separater Eintrag, der eigenständig gerendert und gespeichert wird. In einem echten Projekt kommt `posts`.
aus einer Datenbank oder einem Dienst, einmal pro Regeneration aufgerufen.

## Einschränkungen

**Nexy garantiert** dass der Cache-Schlüssel der Pfad ist, die veraltete Kopie während der Neugenerierung bereitgestellt wird und die
Der Speicher ist begrenzt und threadsicher.

**Übereinstimmung** ist eine Seite, die `revalidate` als öffentlichen Inhalt deklariert. Schreiben Sie es so, als ob jeder Besucher
sieht das gleiche HTML.

**Ihre Bewerbung ist verantwortlich für** alles Weitere:

| Grenze | Was es bedeutet |
|---|---|
| Abfragezeichenfolge ignoriert | `/search?q=a` und `/search?q=b` teilen sich einen Eintrag. Speichern Sie keine Suchseite im Cache. |
| Sitzung nicht isoliert | Die Antwort lautet `public` und der HTML-Code des ersten Besuchers wird allen bereitgestellt. Lesen Sie die Sitzung niemals auf einer Seite mit `revalidate`. |
| Keine serverseitige Invalidierung | Nichts löscht einen Eintrag, bevor sein Fenster endet. `revalidate(...)` innerhalb einer [Aktion](../guides/actions.md) weist den **Browser** nur an, einen Pfad neu zu laden; Dieser Cache wird nicht berührt. |
| Ein Cache pro Prozess | Mehrere Worker unterhalten mehrere Caches mit unterschiedlichen Inhalten. |
| Gleichzeitige Regenerationen | Nichts dedupliziert sie: Zehn veraltete Anfragen können zehn Renderings starten. |
| Fehler bleiben stumm | Eine fehlgeschlagene Neugenerierung stellt weiterhin die alte Seite bereit; Der Fehler wird protokolliert und nicht zurückgegeben. |

## Nächste Schritte

- [SSR](ssr.md): wie die Seite gerendert wird, bevor sie zwischengespeichert wird
- [Aktionen](../guides/actions.md): der `revalidate`-Header und was er nicht tut
- [Leistung](../deployment/performance.md)
- [Seiten](../routing/fbr/pages/README.md): Layouts und dynamische Segmente