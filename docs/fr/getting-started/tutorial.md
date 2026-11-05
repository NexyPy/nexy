# Tutoriel : créer une page de notes en 10 minutes

Vous allez créer un projet, ajouter une page, ajouter un point de terminaison Python, partager des données entre eux et créer pour la production. Vous terminez avec une liste de notes servie sous forme de page et sous forme de JSON.

Nouveau sur Nexy ? Effectuez d'abord le [Démarrage rapide](quick-start.md) : cela prend trois minutes.

```diagram filename="Tout le tutoriel en une seule ligne"
uvx nexy new notes ──► edit layout ──► add page ──► add endpoint ──► share data ──► nx build ──► nx start
```

## 1. Créez le projet

```bash
uvx nexy new notes
cd notes
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

`uvx` est livré avec [uv](https://docs.astral.sh/uv/) et crée uniquement le projet. Chaque commande qui suit s'exécute dans l'environnement virtuel du projet (ou en tant que `uv run nexy dev`).

Choisissez le routeur basé sur des fichiers, un projet Web et n'importe quel framework client (ou aucun). Ouvert
<http://localhost:3000>. Les étapes longues impriment chacune une ligne avec leur durée, comme le fait `uv`.

<!-- router:modular -->
Répondez `No` à l'invite du routeur basé sur un fichier : `nx new` échafaude le routeur modulaire en `src/apps/` au lieu de `src/routes/`.
<!-- /router -->

<!-- router:custom -->
Répondez `Yes` à l'invite du routeur basé sur un fichier pour les pages, puis montez votre `APIRouter` existant dans `nexyconfig.py` : les deux routeurs coexistent.
<!-- /router -->

## 2. Modifiez la mise en page

<!-- router:fbr,custom -->
`src/routes/layout.nexy` est propriétaire du document HTML (avec le routage client React, il s'agit de `layout.tsx`). Modifiez le `<title>` :

```nexy
<title>Notes</title>
```

Enregistrer : le navigateur se recharge. Voir [Mise en page](../routing/fbr/layouts/README.md).
<!-- /router -->

<!-- router:modular -->
Le contrôleur restitue `src/apps/layout.nexy` autour de la vue et ce fichier possède le document HTML. Modifiez le `<title>` :

```nexy
<title>Notes</title>
```

Enregistrer : le navigateur se recharge. Voir [Vues d'un contrôleur](../routing/modular/README.md#views-from-a-controller).
<!-- /router -->

## 3. Ajouter une page

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Ouvrez <http://localhost:3000/notes> : vous devriez voir deux puces. Il est servi à `/notes`. La partie entre `---` est Python, le reste est Jinja2.
<!-- /router -->

<!-- router:modular -->
Un contrôleur renvoie une vue. Créer `src/apps/notes_view.nexy` :

```nexy filename="src/apps/notes_view.nexy"
---
notes = ["Buy milk", "Ship Nexy"]
---
<h1>Notes</h1>
<ul>
  {% for note in notes %}
  <li>{{ note }}</li>
  {% endfor %}
</ul>
```

Déclarez la route dans `src/apps/app_controller.py` et ajoutez le contrôleur au module :

```python filename="src/apps/app_controller.py"
@Controller("/notes")
class NotesController:
    async def get(self):
        return useViews("src/apps/layout.nexy", context={
            "children": useViews("src/apps/notes_view.nexy"),
        })
```

```python filename="src/apps/app_module.py"
from .app_controller import AppController, NotesController

controllers = [AppController, NotesController]
```

Ouvrez <http://localhost:3000/notes> : vous devriez voir deux puces. La partie entre `---` est Python, le reste est Jinja2.
<!-- /router -->

## 4. Ajouter un point de terminaison

<!-- router:fbr,custom -->
```python filename="src/routes/api/notes.py"
async def GET():
    return [{"id": 1, "text": "Buy milk"}]
```

```bash
curl http://localhost:3000/api/notes
```

Vous devriez obtenir `[{"id":1,"text":"Buy milk"}]`. Le nom de la fonction est la méthode HTTP. Les documents sur l'API interactive se trouvent à l'adresse `/docs`.
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/app_controller.py"
@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": 1, "text": "Buy milk"}]
```

Ajoutez `NotesApiController` à `controllers` dans `src/apps/app_module.py`, puis exécutez :

```bash
curl http://localhost:3000/api/notes
```

Vous devriez obtenir `[{"id":1,"text":"Buy milk"}]`. Le nom de la méthode est la méthode HTTP. Les documents sur l'API interactive se trouvent à l'adresse `/docs`.
<!-- /router -->

## 5. Partagez les données

Déplacez la liste vers un module Python et utilisez-la dans les deux fichiers :

```python filename="src/notes.py"
NOTES = ["Buy milk", "Ship Nexy"]
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/notes.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/routes/api/notes.py"
from src.notes import NOTES


async def GET():
    return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/notes_view.nexy"
---
from src.notes import NOTES as notes
---
```

```python filename="src/apps/app_controller.py"
from src.notes import NOTES


@Controller("/api/notes")
class NotesApiController:
    async def get(self):
        return [{"id": i, "text": text} for i, text in enumerate(NOTES, start=1)]
```
<!-- /router -->

## 6. Construire et servir

```bash
nx build
nx start
```

`nx build` imprime chaque phase avec sa durée. `nx start` sert la sortie compilée avec Uvicorn : aucun processus Node au moment de l'exécution.

## Où ensuite

- [Routage](../routing/README.md) : segments et groupes dynamiques
- [Actions](../guides/actions.md) : appeler Python depuis un formulaire ou depuis le client
- [Testing](../guides/testing.md) : pages de test et points de terminaison
- [Deploy](../deployment/README.md) : conteneurs et proxys inverses
