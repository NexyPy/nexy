# Créez une application de notes avec Nexy, partie 2 : pages et mises en page

La partie 2 ajoute la page qui répertorie les notes et montre comment la mise en page l'enveloppe dans le document HTML.

**Avant de commencer :** le projet de [partie 1](create-the-project.md), avec `nexy dev` en cours d'exécution.

## Ajouter la page de notes

<!-- router:fbr,custom -->
Une page est un fichier sous `src/routes/`, et son chemin est son URL. Créez la page de notes :

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

`notes/index.nexy` répond à `/notes`.
<!-- /router -->

<!-- router:modular -->
Un contrôleur répond à une URL et renvoie une vue. Donnez aux notes leur propre dossier, avec une vue :

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

et le contrôleur qui le restitue à `/notes` :

```python filename="src/apps/notes/notes_controller.py"
from nexy.decorators import Controller
from nexy.hooks import useViews

LAYOUT = "src/apps/layout.nexy"


@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews(LAYOUT, context={"children": useViews("src/apps/notes/notes_view.nexy")})
```

Un contrôleur ne répond qu'une fois qu'un module le répertorie. Ajoutez-le au module racine :

```python filename="src/apps/app_module.py"
from nexy.decorators import Module

from .app_controller import AboutController, AppController
from .notes.notes_controller import NotesController


@Module()
class AppModule:
    controllers = [AppController, AboutController, NotesController]
```
<!-- /router -->

Ouvrez <http://localhost:3000/notes> : vous devriez voir deux puces. La partie entre les deux lignes `---` est Python, exécutée sur le serveur ; le reste est en HTML avec des balises Jinja2 telles que `{% for %}` et `{{ note }}`.

## Changer la mise en page

<!-- router:fbr,custom -->
`src/routes/layout.nexy` est propriétaire du document HTML : `<html>`, `<head>` et `<body>`. Nexy enveloppe chaque page, là où il écrit `{{children | safe}}`.
<!-- /router -->
<!-- router:modular -->
`src/apps/layout.nexy` est propriétaire du document HTML : `<html>`, `<head>` et `<body>`. Le contrôleur y enveloppe sa vue en passant la vue comme `children`.
<!-- /router -->

Ouvrez la mise en page et remplacez la ligne `<title>Nexy App</title>` par :

```html
<title>Notes</title>
```

Enregistrer : l'onglet du navigateur indique désormais *Notes*, sur chaque page.

## Donnez de l'espace aux pages sous l'en-tête

L'en-tête de la mise en page est fixe : il reste en haut de la fenêtre, au-dessus de la page. Les pages du starter définissent leur propre espace en dessous ; les pages de l'application Notes partagent une classe pour cela, `app-page`, que chaque page du didacticiel entoure son contenu. Ajoutez-le à la fin de `src/globale.css`, la feuille de style que chaque page charge déjà :

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

Tailwind, qu'utilise le starter, supprime les bordures des champs du formulaire : ces règles les restituent, ainsi les formes des parties suivantes sont visibles.

## Ce que tu as appris

<!-- router:fbr,custom -->
- Un fichier `.nexy` sous `src/routes/` est une page ; son dossier et son nom sont son URL.
- La racine `layout.nexy` enveloppe chaque page du document HTML.
<!-- /router -->
<!-- router:modular -->
- Un contrôleur répond à une URL et affiche une vue `.nexy` avec `useViews` ; un module le répertorie.
- La mise en page est également une vue : le contrôleur lui transmet la vue de la page sous la forme `children`.
<!-- /router -->
- Un fichier `.nexy` est Python entre `---`, puis HTML avec Jinja2.
- `src/globale.css` contient les styles partagés par chaque page, tels que `app-page`.

## Prochaines étapes

- [Partie 3 : routes dynamiques et API](dynamic-routes.md)
- [Fichiers .nexy](../views/nexy/README.md) : accessoires, composants et styles
