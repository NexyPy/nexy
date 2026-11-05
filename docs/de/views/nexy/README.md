# .nexy-Dateien

Eine `.nexy`-Datei ist eine Komponente: Python oben, HTML in der Mitte, CSS unten.

**Bevor Sie beginnen:** ein Projekt, das durch den [Schnellstart](../../getting-started/quick-start.md) erstellt wurde. Eine `.nexy`-Datei benötigt keine Build-Konfiguration: `nx dev` kompiliert sie beim Speichern.

```nexy filename="src/routes/blog/[slug].nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```

## Frontmatter

Alles zwischen den beiden `---`-Zeilen ist Python. Importe werden aufgelöst, wenn die Komponente kompiliert wird; Der Rest wird für jede Anfrage ausgeführt, sodass der Anfragestatus gelesen werden kann.

| Was | Beispiel |
|---|---|
| Ein Modul importieren | `import json`, `from datetime import datetime` |
| Eine Komponente importieren | `from "@/components/card.nexy" import Card` |
| Eine Eigenschaft deklarieren | `title: prop[str] = "Default"` |
| Berechnen Sie einen Wert | `year = datetime.now().year` |
| Lesen Sie die Anfrage | `pathname = usePathname()` |
| Seite zwischenspeichern (ISR) | `revalidate = 60` |

## Eigenschaften

Eigenschaften sind die API der Komponente. `prop[type]` deklariert den Typ, `= value` gibt einen Standardwert an. Eine Eigenschaft ohne Standard muss vom übergeordneten Element übergeben werden.

Importe, die mit einem Alias ​​beginnen, werden über `useAliases` aufgelöst. Das Setup `nx new` schreibt Zuordnungen von `@` zu `src`, was bedeutet, dass `@/components/card.nexy` `src/components/card.nexy` bedeutet.

## Vorlage

Unterhalb der Vorderseite befindet sich HTML mit Jinja2. Variablen aus der Frontmatter und den Eigenschaften liegen im Gültigkeitsbereich.

```html
{% for item in items %}
  <li>{{ item.name }}</li>
{% endfor %}

{% if user %}
  <p>Welcome, {{ user.name }}</p>
{% endif %}
```

Autoescaping ist **aus**: Vorlagen sind der eigene HTML-Code des Projekts, daher wird `{{ value }}` wie geschrieben eingefügt. Entfliehen Sie selbst unsicheren Werten mit `{{ value | e }}`. `| safe` ändert also nichts.

> [!NOTE]
> Wickeln Sie JavaScript ein, das `{{` oder `{%` in `{% raw %}...{% endraw %}` enthält. Frameworks wie Vue und Svelte verwenden dieselben geschweiften Klammern.

## Komponenten

Jedes importierte Callable, dessen Name mit einem Großbuchstaben beginnt, kann als Tag verwendet werden. Der Compiler schreibt es in einen Jinja-Aufruf um: Attribute werden zu Schlüsselwortargumenten.

```nexy filename="src/routes/index.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```

Die letzte Zeile ist genau `{{ Audio("/theme.mp3", controls=True) }}`. Beide Syntaxen gelten für die integrierten Helfer `Image`, `Link`, `Audio` und `Video` – siehe [Komponenten](components.md#two-syntaxes-one-function).

Untergeordnete Elemente werden durch `<Slot />` (Großbuchstabe S) innerhalb der untergeordneten Komponente und durch `{{ children }}` innerhalb eines Layouts gerendert.

Übergeben Sie einen berechneten Wert mit Jinja innerhalb des Attributs: `<Icon path="{{ icon }}" size="{{ size }}" />`. Ein bloßer Name wie `path=icon` ist der Text `icon`, nicht die Variable. Um einer Komponente eine CSS-Klasse zu geben, deklarieren Sie eine `class_name`-Requisite: `class` ist ein Python-Schlüsselwort.

> [!NOTE]
> Ein Hilfstag ist immer selbstschließend. Die Übergabe von Inhalten an `Link` erfolgt über dessen `children`-Argument (`<Link href="/about" children="About" />`), nicht über den Elementinhalt.

## Stile

`<style>`-Blöcke werden mit der Seite ausgegeben, die sie deklariert. Sie haben keinen Gültigkeitsbereich: Ein Klassenname, der in zwei Komponenten verwendet wird, ist eine Klasse. Setzen Sie Ihren Klassen ein Präfix oder einen Namensraum.

## Regeln, die Zeit sparen

- Eine Komponente pro Datei. Der Dateiname ist der Komponentenname in PascalCase (`CopyChip.nexy`). Eine `.nexy`-Komponente wird als Python-Modul importiert: Ein Bindestrich im Namen (`copy-chip.nexy`) wird nicht kompiliert.
- Deklarieren Sie Requisiten, bevor Sie sie verwenden: Eine nicht deklarierte Variable wird als leere Zeichenfolge gerendert, da die undefinierte Variable von Jinja2 hier stumm ist.
- Behalten Sie Nebenwirkungen innerhalb der Funktionen bei – der Frontmatter wird bei jeder Anfrage erneut ausgeführt.

## Nächste Schritte

- [Markdown und MDX](markdown.md): Inhaltsseiten
- [ISR](../../rendering/isr.md): Eine Seite pro Pfad zwischenspeichern
- [CSR](../../rendering/csr.md): clientseitiges Rendering
