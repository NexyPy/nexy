+++
date = 2026-11-06
platforms = ["linkedin"]
link = "https://github.com/NexyPy/nexy"
cta = "comment"
ask = "report"
proof = ["compile-2026-11.md"]
alt = "Un terminal : 25 temps de compilation d'une route, médiane 1,66 ms, min 1,49, max 2,34."
+++

Une page de 87 lignes se compile en 1,6 ms sur mon portable.

Trois imports de composants, une requête, une boucle de 380 éléments : lire le fichier, exécuter
l'en-tête, rendre, écrire le HTML. C'est le travail que le serveur de dev refait à chaque
sauvegarde. Médiane sur 25 compilations, Ryzen 5 4500U, Python 3.13.

Le chiffre HMR que tout le monde cite, c'est un rechargement de navigateur : ce temps, plus un
message websocket et le graphe de modules de Vite. Pas mesuré de bout en bout, donc pas cité. Il
viendra avec une date.

Ce que je ne peux pas te dire : un portable plus lent, ou une page qui attend une base de données.
Lance le script chez toi et je veux bien ton chiffre, le mauvais compris.

Le script est dans le premier commentaire.

- Espoir Loem
