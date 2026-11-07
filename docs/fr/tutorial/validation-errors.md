# Créer une application de notes avec Nexy, partie 7 : afficher les erreurs de validation

La partie 7 refuse une note vide ou trop longue, et montre pourquoi au dessus du formulaire, sur la même page, toujours sans JavaScript.

**Avant de commencer :** l'application de la [partie 6](create-a-note.md).

## Deux types d'erreurs

Les indices de type d'une Action refusent déjà une mauvaise forme : un formulaire sans champ `text` répond à `422` avant l'exécution de `create_note`. Une règle concernant la valeur elle-même, telle que "non vide", vous appartient d'écrire dans l'action.

## Vérifiez la note dans l'action

Un échec renvoie le visiteur vers la liste avec la raison dans l'URL ; un succès revient à la liste sans lui :

```python filename="src/actions/notes.py"
from urllib.parse import urlencode

from nexy.decorators import Action
from nexy.http import RedirectResponse
from src.notes import add_note

MAX_LENGTH = 200


def back(error: str = "") -> RedirectResponse:
    query = f"?{urlencode({'error': error})}" if error else ""
    return RedirectResponse(f"/notes{query}", status_code=303)


@Action
async def create_note(text: str) -> RedirectResponse:
    text = text.strip()
    if not text:
        return back("A note cannot be blank.")
    if len(text) > MAX_LENGTH:
        return back(f"A note is at most {MAX_LENGTH} characters.")
    add_note(text)
    return back()
```

`303` indique au navigateur de charger la page suivante avec un `GET`, afin qu'une actualisation ne publie pas le formulaire une seconde fois.

## Afficher la raison au-dessus du formulaire

`useSearchParams()` lit la chaîne de requête de la requête en cours :

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes/index.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes/notes_view.nexy"
---
from "@/components/NoteCard.nexy" import NoteCard
from nexy import useSearchParams
from src.notes import all_notes

notes = all_notes()
error = useSearchParams().get("error", "")
---
<section class="app-page">
  <h1>Notes</h1>

  {% if error %}
  <p class="note-error" role="alert">{{ error | e }}</p>
  {% endif %}

  <form method="post" action="{{ __actions_path['create_note'] }}">
    <input name="text" placeholder="A new note" maxlength="200" required>
    <button type="submit">Add</button>
  </form>

  {% for note in notes %}
  <NoteCard id="{{ note.id }}" text="{{ note.text }}" />
  {% endfor %}
</section>
```
<!-- /router -->

`| e` échappe au message : la chaîne de requête provient du visiteur, elle n'est donc jamais écrite dans la page au format HTML. `role="alert"` fait qu'un lecteur d'écran l'annonce.

`required` et `maxlength` permettent au navigateur d'arrêter la plupart des erreurs avant qu'elles ne le quittent. L'Action vérifie à nouveau : une demande ne doit pas nécessairement provenir de votre formulaire.

Ajoutez une note de trois espaces : la liste revient avec *Une note ne peut pas être vide.* au-dessus du formulaire.

## Ce que tu as appris

- Les indices de type refusent une mauvaise forme avec `422` ; les règles sur la valeur vont dans l’action.
- Une action peut répondre par un `RedirectResponse` ; `303` après un formulaire évite un deuxième post.
- `useSearchParams()` lit la chaîne de requête et `| e` échappe à ce que le visiteur a envoyé.

## Prochaines étapes

- [Partie 8 : modifier et supprimer une note](edit-and-delete.md)
- [Exceptions et erreurs](../reference/exceptions.md) : à chaque statut auquel une action et une page peuvent répondre
