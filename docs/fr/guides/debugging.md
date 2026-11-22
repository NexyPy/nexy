# Comment déboguer le code du serveur dans Nexy ?

Déboguez le code du serveur de `nx dev` avec `breakpoint()` dans le terminal, ou avec VS Code et `debugpy` : le serveur de développement exécute votre Python dans son propre processus, donc un débogueur qui lui est attaché s'arrête dans vos pages, gestionnaires d'API et actions.

## Comment `nx dev` exécute votre code

`nx dev` démarre uvicorn dans son propre processus, sans travailleur distinct. Lorsqu'un fichier Python ou une page `.nexy` change, il oublie les modules de votre projet et les importe à nouveau dans le même processus. Un débogueur attaché à `nx dev` reste donc attaché lors d'un rechargement, et un point d'arrêt défini dans un fichier garde sa place dans le nouveau code.

Un fichier `.nexy` est compilé dans un module Python sous `__nexy__/`, au même chemin, ce qui exécute :

<!-- router:fbr,custom -->
| Vous écrivez | Nexy court |
|---|---|
| `src/routes/about.nexy` | `__nexy__/src/routes/about.py`, fonction `About()` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/routes/api/users.py` | le fichier lui-même |
<!-- /router -->

<!-- router:modular -->
| Vous écrivez | Nexy court |
|---|---|
| `src/apps/users/user_view.nexy` | `__nexy__/src/apps/users/user_view.py` |
| `src/components/Button.nexy` | `__nexy__/src/components/Button.py` |
| `src/apps/users/user_controller.py` | le fichier lui-même |
<!-- /router -->

Le contenu d'un fichier `.nexy` (le Python entre les deux lignes `---`) devient le corps d'une fonction de ce module. `__nexy__/` est réécrit à chaque modification : ne le modifiez jamais.

## Arrêtez-vous au terminal avec `breakpoint()`

Mettez `breakpoint()` là où vous souhaitez vous arrêter, dans un fichier `.py` ou au début d'un fichier `.nexy` :

<!-- router:fbr,custom -->
```nexy filename="src/routes/about.nexy"
---
from nexy import useSearchParams

page = useSearchParams().get("page", "1")
breakpoint()
---
<p>Page {{ page }}</p>
```

Ouvrez la page. La requête attend et le terminal de `nx dev` affiche pdb, dans le module compilé :

```text
> /path/to/app/__nexy__/src/routes/about.py(21)About()
-> breakpoint()
(Pdb)
```
<!-- /router -->

<!-- router:modular -->
```python filename="src/apps/users/user_controller.py"
from nexy.decorators import Controller


@Controller("/users")
class UserController:
    async def get(self):
        page = "1"
        breakpoint()
        return {"page": page}
```

Ouvrez `/users`. La requête attend et le terminal de `nx dev` affiche pdb sur cette ligne. Au premier plan d'une vue, pdb affiche le module compilé sous `__nexy__/src/apps/`.
<!-- /router -->

Tapez `p page` pour imprimer une valeur, `n` pour la ligne suivante, `c` pour laisser la requête continuer. Supprimez la ligne lorsque vous avez terminé : la requête suivante s'arrête là encore.

## Déboguer avec VS Code

Installez `debugpy` dans l'environnement du projet :

```bash
uv add --dev debugpy
```

Ajoutez ensuite une configuration de lancement. `nexy.modules.cli` est le module derrière la commande `nx`, donc cela fonctionne de la même manière sous Linux, macOS et Windows :

```json filename=".vscode/launch.json"
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "nx dev",
      "type": "debugpy",
      "request": "launch",
      "module": "nexy.modules.cli",
      "args": ["dev"],
      "console": "integratedTerminal"
    }
  ]
}
```

Appuyez sur F5. Définissez des points d'arrêt dans vos fichiers `.py` et dans le module compilé sous `__nexy__/` pour un fichier `.nexy` : VS Code ne peut pas s'arrêter dans un fichier `.nexy`, car il n'est pas Python tant qu'il n'est pas compilé. Les numéros de ligne du module compilé suivent le sujet, donc un point d'arrêt peut se déplacer après la modification de la page ; `breakpoint()` dans le premier sujet ne le fait pas.

## Joindre depuis un autre terminal

Pour démarrer le serveur de développement vous-même et attacher un débogueur ultérieurement :

```bash
python -m debugpy --listen 127.0.0.1:5678 --wait-for-client -m nexy.modules.cli dev
```

`--wait-for-client` conserve le début jusqu'à ce qu'un débogueur se connecte ; laissez-le de côté pour commencer immédiatement. Dans VS Code, attachez avec une configuration de `"request": "attach"` et `"connect": { "host": "127.0.0.1", "port": 5678 }`.

debugpy peut avertir que "des modules gelés sont utilisés". Commencez Python par `-Xfrozen_modules=off` (`python -Xfrozen_modules=off -m debugpy ...`) si un point d'arrêt dans la bibliothèque standard est manqué ; les points d'arrêt dans votre propre code ne sont pas affectés.

## Prochaines étapes

- [Dépannage](troubleshooting.md) : les premiers problèmes rencontrés par les gens
- [Tests](testing.md) : reproduire le bug dans un test une fois que vous l'avez trouvé
- [Fichiers .nexy](../views/nexy/README.md) : frontmatter, props et modèles
