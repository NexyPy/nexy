# Layouts

Ein Layout umschließt jede Seite unterhalb seines Verzeichnisses. Layouts verschachteln: Die Seite wird innerhalb des Layouts von gerendert
sein Verzeichnis, das innerhalb des Layouts des übergeordneten Verzeichnisses bis zum Stammlayout gerendert wird.

Es gibt eine Seite pro Layoutdateityp:

| Datei | Modus | Besitzt das HTML-Dokument | Seite |
|---|---|---|---|
| `layout.nexy` | Server (`useCSR = False`) | ja, im Stammverzeichnis | [layout.nexy](../../../views/nexy/layouts.md) |
| `layout.tsx` | Client (`useCSR = True`) | ja, an der Wurzel (React, Solid, Preact) | [React](../../../views/react/differences.md), [Solid](../../../views/solid/differences.md), [Preact](../../../views/preact/differences.md) |
| `layout.vue` | Client | ja, im Stammverzeichnis | [layout.vue](../../../views/vue/differences.md) |
| `layout.svelte` | Client | ja, im Stammverzeichnis | [layout.svelte](../../../views/svelte/differences.md) |

Ein Projekt verwendet eine Familie. `layout.nexy` und `layout.tsx` können sich nicht im selben Projekt befinden: Server
Der Modus verfügt über `.nexy`-Layouts und der Client-Modus über Framework-Layouts. Siehe
[Servermodus und Clientmodus](../modes.md).

## Wie der Browser das Dokument übernimmt

Im Client-Modus rendert Nexy das Root-Layout in Node, sodass die erste Antwort ein vollständiges Dokument ist. Die
Der Browser übernimmt es dann auf zwei Arten:

| Rahmen | Übernahme | Was es bedeutet |
|---|---|---|
| React, Solid | **Hydrierung** des gesamten Dokuments | Das Server-HTML wird unverändert wiederverwendet |
| Preact, Vue, Svelte | **Körperübernahme** | Das Framework erstellt den Seitenkörper und tauscht ihn gegen den aus, den der Server gesendet hat |

Preact, Vue und Svelte können kein ganzes Dokument hydratisieren: Preacts `hydrate` erstellt ein zweites `<html>`
Element entfernt der Compiler von Vue ein `<script>` aus einer Client-Vorlage und Svelte kann kein `<html>` erstellen.
`<head>` oder `<body>` im Browser. Für sie gelten also `<html>`, `<head>` und die `<body>`-Attribute
diejenigen, die der Server gesendet hat, und nur der Text wird vom Browser erstellt. In der Praxis:

- Fügen Sie den Titel, die Meta-Tags, die Schriftarten und das Theme-Skript in das Root-Layout ein: Sie werden vom Server gerendert
  und bleib wie sie sind.
- Eine Bindung an `<html>`, `<head>` oder `<body>` (zum Beispiel eine reaktive Klasse) wird vom Server angewendet
  wird aber nicht im Browser aktualisiert. Ändern Sie sie über ein Skript, wie es das Theme-Skript tut.
- Der Browser rendert den Körper von Grund auf, anstatt das Server-Markup wiederzuverwenden, also ist der Körper es
  einmal ersetzt, in derselben Aufgabe wie beim ersten Rendern.

## Das Root-Layout

Das Root-Layout ist `src/routes/layout.<ext>`. Es wurde von `nx new` erstellt und ist der einzige Ort, an dem
schreibt `<!DOCTYPE html>`, `<html>`, `<head>` und `<body>` (jedes Framework und `.nexy`). Seiten und verschachtelt
Layouts wiederholen sie nie.

```text
src/routes/
├─ layout.*              root: the document
├─ index.*
└─ dashboard/
   ├─ layout.*           nested: UI only
   ├─ index.*
   └─ settings.*
```

`dashboard/index` wird als `root layout > dashboard layout > page` gerendert.

## Routengruppen

Ein Verzeichnis in Klammern kann ein eigenes Layout haben, ohne die URLs zu ändern:

```text
src/routes/
├─ layout.nexy
├─ (marketing)/
│  ├─ layout.nexy        wraps /pricing and /about only
│  ├─ pricing.nexy
│  └─ about.nexy
└─ (app)/
   └─ dashboard.nexy     only the root layout
```

## Beharrlichkeit

Im Client-Modus bleibt ein Layout gemountet, während der Benutzer zwischen den Seiten navigiert, die es gemeinsam nutzen: its
DOM, Status und Scrollposition bleiben erhalten. Im Servermodus ist jede Navigation ein neues Dokument.

## Nächste Schritte

- [layout.nexy](../../../views/nexy/layouts.md)
- [layout.tsx](../../../views/react/differences.md)
- [Vererbung](../inheritance.md)