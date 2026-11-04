# SSR (rendu du serveur)

## Définition

SSR est la valeur par défaut : le serveur restitue la page au format HTML pour chaque requête. Rien ne le permet, et
aucun indicateur ne le désactive - un projet en mode serveur s'affiche à chaque requête, sauf si une page le déclare
`revalidate`.

## Comment ça marche

| Fichier de route | Qu'est-ce qui produit le code HTML | Quand |
|---|---|---|
| `.nexy` | le module Python compilé, via Jinja2 | chaque requête |
| `.md` | `cmarkgfm`, puis la mise en page la plus proche | à chaque requête |
| `.mdx`, `.tsx`, `.vue`, `.svelte` | le framework, rendu dans Node | à la construction lorsque la route n'a pas de layout, sinon dans le navigateur |
| `.py` | rien : il renvoie du JSON ou un `Response` | - |

Une route de composants est le seul cas qui nécessite une deuxième phrase. En production, un parcours de composants
**sans** une mise en page est servie avec le HTML produit lors de la construction, et le composant l'hydrate. Avec
une mise en page, ou en développement, le conteneur est vide et le composant s'affiche dans le navigateur - le
la page est alors une coquille qui se remplit toute seule.

## Cycle de vie du rendu

1. La requête atteint le routeur basé sur des fichiers. Le chemin correspond et les segments dynamiques sont convertis en
   les types déclarés par le composant.
2. Le composant s'exécute. Celui qui attend sur Node - un document client - s'exécute dans un pool de threads, donc il
   ne bloque pas la boucle d'événements.
3. Le corps est diffusé sous la forme `text/html`. Un composant qui génère des morceaux les diffuse au fur et à mesure qu'il les crée.
   eux.
4. Le navigateur reçoit du HTML. Les îles s'hydratent conformément à leur [directive](islands.md).

Une erreur générée lors du rendu est transformée en page par `errors.nexy` lorsque le projet en possède une : voir
[pages d'erreur](../routing/fbr/errors/README.md).

## Quand utiliser

- La page montre quelque chose que le lecteur possède : une session, un compte, un panier.
- Les données doivent être récentes à chaque chargement.
- Le contenu doit être au format HTML pour les robots d'exploration qui n'exécutent pas JavaScript.
- La page est peu coûteuse à afficher : une requête, un modèle.

## Configuration

Aucun. Deux issues, et elles n’ont pas le même grain :

| Quitter la SSR pour | Faites ceci | Grain |
|---|---|---|
| une page, avec un cache | `revalidate = 60` dans son frontmatter → [ISR](isr.md) | page |
| l'ensemble du projet, acheminé par le client | `useCSR = True` dans `nexyconfig.py` → [CSR](csr.md) | projet |

## Exemple

```nexy filename="src/routes/blog/[slug].nexy"
---
slug: prop[str] = "untitled"
---
<h1>{{ slug }}</h1>
```

`GET /blog/hello` exécute ce modèle une fois, avec `slug` défini sur `hello`. Une deuxième requête l'exécute
encore une fois : rien n'est gardé entre les deux. La chaîne de requête n'est pas un accessoire - lisez-la avec les hooks
[navigation](../routing/fbr/navigation/hooks.md).

## Contraintes

- **Un rendu par demande.** Deux visiteurs dans la même seconde paient chacun pour le rendu et pour le
  requêtes derrière cela.
- **Pas de cache.** Il n'y a pas de cache de réponses partagé à réchauffer : [ISR](isr.md) en ajoute un par URL.
- **Le streaming n'aide qu'un composant qui rapporte.** Une requête lente en haut de la page retarde encore
  le premier octet.
- **Pas de sortie statique.** En mode serveur, rien n'est figé à la construction : il n'y a pas de mode SSG, et aucun
  commande d'exportation. Voir [Rendu](README.md).
- **La fuite automatique est désactivée** dans les modèles `.nexy`. Échappez aux valeurs non fiables avec `| e`.

## Prochaines étapes

- [ISR](isr.md) : cache cette page par URL
- [Îles](islands.md) : conserver SSR et rendre un widget interactif
- [CSR](csr.md) : navigation manuelle vers le navigateur
- [Performances](../deployment/performance.md)