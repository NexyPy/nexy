# Glossaire

Les mots utilisés dans ces documents, une ligne chacun, par ordre alphabétique. Un terme qui nécessite plus qu'une ligne
a une page : suivez le lien. Pour savoir comment les notions s'articulent, lisez
[Concepts de base](../getting-started/core-concepts.md).

## Conditions

| Terme | Sur une seule ligne |
|---|---|
| Action | une fonction Python marquée `@Action`, servie de `POST` et appelable depuis le client ([actions](../guides/actions.md)) |
| ASGI | l'interface parlée par Uvicorn, implémentée par FastAPI et Starlette |
| Mode client | `useCSR = True` : les fichiers du framework sont les routes et le navigateur navigue ([modes](../routing/fbr/modes.md)) |
| Composant | un bloc de construction d'interface utilisateur réutilisable utilisé pour composer une vue ([views](../views/README.md)) |
| CSR | rendu côté client : le navigateur restitue les pages après le premier document ([CSR](../rendering/csr.md)) |
| Dépendance | une fonction FastAPI s'exécute avant un gestionnaire, par route ou par dossier ([dependencies](../routing/fbr/dependencies/README.md)) |
| Coquille de document | les `<html>`, `<head>` et `<body>` autour d'une page, appartenant à la mise en page la plus proche ou à Nexy ([layouts](../routing/fbr/layouts/README.md)) |
| Endpoint | la combinaison unique d'une URL et d'une méthode HTTP ([views](../views/README.md)) |
| Routage basé sur fichier FBR | : un fichier sous `src/routes/` est une route ([routing](../routing/fbr/README.md)) |
| Frontmatter | le bloc Python entre les deux `---` lignes d'un fichier `.nexy` ou `.md` ([fichiers .nexy](../views/nexy/README.md)) |
| Garder | une dépendance qui refuse une demande en levant `HTTPException` ([guards](../routing/modular/guards-and-metadata.md)) |
| Handler | une fonction Python qui gère une requête HTTP pour une méthode spécifique ([views](../views/README.md)) |
| HMR | remplacement de module à chaud : le serveur de développement échange les modules qui ont changé, sans rechargement complet ([frontend](../guides/frontend.md)) |
| Hydratation | le navigateur attachant un framework au HTML que le serveur a déjà envoyé ([îles](../rendering/islands.md)) |
| Island | un composant client monté dans une page rendue par le serveur ([islands](../rendering/islands.md)) |
| ISR | régénération statique incrémentielle : une page mise en cache par chemin, actualisée en arrière-plan ([ISR](../rendering/isr.md)) |
| Layout | un fichier `layout.*` qui enveloppe les pages sous son dossier ([layouts](../routing/fbr/layouts/README.md)) |
| Routeur modulaire | routes déclarées avec `@Module` et `@Controller` sous `src/apps/` ([modular](../routing/modular/README.md)) |
| Page | une ressource adressable par URL définie par un fichier sous `src/routes/` ([views](../views/README.md)) |
| Prefetch | chargeant la page derrière un lien avant que le lecteur ne clique dessus ([linking](../routing/fbr/navigation/linking-and-navigating.md)) |
| Props | les valeurs qu'un parent transmet à un composant ([fichiers .nexy](../views/nexy/README.md)) |
| Revalider | le nombre de secondes après lequel une page ISR est reconstruite en arrière-plan ([ISR](../rendering/isr.md)) |
| Route | un modèle d'URL, produit par le chemin d'un fichier de route ([routing](../routing/README.md)) |
| Groupe de routes | un dossier entre parenthèses qui regroupe les routes sans ajouter de segment ([routes dynamiques](../routing/fbr/pages/dynamic-routes.md)) |
| Gestionnaire de route | la fonction `GET`, `POST`, … d'un fichier de route `.py` ([handlers](../routing/fbr/handlers/README.md)) |
| Mode serveur | `useCSR = False`, par défaut : le serveur restitue les pages `.nexy` et `.md` ([modes](../routing/fbr/modes.md)) |
| Compétence | un dossier avec un `SKILL.md` qui enseigne à un agent de codage une partie de Nexy ([agents de codage](../guides/ai-agents.md)) |
| SSG | génération de sites statiques ; **pas un mode Nexy** : le HTML construit en amont est toujours relu par le serveur ([rendu](../rendering/README.md)) |
| SSR | rendu côté serveur : le serveur restitue chaque page pour sa demande, et c'est la valeur par défaut ([SSR](../rendering/ssr.md)) |
| Afficher | le processus de production du corps de réponse d'une page ([views](../views/README.md)) |

## Fichiers et dossiers

| Nom | Sur une seule ligne |
|---|---|
| `__nexy__/` | sortie générée : les pages compilées, l'entrée client et l'action client ; jamais édité, jamais commis |
| `nexyconfig.py` | la configuration du projet, une classe de `use*` champs ([config](config.md)) |
| `public/` | fichiers servis à la racine, tels que `public/logo.svg` → `/logo.svg` ([conventions de fichiers](file-conventions.md)) |
| `src/apps/` | contrôleurs et modules du routeur modulaire ([modular](../routing/modular/README.md)) |
| `src/components/` | composants importés par pages ; jamais de routes ([conventions de fichiers](file-conventions.md)) |
| `src/routes/` | les routes de l'application ([conventions des fichiers](file-conventions.md)) |

## Étapes suivantes

- [Concepts de base](../getting-started/core-concepts.md) : le modèle auquel ces mots appartiennent
- [Index de la documentation](../README.md) : la page de la tâche à accomplir
- [Conventions des fichiers](file-conventions.md) : les noms réservés derrière ces définitions
- [Pour les agents IA](../guides/ai-agents.md) : les mêmes invariants, écrits pour un agent