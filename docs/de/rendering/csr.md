# CSR (clientseitiges Rendering)

## Definition

CSR übergibt die Navigation an den Browser: Nach dem ersten Dokument wird beim Wechseln zwischen Seiten nicht mehr gefragt
der Server für HTML. Bei Nexy handelt es sich um eine **Projekt**-Entscheidung, nicht um eine Seite eins – `useCSR = True` dreht sich um
Die gesamte Anwendung wird vom Client weitergeleitet.

## Wie es funktioniert

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

Das Projekt ändert dann seine Form:

| | Servermodus (`False`) | Clientmodus (`True`) |
|---|---|---|
| Routen | `.nexy`, `.md`, `.mdx` | `.tsx`, `.jsx`, `.vue`, `.svelte` |
| Dokument | `layout.nexy` | Die Wurzel `layout.tsx` / `.vue` / `.svelte` besitzt `<html>`, `<head>`, `<body>` |
| Client-Komponenten | Inseln innerhalb einer Seite | die Seiten selbst |
| `.nexy` unter `src/routes/` | das Seitenformat | abgelehnt vor `nx dev`, `nx start` und `nx build` |
| Navigation | eine vollständige Anfrage pro Link | der Client-Router |

`.md` und `.mdx` bleiben gültig: Nexy rendert sie auf dem Server innerhalb des Client-Layouts und die
Von dort übernimmt der Client-Router. `.py`-Handler sitzen neben den Routen und werden von FastAPI bedient.

## Rendering-Lebenszyklus

1. Die Anfrage erreicht den dateibasierten Router, der die passende Route und deren Layouts findet.
2. Das Root-Layout rendert das **gesamte Dokument** in Node – die erste Antwort trägt bereits das
   echt `<html>`, keine leere Hülle.
3. Nexy fügt die Client-Assets und eine JSON-Beschreibung der Seite vor `</body>` ein.
4. Der Browser hydratisiert dieses Dokument. Verschachtelte Layouts behalten von da an ihren Zustand.
5. Ein Link zu einer anderen Route wird vom Client-Router verarbeitet: Keine Dokumentanforderung, die Seite ist
   im Browser gerendert.

In der Entwicklung wird das Dokument bei Bedarf vom Vite-Entwicklungsserver gerendert. In der Produktion ist es so
Wird beim Erstellen einmal gerendert: Eine statische Route erhält ihr Dokument, eine dynamische Route erhält eines pro Deklaration
statischer Parameter oder eine Shell – die Layouts um eine leere Seite – wenn keine deklariert wird.

## Wann zu verwenden

- Dashboards, Editoren, alles, was sich wie eine Anwendung verhält.
- Eine Python-API mit einer Client-Anwendung darüber.
- Eine Seite, auf der jede Interaktion lokal ist und eine Rundreise zu spüren wäre.

## Konfiguration

| Einstellung | Wert |
|---|---|
| `useFF` | erforderlich: `useCSR` ohne Client-Framework wird abgelehnt |
| `useCSR` | `True` |
| `useRouter` | muss ausgeschaltet bleiben: Der modulare Router wird im Client-Modus abgelehnt |

Dateien und Ordner, die mit `_` oder `.` beginnen, werden bei diesen Prüfungen ignoriert.

## Beispiel

```tsx filename="src/routes/layout.tsx"
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head><title>My app</title></head>
      <body>{children}</body>
    </html>
  )
}
```

```tsx filename="src/routes/index.tsx"
export default function Home() {
  return <h1>Home</h1>
}
```

## Einschränkungen

- **Das gesamte Projekt.** Sie können nicht eine CSR-Seite in ein Projekt im Servermodus mischen: Wählen Sie den Modus für
  die Anwendung, dann verwenden Sie [islands](islands.md) für die interaktiven Teile einer Servermodus-Seite.
- **Keine `.nexy` Routen.** Alles, was Sie in `.nexy` geschrieben haben, muss eine Framework-Komponente werden.
- **Serverdaten durchlaufen Endpunkte.** Eine Client-Route kann die Datenbank zur Renderzeit nicht lesen; es
  ruft einen `.py`-Handler oder eine [Action](../guides/actions.md) auf.
- **Eine dynamische Route benötigt einen deklarierten statischen Parameter oder sie startet von einer Shell.** Exportieren
  `getStaticParams()` von der Seite – die Next.js-Namen `getStaticPaths` und `generateStaticParams`
  werden ebenfalls akzeptiert - ein Dokument pro Wert. Ohne sie trägt die Shell die Layouts und
  nicht die Seite: Die Seite erscheint, sobald der Browser ausgeführt wurde.
- **CSR ist keine leere Seite und auch kein SPA.** Das erste Dokument wird vom Server gerendert; es
  ist die Navigation, die im Browser stattfindet.

## Nächste Schritte

- [Servermodus und Clientmodus](../routing/fbr/modes.md): die Prüfungen und die abgelehnten Dateien
- [Layouts](../routing/fbr/layouts/README.md): Welche Datei besitzt das Dokument?
- [SSR](ssr.md): die Standardeinstellung, Seite für Seite
- [Frontend](../guides/frontend.md): der Entwicklungsserver und der Client-Build