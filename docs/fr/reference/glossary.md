# Glossaire

Les mots utilisés dans ces documents, une ligne chacun, par ordre alphabétique. Un terme qui nécessite plus qu'une ligne a une page : suivez le lien. Pour savoir comment les notions s'articulent, lisez [Concepts de base](../getting-started/core-concepts.md).

## Conditions

| Durée | En une seule ligne |
|---|---|
| Action | une fonction Python marquée `@Action`, servant de `POST` et appelable depuis le client ([actions](../guides/actions.md)) |
| ASGI | l'interface Uvicorn parle, implémentée par FastAPI et Starlette |
| Mode client | `useCSR = True` : les fichiers de framework sont les itinéraires et les navigations du navigateur ([modes](../routing/fbr/modes.md)) |
| Composant | un bloc de construction d'interface utilisateur réutilisable utilisé pour composer une vue ([vues](../views/README.md)) |
| RSE | rendu côté client : le navigateur restitue les pages après le premier document ([CSR](../rendering/csr.md)) |
| Dépendance | une fonction FastAPI s'exécute avant un gestionnaire, par route ou par dossier ([dépendances](../routing/fbr/dependencies/README.md)) |
| Coque du document | les `<html>`, `<head>` et `<body>` autour d'une page, appartenant à la mise en page la plus proche ou à Nexy ([mises en page](../routing/fbr/layouts/README.md)) |
| Point de terminaison | la combinaison unique d'une URL et d'une méthode HTTP ([vues](../views/README.md)) |
| FBR | Routage basé sur fichier : un fichier sous `src/routes/` est une route ([routage](../routing/fbr/README.md)) |
| Frontière | le bloc Python entre les deux lignes `---` d'un fichier `.nexy` ou `.md` ([fichiers .nexy](../views/nexy/README.md)) |
| Garde | une dépendance qui refuse une demande en levant `HTTPException` ([gardes](../routing/modular/guards-and-metadata.md)) |
| Gestionnaire | une fonction Python qui gère une requête HTTP pour une méthode spécifique ([vues](../views/README.md)) |
| HMR | remplacement de module à chaud : le serveur de développement échange les modules qui ont changé, sans rechargement complet ([frontend](../guides/frontend.md)) |
| Hydratation | le navigateur attachant un framework au HTML que le serveur a déjà envoyé ([îlots](../rendering/islands.md)) |
| Île | un composant client monté dans une page rendue par le serveur ([îlots](../rendering/islands.md)) |
| ISR | régénération statique incrémentielle : une page mise en cache par chemin, rafraîchie en arrière-plan ([ISR](../rendering/isr.md)) |
| Disposition | un fichier `layout.*` qui enveloppe les pages sous son dossier ([mises en page](../routing/fbr/layouts/README.md)) |
| Routeur modulaire | itinéraires déclarés avec `@Module` et `@Controller` sous `src/apps/` ([modulaire](../routing/modular/README.md)) |
| Pages | une ressource adressable par URL définie par un fichier sous `src/routes/` ([vues](../views/README.md)) |
| Prélecture | charger la page derrière un lien avant que le lecteur clique dessus ([liens](../routing/fbr/navigation/linking-and-navigating.md)) |
| Props | les valeurs qu'un parent transmet à un composant ([fichiers .nexy](../views/nexy/README.md)) |
| Revalider | le nombre de secondes après lesquelles une page ISR est reconstruite en arrière-plan ([ISR](../rendering/isr.md)) |
| Itinéraire | un modèle d'URL, produit par le chemin d'un fichier de route ([routage](../routing/README.md)) |
| Groupe de routage | un dossier entre parenthèses qui regroupe les routes sans ajouter de segment ([routes dynamiques](../routing/fbr/pages/dynamic-routes.md)) |
| Gestionnaire d'itinéraire | la fonction `GET`, `POST`, … d'un fichier de route `.py` ([gestionnaires](../routing/fbr/handlers/README.md)) |
| Mode serveur | `useCSR = False`, la valeur par défaut : le serveur restitue les pages `.nexy` et `.md` ([modes](../routing/fbr/modes.md)) |
| Compétence | un dossier avec un `SKILL.md` qui enseigne à un agent de codage une partie de Nexy ([coding agents](../guides/ai-agents.md)) |
| SSG | génération de sites statiques ; **pas un mode Nexy** : le HTML construit en amont est toujours relu par le serveur ([rendu](../rendering/README.md)) |
| RSS | rendu côté serveur : le serveur restitue chaque page pour sa demande, et c'est la valeur par défaut ([SSR](../rendering/ssr.md)) |
| Voir | le processus de production du corps de réponse pour une page ([vues](../views/README.md)) |

## Fichiers et dossiers

| Nom | En une seule ligne |
|---|---|
| `__nexy__/` | sortie générée : les pages compilées, l'entrée client et l'action client ; jamais édité, jamais engagé |
| `nexyconfig.py` | la configuration du projet, une classe de `use*` champs ([configuration](config.md)) |
| `public/` | fichiers servis à la racine, tels que `public/logo.svg` → `/logo.svg` ([conventions de fichiers](file-conventions.md)) |
| `src/apps/` | contrôleurs et modules du routeur modulaire ([modulaire](../routing/modular/README.md)) |
| `src/components/` | composants importés par pages ; jamais de routes ([conventions de fichiers](file-conventions.md)) |
| `src/routes/` | les routes de l'application ([conventions de fichiers](file-conventions.md)) |

## Prochaines étapes

- [Concepts de base](../getting-started/core-concepts.md) : le modèle auquel ces mots appartiennent
- [Index de la documentation](../README.md) : la page correspondant à la tâche à accomplir
- [Conventions de fichiers](file-conventions.md) : les noms réservés derrière ces définitions
- [Pour les agents IA](../guides/ai-agents.md) : les mêmes invariants, écrits pour un agent
