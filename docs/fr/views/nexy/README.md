# .fichiers suivants

Un fichier `.nexy` est un composant : Python en haut, HTML au milieu, CSS en bas.

**Avant de commencer :** un projet créé par le [Démarrage rapide](../../getting-started/quick-start.md).
Un fichier `.nexy` ne nécessite aucune configuration de construction : `nx dev` le compile lors de la sauvegarde.

```nexy filename="src/routes/blog/[slug].nexy"
---
from nexy import usePathname

slug: prop[str] = "untitled"
pathname = usePathname()
---
<article class="post">
  <h1>{{ slug }}</h1>
  <p>You are on {{ pathname }}</p>
</article>

<style>
  .post { max-width: 60ch; }
</style>
```

## Première question

Tout entre les deux lignes `---` est Python. Les importations sont résolues lorsque le composant est
compilé; le reste s'exécute pour chaque requête, afin qu'il puisse lire l'état de la requête.

| Quoi | Exemple |
|---|---|
| Importer un module | `import json`, `from datetime import datetime` |
| Importer un composant | `from "@/components/card.nexy" import Card` |
| Déclarer une propriété | `title: prop[str] = "Default"` |
| Calculer une valeur | `year = datetime.now().year` |
| Lire la demande | `pathname = usePathname()` |
| Cacher la page (ISR) | `revalidate = 60` |

## Propriétés

Les propriétés sont l'API du composant. `prop[type]` déclare le type, `= value` donne une valeur par défaut. Un
la propriété sans valeur par défaut doit être transmise par le parent.

Les importations commençant par un alias sont résolues via `useAliases`. La configuration `nx new` écrit des cartes
`@` à `src`, ce qui fait que `@/components/card.nexy` signifie `src/components/card.nexy`.

## Modèle

Sous le thème principal se trouve du HTML avec Jinja2. Les variables du frontmatter et les propriétés sont dans
portée.

```html
{% for item in items %}
  <li>{{ item.name }}</li>
{% endfor %}

{% if user %}
  <p>Welcome, {{ user.name }}</p>
{% endif %}
```

L'échappement automatique est **désactivé** : les modèles sont le propre HTML du projet, donc `{{ value }}` est inséré comme
écrit. Échappez-vous aux valeurs non fiables avec `{{ value | e }}`. `| safe` ne change donc rien.

> [!REMARQUE]
> envelopper du JavaScript qui contient `{{` ou `{%` dans `{% raw %}...{% endraw %}`.
> Les frameworks tels que Vue et Svelte utilisent les mêmes accolades.

## Composants

Tout appelable importé dont le nom commence par une lettre majuscule peut être utilisé comme balise. Le compilateur
le réécrit dans un appel Jinja : les attributs deviennent des arguments de mots-clés.

```nexy filename="src/routes/index.nexy"
---
from "@/components/card.nexy" import Card
from nexy import Audio
---
<Card title="Hello">
  <p>Child content</p>
</Card>

<Audio src="/theme.mp3" controls=True />
```

La dernière ligne est exactement `{{ Audio("/theme.mp3", controls=True) }}`. Les deux syntaxes sont valables pour le
assistants intégrés `Image`, `Link`, `Audio` et `Video` - voir
[composants](components.md#two-syntaxes-one-function).

Les enfants sont rendus via `<Slot />` (S majuscule) à l'intérieur du composant enfant et via `{{ children }}`
à l'intérieur d'une mise en page.

Passez une valeur calculée avec Jinja à l'intérieur de l'attribut : `<Icon path="{{ icon }}" size="{{ size }}" />`.
Un nom simple tel que `path=icon` est le texte `icon`, pas la variable. Pour donner un CSS à un composant
classe, déclarez un accessoire `class_name` : `class` est un mot-clé Python.

> [!REMARQUE]
> une balise d'assistance se ferme toujours automatiquement. Passer du contenu à `Link` passe par son
> `children` argument (`<Link href="/about" children="About" />`), pas via le contenu de l'élément.

## Styles

Les blocs `<style>` sont émis avec la page qui les déclare. Ils n'ont pas de portée : un nom de classe
utilisé dans deux composants est une classe. Préfixez ou espacez vos classes.

## Des règles qui font gagner du temps

- Un composant par fichier. Le nom du fichier est le nom du composant, en PascalCase (`CopyChip.nexy`). Un
  Le composant `.nexy` est importé en tant que module Python : un trait d'union dans le nom (`copy-chip.nexy`) n'a pas d'effet.
  compiler.
- Déclarez les accessoires avant de les utiliser : une variable non déclarée s'affiche sous la forme d'une chaîne vide, car
  L'indéfini de Jinja2 est silencieux ici.
- Gardez les effets secondaires dans les fonctions - le frontmatter s'exécute à nouveau à chaque requête.

## Prochaines étapes

- [Markdown et MDX](markdown.md) : pages de contenu
- [ISR](../../rendering/isr.md) : cache une page par chemin
- [CSR](../../rendering/csr.md) : rendu côté client