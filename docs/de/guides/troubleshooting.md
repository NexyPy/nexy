# Fehlerbehebung

Die Probleme, auf die die Leute zuerst stoßen, mit dem, was Sie sehen und was zu tun ist. Jedes einzelne stammt aus einem echten Lauf.

## Eine Seite antwortet mit 404, aber ihre Datei existiert

Schauen Sie sich das Terminal an, das `nx dev` oder `nx start` ausführt. Wenn eine Seite nicht importiert werden kann, meldet Nexy
der Fehler mit seiner Datei und Zeile, und die Route ist nicht registriert:

```text
nexy » error __nexy__/src/routes/index.py:18  ImportError: cannot import name 'FrameworkLogo' ...
```

Korrigieren Sie den dort genannten Import. Die übliche Ursache ist eine Komponente, deren Funktionsname nicht übereinstimmt
was Sie importieren (siehe nächster Punkt) und ein Tippfehler im Pfad.

## Eine `.nexy` Seite lässt sich nicht kompilieren: „Logic Parse Error“

```text
src/components/live-panel.nexy - Logic Parse Error: invalid syntax
```

Eine `.nexy`-Komponente wird als Python-Modul importiert, daher muss ihr Dateiname ein gültiger Name sein. Ein Bindestrich
ist nicht. Benennen Sie es in PascalCase, `LivePanel.nexy`, und importieren Sie es mit demselben Namen:

```nexy
from "@/components/LivePanel.nexy" import LivePanel
```

## Eine Komponente stellt ihre untergeordneten Elemente als Text dar `<slot />`

Eine `.nexy`-Komponente platziert ihre untergeordneten Elemente mit `<Slot />`, mit einem großen S. Ein Kleinbuchstabe `<slot />` ist
auf der Seite so belassen, wie sie ist. Vue, das über ein eigenes `<slot />` verfügt, ist nicht betroffen.

## Eine Requisite zeigt den Namen der Variablen

```nexy
<Icon path=icon />          renders: icon
<Icon path="{{ icon }}" />  renders: the value of icon
```

Ein Attribut ohne geschweifte Klammern ist Text. Fügen Sie den Jinja-Ausdruck in das Attribut ein, um einen berechneten Wert zu übergeben
Wert.

## Ein Wert in `{{ ... }}` wird leer gerendert

Jinja2 verbirgt eine undefinierte Variable. Deklarieren Sie jede Eigenschaft, die Sie im Frontmatter verwenden
(`title: prop[str] = ""`) und überprüfen Sie die Rechtschreibung.

## Dienstprogrammklassen haben keine Auswirkung auf einer `.nexy` Seite (UnoCSS)

UnoCSS liest eine Datei nur, wenn sich ihre Erweiterung in ihrer Inhaltspipeline befindet. Ein Serverprojekt erstellt
von `nx new` mit UnoCSS listet bereits `.nexy` auf; ein älterer braucht es in `uno.config.ts`:

```ts
content: {
  filesystem: ['src/**/*.nexy'],
  pipeline: { include: [/\.(vue|svelte|[jt]sx|mdx?|astro|html|nexy)($|\?)/] },
},
```

Tailwind findet `.nexy` Dateien selbstständig.

## Eine `.mdx` Seite fragt nach Paketen

```text
[nexy] MDX support requires optional packages that are not installed.
```

Installieren Sie sie im Projekt: `@mdx-js/rollup`, `remark-gfm` und `@mdx-js/react` (plus
`@mdx-js/esbuild` für `nx build`). MDX benötigt React oder Preact in `useFF`. Ohne ein Client-Framework,
Schreiben Sie die Seite als `.md`. Siehe [Markdown und MDX](../views/nexy/markdown.md).

## `No module named 'sqlmodel'` (oder ein beliebiges Paket), wenn ein Befehl gestartet wird

```text
nexy » nexyconfig.py cannot be loaded: No module named 'sqlmodel'. If it is a package, install it
in this Python (...) or activate the project's virtual environment.
```

Der Befehl wurde im falschen Python ausgeführt. Die Pakete Ihres Projekts (Ihr ORM, Ihre Bibliotheken) sind vorhanden
Es ist `.venv` und `uvx nexy` oder ein globales `nexy` läuft in einer eigenen Umgebung, die nichts davon hat
sie.

Aktivieren Sie die virtuelle Umgebung des Projekts aus dem Projektordner und führen Sie dann den Befehl erneut aus:

```bash
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

Die Eingabeaufforderung beginnt mit `(.venv)`, wenn sie aktiv ist. Oder überspringen Sie die Aktivierung mit
`uv run nexy dev`. Wenn das Paket wirklich im Projekt fehlt, fügen Sie es mit `uv add sqlmodel` hinzu.

## `nx dev` zeigt einen Fehler an und wartet

Wenn Ihre Anwendung nicht gestartet werden kann, meldet `nx dev` den Grund und wartet auf die nächste Dateiänderung. das tut es
nicht beenden. Korrigieren Sie die Datei und speichern Sie sie. Nur Strg+C stoppt es.

## Der Port ist belegt

`nx dev` nimmt den nächsten freien Port und druckt ihn. Um eines auszuwählen, verwenden Sie `--port` oder stellen Sie `usePort` ein
`nexyconfig.py`.

## Das Design blinkt weiß auf einer dunklen Seite

Das gespeicherte Design muss vor dem ersten Malen angewendet werden. Behalten Sie das kleine Skript des Starters im
`<head>` des Root-Layouts und fügen Sie `suppressHydrationWarning` auf `<html>` in React ein.

## Hängt immer noch fest

- Lesen Sie die Seite der Funktion im [Dokumentationsindex](../README.md).
- Wenn die Dokumente und der Code nicht übereinstimmen, ist der Code richtig: Bitte öffnen Sie eine
  [Problem](https://github.com/NexyPy/nexy/issues) beim Benennen der Seite.