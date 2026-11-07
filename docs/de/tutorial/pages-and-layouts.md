# Erstellen Sie eine Notizen-App mit Nexy, Teil 2: Seiten und Layouts

Teil 2 fügt die Seite hinzu, auf der die Notizen aufgelistet sind, und zeigt, wie das Layout sie in das HTML-Dokument einbettet.

**Bevor Sie beginnen:** das Projekt von [Teil 1](create-the-project.md), wobei `nexy dev` läuft.

## Fügen Sie die Notizenseite hinzu

<!-- router:fbr,custom -->
Eine Seite ist eine Datei unter `src/routes/` und ihr Pfad ist ihre URL. Erstellen Sie die Notizenseite:

```nexy filename="src/routes/notes/index.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

`notes/index.nexy` antwortet `/notes`.
<!-- /router -->

<!-- router:modular -->
Ein Controller antwortet auf eine URL und gibt eine Ansicht zurück. Geben Sie den Notizen einen eigenen Ordner mit einer Ansicht:

```nexy filename="src/apps/notes/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<section class="app-page">
  <h1>Notes</h1>
  <ul>
    {% for note in notes %}
    <li>{{ note }}</li>
    {% endfor %}
  </ul>
</section>
```

und der Controller, der es bei `/notes` rendert:

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/notes/notes_view.nexy")})
```

Ein Controller antwortet erst, wenn ein Modul ihn auflistet. Fügen Sie es dem Root-Modul hinzu:

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController]
```
<!-- /router -->

Öffnen Sie <http://localhost:3000/notes>: Sie sollten zwei Aufzählungszeichen sehen. Der Teil zwischen den beiden `---`-Zeilen ist Python und wird auf dem Server ausgeführt. der Rest ist HTML mit Jinja2-Tags wie `{% for %}` und `{{ note }}`.

## Ändern Sie das Layout

<!-- router:fbr,custom -->
`src/routes/layout.nexy` besitzt das HTML-Dokument: `<html>`, `<head>` und `<body>`. Nexy umschließt jede Seite darin, auf der geschrieben steht `{{children | safe}}`.
<!-- /router -->
<!-- router:modular -->
`src/apps/layout.nexy` besitzt das HTML-Dokument: `<html>`, `<head>` und `<body>`. Der Controller umschließt seine Ansicht darin, indem er die Ansicht als `children` übergibt.
<!-- /router -->

Öffnen Sie das Layout und ändern Sie die Zeile `<title>Nexy App</title>` in:

```html
<title>Notes</title>
```

Speichern: Auf der Registerkarte des Browsers wird jetzt auf jeder Seite *Notizen* angezeigt.

## Geben Sie den Seiten Platz unter der Kopfzeile

Die Kopfzeile des Layouts ist fixiert: Sie bleibt oben im Fenster über der Seite. Die Seiten des Starters legen darunter ihren eigenen Platz fest; Die Seiten der Notizen-App teilen sich dafür eine Klasse, `app-page`, die jede Seite des Tutorials um ihren Inhalt legt. Fügen Sie es am Ende von `src/globale.css` hinzu, dem Stylesheet, das jede Seite bereits lädt:

```css
/* The pages of the notes app: one readable column below the fixed header. */
.app-page {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  max-width: 42rem;
  margin: 0 auto;
  padding: 8rem 1.5rem 5rem;
}

.app-page h1 {
  font-size: 2rem;
}

.app-page form {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  gap: 0.5rem;
}

.app-page label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.app-page input:not([type="hidden"]) {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border-second);
  border-radius: 0.375rem;
  background: var(--background);
}

.app-page button {
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  background: var(--foreground);
  color: var(--background);
  cursor: pointer;
}

.app-page a {
  text-decoration: underline;
}
```

Tailwind, das der Starter verwendet, entfernt die Ränder von Formularfeldern: Diese Regeln geben sie zurück, sodass die Formen der nächsten Teile sichtbar sind.

## Was du gelernt hast

<!-- router:fbr,custom -->
- Eine `.nexy`-Datei unter `src/routes/` ist eine Seite; Sein Ordner und Name sind seine URL.
- Der Stamm `layout.nexy` umschließt jede Seite im HTML-Dokument.
<!-- /router -->
<!-- router:modular -->
- Ein Controller antwortet auf eine URL und rendert eine `.nexy`-Ansicht mit `useViews`; Ein Modul listet es auf.
- Auch das Layout ist eine Ansicht: Der Controller übergibt ihm die Seitenansicht als `children`.
<!-- /router -->
- Eine `.nexy`-Datei ist Python zwischen `---`, dann HTML mit Jinja2.
- `src/globale.css` enthält die Stile, die jede Seite gemeinsam hat, wie zum Beispiel `app-page`.

## Nächste Schritte

- [Teil 3: Dynamische Routen und eine API](dynamic-routes.md)
- [.nexy-Dateien](../views/nexy/README.md): Requisiten, Komponenten und Stile
