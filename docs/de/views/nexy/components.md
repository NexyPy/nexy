# Komponenten

Nexy exportiert eine kleine Reihe von Hilfsprogrammen, die HTML-Strings zurückgeben. Jedes wird in einer `.nexy`-Vorlage auf zwei Arten verwendet: als Jinja-Aufruf oder als HTML-Tag.

## Zwei Syntaxen, eine Funktion

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```
<!-- /router -->

Beide Zeilen erzeugen das gleiche Markup:

```html
<audio preload="metadata" controls><source src="/theme.mp3" type="audio/mp3" /></audio>
```

Der Compiler schreibt `<Audio ... />` in `{{ Audio(...) }}` um, sodass die Tag-Form keine zweite API ist: Attribute sind die Schlüsselwortargumente der Funktion.

## Regeln der Tag-Form

| Im Tag | Wird |
|---|---|
| `<Audio src="/a.mp3" />` | `Audio(src="/a.mp3")` |
| `controls=True` | `controls=True`, ein echter Boolescher Wert |
| `width=640` | `width=640`, eine Zahl |
| `src="{{ url }}"` | `src=(url)`, bewertet in Jinja |
| irgendein anderes `value` | `"value"`, eine Zeichenfolge |

- Das Tag muss mit einem Großbuchstaben beginnen und in die Frontmatter importiert werden; andernfalls löst der Compiler `Missing Import: <Name> used but not declared.` aus.
- Die Tag-Form ist **selbstschließend**. `<Audio src="/a.mp3" />` und `{{ Audio("/a.mp3") }}` sind gleichwertig; Das Schreiben von untergeordneten Elementen innerhalb eines Hilfstags wird nicht unterstützt.
- Ein bloßes HTML-Attribut ist hier kein boolescher Wert: `controls` wird zu `controls=""`, was falsch ist. Schreiben Sie `controls=True`.

> [!NOTE]
> `class_name` ist das dokumentierte Schlüsselwort für CSS-Klassen. Zusätzliche Schlüsselwortargumente werden zu HTML-Attributen, sodass `class="nav"` auch die Ausgabe erreicht.

## Bild

```nexy
---
from nexy import Image
---
{{ Image("/logo.png", alt="Logo", width=128, height=32) }}

<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

`Image(src, alt="", width=None, height=None, loading="lazy", class_name=None, **attrs)` rendert ein `<img>` standardmäßig mit Lazy Loading.

## Link

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` rendert ein `<a data-nexy-link>`, das vom Client-Router verarbeitet wird. Mit `prefetch=True` wird das Ziel durch Schweben oder Berühren des Links durch `window.__nexy_prefetch` erwärmt.

> [!NOTE]
> Die Tag-Form nimmt die Bezeichnung als `children` an, nicht als Elementinhalt: `<Link href="/about" children="About" />`. Um Markup in einen Link einzufügen, verwenden Sie das Aufrufformular mit `children=` oder eine `.nexy`-Komponente, die ein `<Slot />` rendert.

## Audio und Video

```nexy
---
from nexy import Audio, Video
---
{{ Audio("/theme.mp3", controls=True) }}
{{ Video("/demo.mp4", width=640, height=360, muted=True, sources=["/demo.webm", "/demo.mp4"]) }}

<Audio src="/theme.mp3" controls=True />
<Video src="/demo.mp4" width=640 height=360 muted=True />
```

`Audio(src, controls=True, autoplay=False, loop=False, muted=False, preload="metadata", class_name=None, sources=None, **attrs)` und `Video(src, width=None, height=None, ...)` rendern native Player. `sources` fügt `<source>` Tags mit dem von jeder Erweiterung abgeleiteten MIME-Typ hinzu.

## Eine Komponente, die Sie selbst schreiben

Eine wiederverwendbare `.nexy`-Komponente ist eine Datei unter `src/components/`: Python Requisiten oben, HTML unten. Es wird wie jedes andere Python-Modul importiert.

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest notes" tone="warm">
  <p>Everything published this week.</p>
</Card>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest notes" tone="warm">
  <p>Everything published this week.</p>
</Card>
```
<!-- /router -->

`title` hat keinen Standardwert, daher muss die Seite ihn übergeben; `tone` fällt auf `"neutral"` zurück. Der Markup zwischen den Tags kommt innerhalb von `<Slot />` (Großbuchstabe S) an. Siehe [.nexy-Dateien](README.md#components) für Requisiten, Slots und die Regeln der Tag-Form.

## Importieren einer Client-Komponente

Importieren Sie aus einer `.nexy`-Datei eine Framework-Komponente nach Pfad. Der Compiler mountet es auf dem Client und übergibt die Attribute als Requisiten:

```nexy
---
from "@/components/Counter.tsx" import Counter
---
<Counter start="0" />
```

`Import(path, framework, symbol)` macht dasselbe in Python:

```python
from nexy import Import

counter = Import("@/components/Counter.tsx", "react", "Counter")
html = counter(start=0)
```

Die gleiche Importsyntax löst `.json`-, `.css`- und Bilddateien in ihre URLs auf.

## Vorlage und Vite

`Template().render(path, context)` rendert eine Vorlagendatei (Jinja2 oder Markdown wird in HTML für `.md` Routen gerendert). `Template().invalidate(path)` löscht es aus dem Cache.

`Vite()` gibt die Client-Tags für den aktuellen Modus zurück: das HMR-Skript in der Entwicklung, das erstellte Client-Bundle in der Produktion. Nexy ruft es für jede Seite auf; man braucht es selten direkt.

## Noch nicht implementiert

`Form` und `Script` sind exportierte Platzhalter ohne Verhalten. Verlassen Sie sich nicht auf sie.

## Nächste Schritte

- [.nexy-Dateien](README.md): Hier werden diese Helfer verwendet
- [React](../react/differences.md): Importieren von `.tsx` Komponenten
- [Frontend](../../guides/frontend.md): wie Client-Komponenten gebündelt werden
