# Tests

`nx test` exécute les tests du serveur avec pytest et le client teste avec vitest lorsque vous les demandez.

```bash
nx test                       # pytest
nx test -k create_user        # extra arguments go to pytest
nx test --client              # pytest, then vitest
nx test --no-server --client  # vitest only
```

## Qu'est-ce qui court

| Partie | Commande | Condition |
|---|---|---|
| Le serveur | `pytest` | s'exécute sur `tests/` lorsqu'il existe, sinon à la racine du projet ; ignoré avec un avertissement lorsque pytest n'est pas installé |
| Client | `npx vitest run` | uniquement avec `--client`, et uniquement lorsque `vitest.config.ts` existe ou que `vitest` apparaît dans `package.json` |

Il n’y a pas d’exécuteur de bout en bout intégré. Pilotez le serveur avec `TestClient` et ajoutez vous-même Playwright ou Cypress pour le comportement du navigateur.

## Testez le serveur

Le client de test communique avec l'application ASGI en cours de processus : aucun serveur à démarrer, aucun port à sélectionner.

```python filename="tests/test_pages.py"
from fastapi.testclient import TestClient

from nexy.app import app


def test_home_renders():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
```

`nexy.app.app` est l'application assemblée, construite lors de sa première lecture. Il lit `nexyconfig.py` à partir du répertoire de travail, alors exécutez pytest à partir de la racine du projet.

Lorsqu'un test modifie la configuration ou les itinéraires, créez une nouvelle application au lieu de réutiliser celle au niveau du module :

```python
from fastapi.testclient import TestClient
from nexy.modules.routers.app import AppServer


def test_api_hello():
    with TestClient(AppServer().run()) as client:
        response = client.get("/api/hello")
    assert response.json() == {"message": "Hello"}
```

`AppServer().run()` réassemble les routes, les middlewares, les sessions et les traductions, de sorte que chaque appel démarre à partir de l'état actuel du répertoire du projet.

## Que affirmer

Une page renvoie du HTML. Affirmez le statut, puis le contenu qui vous intéresse :

```python
def test_blog_page_renders_slug(client):
    response = client.get("/blog/post-1")
    assert "post-1" in response.text
```

Un gestionnaire d'API renvoie JSON. Un échec de validation est un `422`, et une route manquante est un `404` répondu par `notfound.nexy` lorsque ce fichier existe :

```python
def test_create_item_validates_body(client):
    assert client.post("/api/items", json={}).status_code == 422
```

Pour une action, testez directement la fonction - c'est une fonction normale - et testez le point de terminaison HTTP en lisant son chemin généré depuis la page qui l'expose :

```python
from src.actions.user import create_user


async def test_create_user_returns_name():
    assert await create_user("Ada") == {"name": "Ada"}
```

```python
def test_form_posts_to_action(client):
    html = client.get("/").text
    action = html.split('action="')[1].split('"')[0]
    response = client.post(action, data={"name": "Ada"}, follow_redirects=False)
    assert response.status_code == 303
```

Un appel avec JSON répond avec le résultat, et `422` avec les champs invalides.

> [!NOTE]
> les chemins d’action sont spécifiques au projet et générés. Ne codez jamais en dur `/_nx_<hash>` dans un test.

## Tester un composant `.nexy`

`nexy.testing.render` compile un composant, avec les composants qu'il importe, et renvoie son code HTML. Les accessoires sont des arguments de mots-clés et `children=` remplit l'emplacement :

```python filename="tests/test_button.py"
from nexy.testing import render


def test_button_shows_its_label():
    assert "Save" in render("src/components/button.nexy", label="Save")
```

Exécutez pytest depuis la racine du projet : les fichiers compilés vont dans `__nexy__/`, comme pour `nx dev`. Un composant qui lit la requête (`usePathname`, `useSession`) a besoin d'un test de page avec `TestClient` à la place.

## Tester le client

`nx test --client` attend votre propre configuration Vitest. Un test de composant minimal :

```tsx filename="src/components/counter.test.tsx"
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Counter from "./counter";

describe("Counter", () => {
  it("starts at zero", () => {
    const { getByText } = render(<Counter start={0} />);
    expect(getByText("0")).toBeTruthy();
  });
});
```

`vitest` et la bibliothèque de tests sont des dépendances du projet : `nexy new` n'installe pas de pile de tests. Ajoutez `vitest.config.ts` avec l'environnement dont vous avez besoin (jsdom ou happy-dom pour les composants).

## Intégration continue

Deux commandes suffisent pour un pipeline de projet :

```bash
nx build
nx test
```

`nx build` échoue en raison d'une erreur de compilation ; `nx test` échoue en cas d'assertion défaillante et sort non nul. `nx check` ajoute mypy et `tsc` à l'exécution.

Travailler sur Nexy lui-même utilise différentes commandes : voir [CONTRIBUTING](https://github.com/NexyPy/nexy/blob/main/CONTRIBUTING.md).

## Prochaines étapes

- [CLI](../reference/cli.md) : chaque indicateur de `nx test`
- [API](../routing/fbr/handlers/README.md) : ce que renvoie un point de terminaison
- [Déployer](../deployment/README.md) : compilez avant de tester dans CI
