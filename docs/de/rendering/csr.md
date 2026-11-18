# CSR (clientseitiges Rendering)

## Definition

CSR übergibt die Navigation an den Browser: Nach dem ersten Dokument wird beim Wechseln zwischen Seiten nicht mehr der Server nach HTML gefragt. In Nexy handelt es sich um eine **Projektentscheidung**, nicht um eine Seite-eins-Entscheidung – `useCSR = True` stellt die gesamte Anwendung client-geroutet dar.

## Wie es funktioniert

```python filename="nexyconfig.py"
from nexy.core.models import NexyConfigModel
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = react()
    useCSR = True
```

Das Projekt ändert dann seine Form:

| | Servermodus (`False`) | Client-Modus (`True`) |
|---|---|---|
| Routen | `.nexy`, `.md`, `.mdx` | `.tsx`, `.jsx`, `.vue`, `.svelte` |
| Dokument | `layout.nexy` | die Wurzel `layout.tsx` / `.vue` / `.svelte` besitzt `<html>`, `<head>`, `<body>` |
| Client-Komponenten | Inseln innerhalb einer Seite | die Seiten selbst |
| `.nexy` unter `src/routes/` | das Seitenformat | abgelehnt vor `nx dev`, `nx start` und `nx build` |
| Navigation | eine vollständige Anfrage per Link | Der Client-Router |

`.md` und `.mdx` bleiben gültig: Nexy rendert sie auf dem Server im Client-Layout und der Client-Router übernimmt von dort aus. `.py` Abfertiger sitzen neben den Routen und werden von FastAPI bedient.

## Rendering-Lebenszyklus

1. Die Anfrage erreicht den dateibasierten Router, der die passende Route und deren Layouts findet.
2. Das Root-Layout rendert das **gesamte Dokument** in Node – die erste Antwort enthält bereits das echte `<html>`, keine leere Shell.
3. Nexy fügt die Client-Assets und eine JSON-Beschreibung der Seite vor `</body>` ein.
4. Der Browser hydratisiert dieses Dokument. Verschachtelte Layouts behalten von da an ihren Zustand.
5. Ein Link zu einer anderen Route wird vom Client-Router verarbeitet: keine Dokumentanforderung, die Seite wird im Browser gerendert.

In der Entwicklung wird das Dokument bei Bedarf vom Vite-Entwicklungsserver gerendert. In der Produktion wird es einmal beim Erstellen gerendert: Eine statische Route erhält ihr Dokument, eine dynamische Route erhält eines pro deklariertem statischen Parameter oder eine Shell – die Layouts um eine leere Seite – wenn sie keines deklariert.

## Wann zu verwenden

- Dashboards, Editoren, alles, was sich wie eine Anwendung verhält.
- Eine Python API mit einer Client-Anwendung darüber.
- Eine Seite, auf der jede Interaktion lokal ist und eine Rundreise spürbar wäre.

## Konfiguration

| Einstellung | Wert |
|---|---|
| `useFF` | erforderlich: `useCSR` ohne Client-Framework wird abgelehnt |
| `useCSR` | `True` |
| `useRouter` | muss aus bleiben: Der modulare Router wird im Client-Modus abgelehnt |

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

## Rendern Sie eine dynamische Route vorab

Eine dynamische Route wie `src/routes/blog/[slug].tsx` stimmt mit jedem Wert überein, sodass der Build nicht wissen kann, welche Seiten gerendert werden sollen. Exportieren Sie `generateStaticParams()` von der Seite, um sie aufzulisten: `nexy build` rendert ein vollständiges Dokument pro Eintrag und `nexy start` stellt es für diesen Pfad bereit. Die Next.js-Namen `getStaticPaths` und `getStaticParams` werden ebenfalls akzeptiert, und die Funktion kann `async` sein.

```tsx filename="src/routes/blog/[slug].tsx"
export async function generateStaticParams() {
  return [{ slug: "hello" }, { slug: "world" }]
}

export default function Post({ slug }: { slug: string }) {
  return <h1>{slug}</h1>
}
```

Jeder Eintrag ist ein Objekt von Parametern oder `{ params: {...} }`, da `getStaticPaths` sie zurückgibt. Der Build schreibt:

| Datei in `__nexy__/client/static/` | Serviert für |
|---|---|
| `src/routes/blog/[slug]/blog/hello.html` | `/blog/hello` |
| `src/routes/blog/[slug]/blog/world.html` | `/blog/world` |
| `src/routes/blog/[slug].shell.html` | irgendein anderes `/blog/...` |

Ein Pfad, den die Liste nicht benennt, funktioniert trotzdem: Er ruft die Shell und die Layouts um eine leere Seite ab und die Seite erscheint, sobald der Browser ausgeführt wurde. In `nexy dev` wird jeder Pfad auf Anfrage gerendert, egal ob aufgelistet oder nicht.

## Einschränkungen

- **Das gesamte Projekt.** Sie können nicht eine CSR-Seite in ein Servermodus-Projekt mischen: Wählen Sie den Modus für die Anwendung aus und verwenden Sie dann [Inseln](islands.md) für die interaktiven Teile einer Servermodus-Seite.
- **Keine `.nexy` Routen.** Alles, was Sie in `.nexy` geschrieben haben, muss eine Framework-Komponente werden.
- **Serverdaten durchlaufen Endpunkte.** Eine Client-Route kann die Datenbank zur Renderzeit nicht lesen; es ruft einen `.py`-Handler oder eine [Aktion](../guides/actions.md) auf.
- **Eine dynamische Route beginnt bei einer Shell, es sei denn, sie listet ihre Parameter auf.** Siehe [Eine dynamische Route vorab rendern](#pre-render-a-dynamic-route).
- **CSR ist keine leere Seite und auch kein SPA.** Das erste Dokument wird vom Server gerendert; Es ist die Navigation, die im Browser stattfindet.

## Nächste Schritte

- [Servermodus und Clientmodus](../routing/fbr/modes.md): die Prüfungen und die abgelehnten Dateien
- [Layouts](../routing/fbr/layouts/README.md): Welche Datei besitzt das Dokument?
- [SSR](ssr.md): die Standardeinstellung, Seite für Seite
- [Frontend](../guides/frontend.md): der Entwicklungsserver und der Client-Build
