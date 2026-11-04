# Mise à niveau vers 2.2

Qu'est-ce qui change pour un projet existant lorsque vous passez de la version 2.1 à la version 2.2, et que faire à ce sujet. Le
la liste complète se trouve dans le [changelog](../../CHANGELOG.md).

```bash
uv add "nexy>=2.2"            # or: uv tool upgrade nexy
nx build
nx test
```

## Ce que vous devrez peut-être changer

| Modifier | Faites ceci |
|---|---|
| **`.mdx` est compilé par Vite uniquement.** Le compilateur Python ne le rend plus | Gardez React ou Preact dans `useFF` et installez `@mdx-js/rollup`, `remark-gfm` et `@mdx-js/react`. Une page sans composants peut être un fichier `.md` à la place |
| **`useBadge` a disparu.** La balise "Builded with Nexy" n'existe plus | Supprimez la ligne de `nexyconfig.py`. Une ligne restante est ignorée |
| **`nx check` ne compile plus `.mdx`** | Rien : Vite signale les erreurs MDX lors de la construction |

## Ce qui reste le même

- Vos itinéraires, tracés, actions et configuration.
- Les projets existants conservent leurs propres pages de démarrage. La nouvelle conception de démarrage s'applique uniquement aux projets
  créé après la mise à niveau.
- La barre d'outils de développement et `useDevTools`.

## Nouveau dans la version 2.2

- **Fichiers d'agent.** `nx new` écrit `AGENTS.md`, `CLAUDE.md` et les compétences nécessaires pour coder les agents. Pour un
  projet que vous avez déjà, exécutez `nx skills`. Il n'écrase jamais un fichier que vous avez écrit. Voir
  [Agents de codage](../guides/ai-agents.md).
- **Un serveur de développement qui continue de fonctionner.** Lorsque votre application ne peut pas démarrer, `nx dev` indique pourquoi et
  attend le prochain changement au lieu de quitter.
- **Un nouveau starter** pour chaque framework dans Tailwind ou UnoCSS, avec les mêmes pages et composants.
- **UnoCSS lit les `.nexy` fichiers** dans un projet serveur. Si vous utilisez UnoCSS avec des pages `.nexy`, ajoutez le
  Bloc `content` affiché dans [Dépannage](../guides/troubleshooting.md).

## Documentation corrigée

Trois pages disaient quelque chose que le code ne fait pas. Si vous les avez suivis, vérifiez vos fichiers :

- Un composant `.nexy` place ses enfants avec `<Slot />` (S majuscule), et non avec `<slot />`.
- Un fichier de composant `.nexy` est nommé en PascalCase : il est importé en tant que module Python, donc un trait d'union
  ne compile pas.
- Pour `.mdx`, le framework est Preact lorsque le fichier importe `preact`, React sinon.

## Où ensuite

- [Index de la documentation](../README.md) : la page de ce que vous construisez
- [Dépannage](../guides/troubleshooting.md) : les problèmes rencontrés en premier
- [Config](../reference/config.md) : chaque champ `use*` et sa valeur par défaut