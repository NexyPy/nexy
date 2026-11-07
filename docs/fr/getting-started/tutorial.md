# Tutoriel Nexy : créer une application de notes étape par étape

Le didacticiel Nexy crée une application Notes à partir d'un dossier vide vers une version de production, une partie à la fois, et chaque partie se termine par une application qui s'exécute.

Nouveau sur Nexy ? Le [Démarrage rapide](quick-start.md) montre qu'il fonctionne en trois minutes ; revenez ici pour savoir comment cela fonctionne.

## Comment fonctionne le tutoriel

- **Une application qui grandit.** Chaque partie ajoute une fonctionnalité à l'application de notes de la partie précédente.
- **Votre routeur.** Les pièces suivent le routeur choisi en haut du menu : basé sur fichier, modulaire ou personnalisé. Basculez-le là, et les fichiers de chaque partie changent avec lui.
- **Code qui s'exécute.** Chaque fichier portant un nom au-dessus est un fichier entier, et la suite de tests relit les parties dans l'ordre sur un nouveau projet : ce que vous copiez est ce qui s'exécute.
- **Arrêtez-vous n'importe où.** Chaque partie dure 10 à 20 minutes et se termine par ce qu'il faut vérifier dans le navigateur.

## Les pièces

### Unité 1 : les bases

| Partie | Ce que tu ajoutes | Ce que tu apprends |
|---|---|---|
| [1. Créez le projet](../tutorial/create-the-project.md) | un projet qui se déroule | `nexy new`, `nexy dev` |
| [2. Pages et mises en page](../tutorial/pages-and-layouts.md) | la page des notes | les pages, les vues, la mise en page |
| [3. Des routes dynamiques et une API](../tutorial/dynamic-routes.md) | `/notes/1` et `/api/notes` | Segments d'URL, routes JSON, `notFound` |
| [4. Composants](../tutorial/components.md) | une carte par note | `.nexy` composants et leurs accessoires |

### Unité 2 : données

| Partie | Ce que tu ajoutes | Ce que tu apprends |
|---|---|---|
| [5. Stockez les notes dans SQLite](../tutorial/store-the-notes.md) | un modèle, une migration, une graine | SQLModel, `nx migrate` |
| [6. Créez une note à partir d'un formulaire](../tutorial/create-a-note.md) | un formulaire qui enregistre une note | Actions, formes sans JavaScript |
| [7. Afficher les erreurs de validation](../tutorial/validation-errors.md) | un message au dessus du formulaire | règles dans une action, `303`, `useSearchParams` |
| [8. Modifier et supprimer une note](../tutorial/edit-and-delete.md) | les formes d'une note | plusieurs Actions par page, champs cachés |
| [9. Paginez les notes](../tutorial/paginate-the-notes.md) | cinq notes par page | `offset` et `limit`, liens entre pages |

### Unité 3 : utilisateurs

| Partie | Ce que tu ajoutes | Ce que tu apprends |
|---|---|---|
| [10. Créez un compte et connectez-vous](../tutorial/accounts.md) | s'inscrire, se connecter, se déconnecter | sessions, hachage de mot de passe |
| [11. Donnez à chaque utilisateur ses propres notes](../tutorial/own-notes.md) | notes appartenant à un utilisateur | clés étrangères, `redirect`, `401` |
| [12. Réinitialiser un mot de passe oublié par email](../tutorial/password-reset.md) | un lien de réinitialisation envoyé par email | `smtplib`, jetons signés qui expirent |

### Unité 4 : interactivité

| Partie | Ce que tu ajoutes | Ce que tu apprends |
|---|---|---|
| [13. Recherchez les notes pendant que vous tapez](../tutorial/search-the-notes.md) | un champ de recherche qui filtre au fur et à mesure que vous tapez | React îles, accessoires de Python |
| [14. Cochez une note sans recharger la page](../tutorial/tick-a-note.md) | un bouton Terminé sur chaque note | enrichissement progressif, une Action pour une forme et pour `fetch` |

### À venir ensuite

| Unité | Ce que l'application gagne |
|---|---|
| 5. Au-delà de la demande | notes partagées par e-mail en arrière-plan, résumé quotidien, mises à jour en direct |
| 6. Navire | tests, pages et journaux d'erreurs, en-têtes de sécurité, une version Docker |

## Prochaines étapes

- [Partie 1 : créer le projet](../tutorial/create-the-project.md)
- [Concepts de base](core-concepts.md) : les mots utilisés dans le didacticiel
