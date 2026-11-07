# Composants

Nexy exporte un petit ensemble d'assistants qui renvoient des chaînes HTML. Chacun est utilisé de deux manières dans un modèle `.nexy` : comme appel Jinja ou comme balise de style HTML.

## Deux syntaxes, une fonction

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from nexy import Audio
---
{{ Audio("/theme.mp3", controls=True) }}

<Audio src="/theme.mp3" controls=True />
```
<!-- /router -->

Les deux lignes produisent le même balisage :

```html
<audio preload="metadata" controls><source src="/theme.mp3" type="audio/mp3" /></audio>
```

Le compilateur réécrit `<Audio ... />` en `{{ Audio(...) }}`, donc la forme de balise n'est pas une seconde API : les attributs sont les arguments de mot-clé de la fonction.

## Règles du formulaire de balise

| Dans la balise | Devient |
|---|---|
| `<Audio src="/a.mp3" />` | `Audio(src="/a.mp3")` |
| `controls=True` | `controls=True`, un vrai booléen |
| `width=640` | `width=640`, un certain nombre |
| `src="{{ url }}"` | `src=(url)`, évalué dans Jinja |
| tout autre `value` | `"value"`, une chaîne |

- Le tag doit commencer par une lettre majuscule et être importé dans le frontmatter ; sinon le compilateur génère `Missing Import: <Name> used but not declared.`
- La forme de l'étiquette est **à fermeture automatique**. `<Audio src="/a.mp3" />` et `{{ Audio("/a.mp3") }}` sont équivalents ; l'écriture d'enfants à l'intérieur d'une balise d'assistance n'est pas prise en charge.
- Un simple attribut HTML n'est pas ici un booléen : `controls` devient `controls=""`, ce qui est faux. Écrivez `controls=True`.

> [!NOTE]
> `class_name` est le mot-clé documenté pour les classes CSS. Les arguments de mots-clés supplémentaires deviennent des attributs HTML, donc `class="nav"` atteint également la sortie.

## Images

```nexy
---
from nexy import Image
---
{{ Image("/logo.png", alt="Logo", width=128, height=32) }}

<Image src="/logo.png" alt="Logo" width=128 height=32 />
```

`Image(src, alt="", width=None, height=None, loading="lazy", class_name=None, **attrs)` restitue un `<img>` avec un chargement paresseux par défaut.

## Lien

```nexy
---
from nexy import Link
---
{{ Link("/about", "About", class_name="nav-link") }}
```

`Link(href, children="", class_name=None, prefetch=True, **attrs)` restitue un `<a data-nexy-link>` géré par le routeur client. Avec `prefetch=True`, survoler ou toucher le lien réchauffe la cible via `window.__nexy_prefetch`.

> [!NOTE]
> la forme de balise prend l'étiquette comme `children`, et non comme contenu d'élément : `<Link href="/about" children="About" />`. Pour placer un balisage dans un lien, utilisez le formulaire d'appel avec `children=` ou un composant `.nexy` qui restitue un `<Slot />`.

## Audio et vidéo

```nexy
---
from nexy import Audio, Video
---
{{ Audio("/theme.mp3", controls=True) }}
{{ Video("/demo.mp4", width=640, height=360, muted=True, sources=["/demo.webm", "/demo.mp4"]) }}

<Audio src="/theme.mp3" controls=True />
<Video src="/demo.mp4" width=640 height=360 muted=True />
```

`Audio(src, controls=True, autoplay=False, loop=False, muted=False, preload="metadata", class_name=None, sources=None, **attrs)` et `Video(src, width=None, height=None, ...)` rendent les lecteurs natifs. `sources` ajoute des balises `<source>` avec le type MIME dérivé de chaque extension.

## Un composant que vous écrivez vous-même

Un composant `.nexy` réutilisable est un fichier sous `src/components/` : Python props en haut, HTML en dessous. Il est importé comme n'importe quel autre module Python.

```nexy filename="src/components/Card.nexy"
---
title: prop[str]
tone: prop[str] = "neutral"
---
<article class="card card-{{ tone }}">
  <h2>{{ title }}</h2>
  <Slot />
</article>
```

<!-- router:fbr,custom -->
```nexy filename="src/routes/index.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest notes" tone="warm">
  <p>Everything published this week.</p>
</Card>
```
<!-- /router -->

<!-- router:modular -->
```nexy filename="src/apps/home_view.nexy"
---
from "@/components/Card.nexy" import Card
---
<Card title="Latest notes" tone="warm">
  <p>Everything published this week.</p>
</Card>
```
<!-- /router -->

`title` n'a pas de valeur par défaut, la page doit donc la transmettre ; `tone` revient à `"neutral"`. Le balisage entre les balises arrive à l’intérieur de `<Slot />` (S majuscule). Voir [fichiers .nexy](README.md#components) pour les accessoires, les emplacements et les règles du formulaire de balise.

## Importer un composant client

A partir d'un fichier `.nexy`, importez un composant du framework par chemin ; le compilateur le monte sur le client et transmet les attributs comme accessoires :

```nexy
---
from "@/components/Counter.tsx" import Counter
---
<Counter start="0" />
```

`Import(path, framework, symbol)` fait de même dans Python :

```python
from nexy import Import

counter = Import("@/components/Counter.tsx", "react", "Counter")
html = counter(start=0)
```

La même syntaxe d'importation résout les `.json`, `.css` et les fichiers image en leurs URL.

## Modèle et Vite

`Template().render(path, context)` restitue un fichier modèle (Jinja2 ou Markdown rendu au format HTML pour les routes `.md`). `Template().invalidate(path)` le supprime du cache.

`Vite()` renvoie les balises client pour le mode actuel : le script HMR en développement, le bundle client construit en production. Nexy l'appelle pour chaque page ; vous en avez rarement besoin directement.

## Pas encore mis en œuvre

`Form` et `Script` sont des espaces réservés exportés sans comportement. Ne comptez pas sur eux.

## Prochaines étapes

- [Fichiers .nexy](README.md) : où ces assistants sont utilisés
- [React](../react/differences.md) : importation de composants `.tsx`
- [Frontend](../../guides/frontend.md) : comment les composants clients sont regroupés
