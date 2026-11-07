# Créer une application de notes avec Nexy, partie 4 : composants

La partie 4 transforme chaque note en un composant réutilisable, un fichier `.nexy` que vous importez comme un nom Python et utilisez comme une balise HTML.

**Avant de commencer :** l'application de la [partie 3](dynamic-routes.md).

## Écrire le composant

Un composant est un fichier `.nexy` en dehors des routes. Ses accessoires sont déclarés avec `prop[...]`, et l'appelant les transmet comme attributs :

```nexy filename="src/components/NoteCard.nexy"
---
id: prop[int]
text: prop[str]
---
<article class="note">
  <a href="/notes/{{ id }}">{{ text }}</a>
</article>

<style>
  .note { padding: 0.75rem 1rem; border: 1px solid #ddd; border-radius: 0.5rem; }
</style>
```

Le bloc `<style>` est envoyé avec chaque page qui utilise la carte. Sa portée n'est pas étendue : `.note` est une classe pour la page entière, donnez donc les noms des classes d'un composant que lui seul utilise.

## Utilisez-le dans la liste

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from src.notes import NOTES

notes = NOTES.items()
---
<section class="app-page">
  <h1>Notes</h1>
  {% for id, text in notes %}
  <NoteCard id="{{ id }}" text="{{ text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`@/` est l'alias d'importation de la partie 1 : il pointe vers `src/`. Le nom du fichier est le nom du composant, en PascalCase : `NoteCard.nexy` exporte `NoteCard`.

Ouvrir <http://localhost:3000/notes> : chaque note est désormais une carte.

## Ce que tu as appris

- Un fichier `.nexy` en dehors des routes est un composant ; ses `prop[...]` sont ses attributs.
- `from "@/components/x.nexy" import X` l'importe ; `<X />` le rend.
- Un bloc `<style>` n'a pas de portée : nommez les classes d'un composant après lui.

## Prochaines étapes

- [Partie 5 : stocker les notes dans SQLite](store-the-notes.md)
- [Composants](../views/nexy/components.md) : `Image`, `Link` et les assistants intégrés
