# Dynamische Routen

Ein in eckigen Klammern geschriebenes Pfadsegment entspricht einem beliebigen Wert und übergibt ihn an die Seite oder den Handler.

## Dynamische Segmente

`blog/[slug].nexy` dient `/blog/{slug}`. Deklarieren Sie auf einer Seite das Segment als Eigenschaft. Nehmen Sie es in einem Python-Handler als Argument.

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str]
---
<h1>{{ slug }}</h1>
```

```python filename="src/routes/api/users/[id].py"
async def GET(id: int):
    return {"id": id}
```

## Typisierte Segmente

Die Annotation entscheidet über den Typ.

| Wobei | Konvertierung |
|---|---|
| `.py` Handler | jede FastAPI Typanmerkung (`int`, `UUID`, `Enum`...) |
| `.nexy` Seite | `int` und `float` werden konvertiert; alles andere bleibt eine Schnur |

Ein Wert, der nicht mit der Annotation übereinstimmt, ist **nicht gefunden**: `/api/users/abc` antwortet `404`, da eine dynamische Route jede URL erfasst und eine URL, die nicht konvertiert werden kann, einfach nicht existiert. Siehe [Validierung und Fehler](../handlers/validation-and-errors.md).

## Catch-All-Segmente

`docs/[...path].nexy` dient `/docs/{path:path}`. Die restlichen Segmente kommen als eine Zeichenfolge an, einschließlich Schrägstrichen.

```nexy filename="src/routes/docs/[...path].nexy"
---
path: prop[str]
---
<pre>{{ path }}</pre>
```

`/docs/a/b/c` ergibt `path == "a/b/c"`.

## Routengruppen

Ein Verzeichnis in Klammern organisiert Dateien, die nicht in der URL erscheinen. Es nimmt immer noch an der [Vererbung](../inheritance.md) teil: seine `layout.*` und `dependencies.py` gelten für das, was sich darin befindet.

```text
src/routes/
├─ (marketing)/
│  ├─ layout.nexy        applies to the pages in the group
│  ├─ pricing.nexy       /pricing
│  └─ about.nexy         /about
└─ (app)/
   └─ dashboard.nexy     /dashboard
```

Verwenden Sie Gruppen, um verschiedenen Abschnitten unterschiedliche Layouts zu geben, ohne ihre URLs zu ändern.

## Priorität

Statische Routen gewinnen über dynamische und dynamische über Catch-Alls: `/blog/new` entspricht `blog/new.nexy` vor `blog/[slug].nexy`.

## Eine Datei pro URL

Zwei Dateien, die zur gleichen URL aufgelöst werden, werden beide registriert. Platzieren Sie `blog.nexy` nicht neben `blog/index.nexy` und mischen Sie auch nicht `index.nexy` und `index.py` für denselben Pfad.

## Nächste Schritte

- [Seiten](README.md)
- [Fehlerseiten](../errors/README.md)
- [Dateikonventionen](../../../reference/file-conventions.md)
