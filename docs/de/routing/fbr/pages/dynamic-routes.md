# Dynamische Routen

Ein in eckigen Klammern geschriebenes Pfadsegment entspricht einem beliebigen Wert und übergibt ihn an die Seite oder den Handler.

## Dynamische Segmente

`blog/[slug].nexy` dient `/blog/{slug}`. Deklarieren Sie auf einer Seite das Segment als Eigenschaft. in einem Python
Handler, nimm es als Argument.

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
| `.py` Handler | jede FastAPI-Typanmerkung (`int`, `UUID`, `Enum`...) |
| `.nexy` Seite | `int` und `float` werden konvertiert; alles andere bleibt eine Schnur |

Ein Wert, der nicht mit der Anmerkung übereinstimmt, ist **nicht gefunden**: `/api/users/abc` antwortet `404`, weil
Eine dynamische Route erfasst jede URL und eine URL, die nicht konvertiert werden kann, existiert einfach nicht. Siehe
[Validierung und Fehler](../handlers/validation-and-errors.md).

## Catch-All-Segmente

`docs/[...path].nexy` dient `/docs/{path:path}`. Die restlichen Segmente kommen als eine Zeichenfolge an,
Schrägstriche enthalten.

```nexy filename="src/routes/docs/[...path].nexy"
---
path: prop[str]
---
<pre>{{ path }}</pre>
```

`/docs/a/b/c` ergibt `path == "a/b/c"`.

## Routengruppen

Ein Verzeichnis in Klammern organisiert Dateien, die nicht in der URL erscheinen. Es nimmt immer noch teil
[Vererbung](../inheritance.md): Seine `layout.*` und `dependencies.py` gelten für das, was sich darin befindet.

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

Statische Routen gewinnen gegenüber dynamischen und dynamische gegenüber Catch-Alls:
`/blog/new` entspricht `blog/new.nexy` vor `blog/[slug].nexy`.

## Eine Datei pro URL

Zwei Dateien, die zur gleichen URL aufgelöst werden, werden beide registriert. Setzen Sie nicht `blog.nexy` daneben
`blog/index.nexy` oder mischen Sie `index.nexy` und `index.py` für denselben Pfad.

## Nächste Schritte

- [Seiten](README.md)
- [Fehlerseiten](../errors/README.md)
- [Dateikonventionen](../../../reference/file-conventions.md)