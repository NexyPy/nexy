# Frontend-Seiten

Eine **Seite** ist die Grundeinheit einer Nexy-Anwendung. Es handelt sich um eine URL-adressierbare Ressource, die durch eine Datei unter `src/routes/` definiert wird. 

Unabhängig vom verwendeten Client-Framework folgt jede Seite denselben universellen Lebenszyklus- und Architekturbeschränkungen.

## Der Seitenlebenszyklus

Wenn ein Benutzer zu einer Seite navigiert, führt Nexy die folgenden Schritte aus:

1.  **Route Matching**: Der Router identifiziert die Datei, die der URL entspricht.
2.  **Datenabruf**: Der Server führt die Logik der Seite aus (Python Frontmatter oder Framework Loader), um die erforderlichen Daten abzurufen.
3.  **Komposition**: Die Seite wird in ihr nächstgelegenes `layout.nexy` (oder Framework-Layout) eingebunden.
4.  **Rendering**: Das Ergebnis wird in HTML gerendert (über Jinja2, Markdown oder Framework SSR).
5.  **Hydration**: Wenn die Seite ein Client-Framework verwendet, hängt der Browser die interaktive Logik an den statischen HTML-Code an.

## Routing und URLs

Das Routing erfolgt ausschließlich dateibasiert. Die URL wird durch den Pfad der Datei unter `src/routes/` abzüglich der Erweiterung bestimmt.

### Dynamische Segmente
Um eine Route zu erstellen, die je nach Parameter (z. B. einem Benutzerprofil) variiert, verwenden Sie eckige Klammern:
- `src/routes/user/[id].tsx` → `/user/123`

Der Wert des Segments (`123`) steht der Seite über den `useParams()`-Hook von `@nexy/client` zur Verfügung.

### Routengruppen
In Klammern eingeschlossene Ordner werden vom Router ignoriert, ermöglichen Ihnen jedoch das Gruppieren von Dateien für Organisationszwecke oder gemeinsame Layouts:
- `src/routes/(auth)/login.tsx` → `/login`

## Seitenmetadaten
Jede Seite kann Metadaten (Titel, Beschreibung, OpenGraph-Tags) definieren, die Nexy in die Dokumenthülle einfügt. In `.nexy`-Dateien erfolgt dies im Frontmatter; In Framework-Dateien wird es über einen `metadata`-Export bereitgestellt.

## Framework-Implementierung
Die oben genannten Konzepte sind universell. Um zu erfahren, wie Sie eine Seite in Ihrem spezifischen Framework implementieren, lesen Sie die Anleitung **Unterschiede**:

- [React Unterschiede](../react/differences.md)
- [Vue Unterschiede](../vue/differences.md)
- [Svelte Unterschiede](../svelte/differences.md)
- [Solid Unterschiede](../solid/differences.md)
- [Preact Unterschiede](../preact/differences.md)
