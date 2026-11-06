# Frontend-Seiten

Eine **Seite** ist die Grundeinheit einer Nexy-Anwendung. Es handelt sich um eine URL-adressierbare Ressource, die durch eine Datei unter `src/routes/` definiert wird. 

Unabhängig vom verwendeten Client-Framework folgt jede Seite denselben universellen Lebenszyklus- und Architekturbeschränkungen.

## Der Seitenlebenszyklus

Wenn ein Benutzer zu einer Seite navigiert, führt Nexy die folgenden Schritte aus:

1.  **Route Matching**: Der Router identifiziert die Datei, die der URL entspricht.
2.  **Datenabruf**: Der Server führt den Python Frontmatter der Seite aus, um die benötigten Daten abzurufen.
3.  **Komposition**: Die Seite wird in ihr nächstgelegenes `layout.nexy` (oder Framework-Layout) eingebunden.
4.  **Rendering**: Das Ergebnis wird in HTML gerendert (über Jinja2, Markdown oder Framework SSR).
5.  **Hydration**: Wenn die Seite ein Client-Framework verwendet, hängt der Browser die interaktive Logik an den statischen HTML-Code an.

Schritte 2 bis 4 auf einer Seite im Servermodus: Der Frontmatter ruft ab, die Vorlage rendert und das Root-Layout umschließt das Ergebnis.

```nexy filename="src/routes/users.nexy"
---
from src.users import all_users

users = all_users()
---
<h1>Users</h1>
<ul>
  {% for user in users %}
  <li>{{ user.name }}</li>
  {% endfor %}
</ul>
```

## Routing und URLs

Das Routing erfolgt ausschließlich dateibasiert. Die URL wird durch den Pfad der Datei unter `src/routes/` abzüglich der Erweiterung bestimmt.

```text
src/routes/
├─ index.tsx            /
├─ about.tsx            /about
└─ blog/
   ├─ index.tsx         /blog
   └─ [slug].tsx        /blog/hello-world
```

### Dynamische Segmente
Um eine Route zu erstellen, die je nach Parameter (z. B. einem Benutzerprofil) variiert, verwenden Sie eckige Klammern:
- `src/routes/user/[id].tsx` → `/user/123`

Der Wert des Segments (`123`) steht der Seite über den `useParams()`-Hook von `@nexy/client` zur Verfügung.

```tsx filename="src/routes/user/[id].tsx"
import { useParams } from "@nexy/client";

export default function User() {
  const { id } = useParams<{ id: string }>();
  return <h1>User {id}</h1>;
}
```

### Routengruppen
In Klammern eingeschlossene Ordner werden vom Router ignoriert, ermöglichen Ihnen jedoch das Gruppieren von Dateien für Organisationszwecke oder gemeinsame Layouts:
- `src/routes/(auth)/login.tsx` → `/login`

```text
src/routes/
├─ layout.tsx
└─ (auth)/
   ├─ layout.tsx        wraps /login and /signup only
   ├─ login.tsx         /login
   └─ signup.tsx        /signup
```

## Seitenmetadaten
Jede Seite kann Metadaten (Titel, Beschreibung, OpenGraph-Tags) definieren, die Nexy in die Dokumenthülle einfügt. Eine `.nexy`-Seite setzt es im Titelblatt, mit einem Literal oder mit `setMetadata`:

```nexy filename="src/routes/blog.nexy"
---
metadata = {"title": "Blog", "description": "Posts about Nexy"}
---
<h1>Blog</h1>
```

`setMetadata` ist Python: Eine `.tsx`-, `.vue`- oder `.svelte`-Seite hat keinen `metadata`-Export, also schreiben Sie im Client-Modus den Titel und die Meta-Tags im Root-Layout. Siehe [Seitenmetadaten](../../routing/fbr/pages/metadata.md) für jedes Feld.

## Framework-Implementierung
Die oben genannten Konzepte sind universell. Informationen zum Implementieren einer Seite in Ihrem spezifischen Framework finden Sie im Leitfaden **Unterschiede**:

- [React Unterschiede](../react/differences.md)
- [Vue Unterschiede](../vue/differences.md)
- [Svelte Unterschiede](../svelte/differences.md)
- [Solid Unterschiede](../solid/differences.md)
- [Preact Unterschiede](../preact/differences.md)
