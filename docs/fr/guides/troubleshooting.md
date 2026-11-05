# Dépannage

Les problèmes que les gens rencontrent en premier, avec ce que vous voyez et quoi faire. Chacun est issu d’une véritable course.

## Une page répond à 404 mais son fichier existe

Regardez le terminal qui exécute `nx dev` ou `nx start`. Lorsqu'une page ne peut pas être importée, Nexy signale l'erreur avec son fichier et sa ligne, et la route n'est pas enregistrée :

```text
nexy » error __nexy__/src/routes/index.py:18  ImportError: cannot import name 'FrameworkLogo' ...
```

Corrigez l'importation nommée ici. Les causes habituelles sont un composant dont le nom de fonction ne correspond pas à ce que vous importez (voir l'élément suivant) et une faute de frappe dans le chemin.

## Une page `.nexy` ne se compile pas : "Erreur d'analyse logique"

```text
src/components/live-panel.nexy - Logic Parse Error: invalid syntax
```

Un composant `.nexy` est importé en tant que module Python, son nom de fichier doit donc être un nom valide. Un trait d’union ne l’est pas. Nommez-le en PascalCase, `LivePanel.nexy`, et importez-le avec le même nom :

```nexy
from "@/components/LivePanel.nexy" import LivePanel
```

## Un composant restitue ses enfants sous forme de texte `<slot />`

Un composant `.nexy` place ses enfants avec `<Slot />`, avec un S majuscule. Un `<slot />` minuscule est laissé tel quel dans la page. Vue, qui possède son propre `<slot />`, n'est pas affecté.

## Un accessoire montre le nom de la variable

```nexy
<Icon path=icon />          renders: icon
<Icon path="{{ icon }}" />  renders: the value of icon
```

Un attribut sans accolades est du texte. Mettez l'expression Jinja dans l'attribut pour transmettre une valeur calculée.

## Une valeur dans `{{ ... }}` rend vide

Jinja2 cache une variable non définie. Déclarez chaque propriété que vous utilisez dans le frontmatter (`title: prop[str] = ""`) et vérifiez l'orthographe.

## Les classes utilitaires n'ont aucun effet dans une page `.nexy` (UnoCSS)

UnoCSS lit un fichier uniquement lorsque son extension est dans son pipeline de contenu. Un projet de serveur créé par `nx new` avec UnoCSS répertorie déjà `.nexy` ; un plus âgé en a besoin dans `uno.config.ts` :

```ts
content: {
  filesystem: ['src/**/*.nexy'],
  pipeline: { include: [/\.(vue|svelte|[jt]sx|mdx?|astro|html|nexy)($|\?)/] },
},
```

Tailwind trouve les fichiers `.nexy` tout seul.

## Une page `.mdx` demande des packages

```text
[nexy] MDX support requires optional packages that are not installed.
```

Installez-les dans le projet : `@mdx-js/rollup`, `remark-gfm` et `@mdx-js/react` (plus `@mdx-js/esbuild` pour `nx build`). MDX a besoin de React ou Preact dans `useFF`. Sans framework client, écrivez la page comme `.md`. Voir [Markdown et MDX](../views/nexy/markdown.md).

## `No module named 'sqlmodel'` (ou n'importe quel package) lorsqu'une commande démarre

```text
nexy » nexyconfig.py cannot be loaded: No module named 'sqlmodel'. If it is a package, install it
in this Python (...) or activate the project's virtual environment.
```

La commande s'est exécutée dans le mauvais Python. Les packages de votre projet (votre ORM, vos bibliothèques) sont dans son `.venv`, et `uvx nexy` ou un `nexy` global s'exécute dans un environnement qui lui est propre qui n'en possède aucun.

Activez l'environnement virtuel du projet, depuis le dossier du projet, puis réexécutez la commande :

```bash
.venv\Scripts\activate    # Windows; on macOS and Linux: source .venv/bin/activate
nexy dev
```

L'invite commence par `(.venv)` lorsqu'elle est active. Ou ignorez l'activation avec `uv run nexy dev`. Si le package est vraiment absent du projet, ajoutez-le avec `uv add sqlmodel`.

## `nx dev` affiche une erreur et attend

Lorsque votre application ne peut pas démarrer, `nx dev` indique pourquoi et attend la prochaine modification de fichier ; ça ne sort pas. Corrigez le fichier et enregistrez. Seul Ctrl+C l'arrête.

## Le port est occupé

`nx dev` prend le prochain port libre et l'imprime. Pour en choisir un, utilisez `--port` ou définissez `usePort` dans `nexyconfig.py`.

## Le thème clignote en blanc sur une page sombre

Le thème enregistré doit être appliqué avant la première peinture. Conservez le petit script du starter dans le `<head>` de la mise en page racine, et mettez `suppressHydrationWarning` sur `<html>` dans React.

## Toujours coincé

- Lisez la page de la fonctionnalité dans [l'index de la documentation](../README.md).
- Si la documentation et le code ne sont pas d'accord, le code est correct : veuillez ouvrir un [ticket](https://github.com/NexyPy/nexy/issues) nommant la page.
