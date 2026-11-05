# Barre d'outils de développement

`nexy dev` ajoute une barre d'outils à chaque page HTML. Il se trouve dans le coin inférieur gauche, indique l'itinéraire sur lequel vous vous trouvez et la durée du serveur, et s'ouvre sur un panneau. Cela ne fait jamais partie d’une réponse de production.

| L'onglet | affiche |
|---|---|
| Page | URL, route, gestionnaire, le fichier d'où il provient (avec un lien qui l'ouvre dans votre éditeur), statut, heure du serveur, premier octet, premier dessin, contenu principal, changement de mise en page (gradué vert, orange ou rouge), prêt pour DOM |
| Routes | chaque itinéraire de l'application avec ses méthodes, un filtre et celui actuel marqué ; chacun renvoie à son fichier |
| Erreurs | erreurs du serveur depuis le démarrage de `nexy dev` et erreurs générées par le navigateur |
| Paramètres | thème (correspondre à la page, sombre ou clair), position, taille, masquer, réinitialiser |

## Déplacez-le

Faites glisser le bouton : il suit le pointeur et s'accroche au coin le plus proche lorsque vous le relâchez. Le panneau s'ouvre vers le milieu de l'écran, quel que soit l'endroit où se trouve le bouton. La position est conservée dans ce navigateur. Vous pouvez également choisir un coin dans **Paramètres**.

`Shift` + `Alt` + `D` masque et affiche la barre d'outils. `Esc` ferme le panneau.

## Erreurs

Une erreur non détectée dans le navigateur ouvre une boîte de dialogue sur la page avec le message et la pile ; avec plusieurs erreurs, parcourez-les (1 sur 3). Une erreur de serveur répond par une page du même genre : l'erreur, l'endroit où elle a été générée et le code qui l'entoure.

## Éteignez-le

```python filename="nexyconfig.py"
class NexyConfig(NexyConfigModel):
    useDevTools = False
```

La barre d'outils est un bloc de style et un script ajouté avant `</body>` : pas de requête externe, pas de dépendance. JSON, les fichiers et chaque réponse qui n'est pas HTML sont laissés seuls.

## Prochaines étapes

- [Config](../reference/config.md) : toutes les options
- [Testing](testing.md) : tester une page ou un composant
