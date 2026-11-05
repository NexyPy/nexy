# Actions et navigation

L'interaction dans Nexy est gérée via un système unifié d'**Actions** et de **Navigation**, garantissant que le frontend et le backend restent synchronisés sans code de colle API manuel.

## Le contrat d'action

Une **Action** est une fonction côté serveur qui gère une mutation (par exemple, la mise à jour d'une base de données). 

1.  **Entrée typée** : les actions sont définies dans Python avec des indications de type. Nexy génère un client TypeScript correspondant, vous obtenez donc la saisie semi-automatique et la validation dans votre IDE.
2.  **Exécution atomique** : une action est une seule requête `POST`.
3.  **Gestion des résultats** : les actions renvoient un résultat typé que le client peut utiliser pour mettre à jour l'interface utilisateur.

## Navigation côté client

La navigation dans Nexy est « intelligente ». Au lieu d'un rechargement complet du navigateur, Nexy échange le contenu de la page actuelle tout en gardant les mises en page actives montées.

- **Le composant `Link`** : utilisez le composant `Link` spécifique au framework pour effectuer des transitions côté client.
- **Navigation programmatique** : utilisez la fonction `navigate()` de `@nexy/client` pour changer de page en réponse à la logique (par exemple, après une connexion réussie).

## Coordination : Action → Navigation

Le modèle le plus courant consiste à effectuer une action, puis à diriger l'utilisateur vers une nouvelle page.

**Le flux de revalidation :**
1.  Le client appelle une action.
2.  L'action s'exécute sur le serveur et appelle `revalidate("/path")`.
3.  Le serveur renvoie le résultat accompagné d'un signal pour actualiser le chemin spécifié.
4.  Le client met à jour le contenu de la page pour refléter le nouvel état.

## Mise en œuvre du cadre

L'API pour appeler des actions et naviguer varie selon le framework. Consultez le guide des **Différences** pour la technologie que vous avez choisie :

- [React Différences](../react/differences.md)
- [Vue Différences](../vue/differences.md)
- [Svelte Différences](../svelte/differences.md)
- [Solid Différences](../solid/differences.md)
- [Preact Différences](../preact/differences.md)
