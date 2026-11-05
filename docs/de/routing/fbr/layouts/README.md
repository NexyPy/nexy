# Layouts

Ein Layout umschließt jede Seite unterhalb seines Verzeichnisses. Verschachtelte Layouts: Die Seite wird im Layout ihres Verzeichnisses gerendert, das wiederum im Layout des übergeordneten Verzeichnisses bis zum Stammlayout gerendert wird.

Es gibt eine Seite pro Layoutdateityp:

| Datei | Modus | Besitzt das HTML-Dokument | Seite |
|---|---|---|---|
| `layout.nexy` | Server (`useCSR = False`) | ja, im Stammverzeichnis | [layout.nexy](../../../views/nexy/layouts.md) |
| `layout.tsx` | Client (`useCSR = True`) | ja, an der Wurzel (React, Solid, Preact) | [React](../../../views/react/differences.md), [Solid](../../../views/solid/differences.md), [Preact](../../../views/preact/differences.md) |
| `layout.vue` | Client | ja, im Stammverzeichnis | [layout.vue](../../../views/vue/differences.md) |
| `layout.svelte` | Client | ja, im Stammverzeichnis | [layout.svelte](../../../views/svelte/differences.md) |

Ein Projekt verwendet eine Familie. `layout.nexy` und `layout.tsx` können nicht im selben Projekt leben: Der Servermodus verfügt über `.nexy`-Layouts und der Client-Modus über Framework-Layouts. Siehe [Servermodus und Clientmodus](../modes.md).

## Wie der Browser das Dokument übernimmt

Im Client-Modus rendert Nexy das Root-Layout in Node, sodass die erste Antwort ein vollständiges Dokument ist. Der Browser übernimmt es dann auf zwei Arten:

| Rahmen | Übernahme | Was es bedeutet |
|---|---|---|
| React, Solid | **Hydrierung** des gesamten Dokuments | Das Server-HTML wird unverändert wiederverwendet |
| Preact, Vue, Svelte | **Körperübernahme** | Das Framework erstellt den Seitenkörper und tauscht ihn gegen den aus, den der Server gesendet hat |

Preact, Vue und Svelte können kein ganzes Dokument hydratisieren: Preacts `hydrate` erstellt ein zweites `<html>`-Element, Vues Compiler löscht ein `<script>` aus einer Client-Vorlage und Svelte kann `<html>`, `<head>` oder `<body>` nicht im Browser erstellen. Für sie sind also die Attribute `<html>`, `<head>` und `<body>` diejenigen, die der Server gesendet hat, und nur der Körper wird vom Browser erstellt. In der Praxis:

- Platzieren Sie Titel, Meta-Tags, Schriftarten und Theme-Skript im Root-Layout: Sie werden vom Server gerendert und bleiben unverändert.
- Eine Bindung an `<html>`, `<head>` oder `<body>` (z. B. eine reaktive Klasse) wird vom Server angewendet, aber nicht im Browser aktualisiert. Ändern Sie sie über ein Skript, wie es das Theme-Skript tut.
- Der Browser rendert den Textkörper von Grund auf, anstatt das Server-Markup wiederzuverwenden. Daher wird der Textkörper einmal in derselben Aufgabe wie beim ersten Rendern ersetzt.

## Das Root-Layout

Das Root-Layout ist `src/routes/layout.<ext>`. Es wird von `nx new` erstellt und ist der einzige Ort, an dem `<!DOCTYPE html>`, `<html>`, `<head>` und `<body>` (jedes Framework und `.nexy`) geschrieben werden. Seiten und verschachtelte Layouts wiederholen sie niemals.

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

Im Client-Modus bleibt ein Layout gemountet, während der Benutzer zwischen den Seiten navigiert, die es gemeinsam nutzen: Sein DOM, sein Status und seine Scroll-Position bleiben erhalten. Im Servermodus ist jede Navigation ein neues Dokument.

## Nächste Schritte

- [layout.nexy](../../../views/nexy/layouts.md)
- [layout.tsx](../../../views/react/differences.md)
- [Vererbung](../inheritance.md)
