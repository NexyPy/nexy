# Projektstruktur

Jede Datei in einem Nexy-Projekt hat einen Job. Diese Seite sagt welche.

## Oberste Ebene

```text
my-app/
├─ src/
│  ├─ routes/            file-based routes (FBR)
│  │  ├─ index.nexy      → /
│  │  ├─ layout.nexy     shared layout, not a route
│  │  └─ api/hello.py    → /api/hello
│  ├─ apps/              modular router, decorators (optional, next to routes/)
│  ├─ components/        imported components (a convention, not enforced)
│  └─ globale.css        global styles (created by `nexy new`)
├─ public/               served at /
├─ nexyconfig.py         project configuration
├─ pyproject.toml
├─ package.json          only with a client framework
├─ vite.config.ts        only with a client framework
└─ __nexy__/             build output - generated, never edited
```

Um einen Ordner auszuwählen, fragen Sie nach der Datei:

- **Etwas, das der Browser öffnen kann** – eine Route: `src/routes/`.
- **Ein Teil, das von mehreren Routen verwendet wird** – eine Komponente oder ein Modul: `src/components/`, `src/`.
- **Eine Datei wurde so bereitgestellt, wie sie ist** - `public/`.
- **Ein Controller des modularen Routers** - `src/apps/`.
- **Generiert** - `__nexy__/`; Bearbeiten Sie es niemals.

> [!WARNING]
> `src/routes/` wird gescannt: Ein dort platzierter Helfer wird zur Route. Setzen Sie einen Helfer ein, der keine Route darstellt
> außerhalb von `src/routes/` oder beginnen Sie den Namen mit `_`.

## `src/routes/`

Jede Datei wird zu einer Route, mit Ausnahme der unten aufgeführten reservierten Namen. Der Dateipfad abzüglich der Erweiterung lautet
die URL - siehe [routing](../routing/README.md).

| Datei | Rolle |
|---|---|
| `layout.nexy` | umschließt Geschwister- und untergeordnete Seiten |
| `errors.nexy` | 500 Seiten für das Verzeichnis |
| `notfound.nexy` | 404-Seite für das Verzeichnis |
| `dependencies.py` | Gemeinsame FastAPI-Abhängigkeiten für das Verzeichnis |
| `__init__.py` | Python-Paketmarkierung |
| `loading.nexy` | reserviert – von Routen ausgeschlossen, aber es hat noch keinen Laufzeiteffekt |

Jeder Seitenname existiert auch pro Framework. Wenn `react()` konfiguriert ist, `layout.jsx` und `layout.tsx`
sind genau wie `layout.nexy` reserviert. Die Listen sind in `nexy/core/config.py` eingebaut.
(`LAYOUT_FILE_NAMES`, `ERROR_FILE_NAMES`, `NOTFOUND_FILE_NAMES`, `LOADING_FILE_NAMES`).

> [!NOTE]
> `notfound.nexy` und `errors.nexy` werden nur installiert, wenn eine Kopie vorhanden ist
> Routen-Root. Eine Kopie in ein Unterverzeichnis verfeinert dann die Seite für dieses Präfix.

## `src/apps/`

Das Verzeichnis `nexy new` wird für den modularen Router verwendet: Controller, Module und Provider-Register
ihre Routen durch Dekoratoren von `nexy.decorators`, dann wird das Aggregat `APIRouter` gemountet
mit `useRouter` in `nexyconfig.py`.

Ein Projekt kann beide Router haben: `useRouter` mountet den modularen Router und `src/routes/` wird gescannt
wann immer dieses Verzeichnis existiert. Siehe [modulares Routing](../routing/modular/README.md).

## `public/`

Hier werden Dateien aus dem Stammverzeichnis der Website bereitgestellt: `/favicon.ico`, `/robots.txt`, Bilder, Schriftarten.

## `__nexy__/`

Erstellt von `nx build` (und von `nx dev` für die benötigten Teile). Es enthält:

- die kompilierten Routenmodule als Python-Paket (`__nexy__/src/routes/...`);
- die generierten Client-Einstiegspunkte (`main.ts`, `vite.ts`, `*.auto.ts`);
- `client/` nach einem Vite-Build – Assets, Manifest, vorgerendertes HTML;
- `build-cache.json`.

Behandeln Sie das gesamte Verzeichnis als Wegwerfverzeichnis: Löschen Sie es und erstellen Sie es neu. Bei einer manuellen Bearbeitung geht die Änderung verloren
beim nächsten Build. Fügen Sie es zu `.gitignore` hinzu.

## Nächste Schritte

- [Routing](../routing/README.md): Wie ein Pfad zu einer URL wird
- [Config](../reference/config.md): jede Projektoption
- [Frontend](../guides/frontend.md): Vite, Styling und der Client-Build