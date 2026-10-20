# Livrables — test MyBestSim

## Dashboard

`dashboard.html` est un rapport autonome : les données des 18 CSV sont intégrées à la page. Il s'ouvre dans un navigateur sans dépendance, serveur ou installation. `index.html` est la même page, nommée ainsi pour servir de page d'accueil lors du déploiement.

En plus des indicateurs principaux, le dashboard détaille la répartition des volumes (1, 3, 5, 10, 20 et 50 Go), des durées de validité (7, 15 et 30 jours) et des réseaux 4G/5G. Il affiche aussi le volume médian et le prix médian par Go, calculés uniquement sur les offres à volume chiffré.

Pour recalculer le rapport après remplacement ou mise à jour des CSV :

```powershell
python generate_dashboard.py
```

Le script lit les fichiers de `donnees-test-mybestsim/` et régénère `dashboard.html` et `index.html`. Python 3 est requis ; aucune bibliothèque externe n'est utilisée.

Pour GitHub Pages, publier `index.html` à la racine d'une branche configurée pour Pages. La page contient le catalogue intégré et ne requiert ni serveur applicatif ni accès aux CSV une fois générée. Le dépôt doit être public pour un lien Pages accessible sans authentification.

### Méthode de calcul

- Une ligne de CSV correspond à une offre ; les 18 fichiers sont agrégés.
- Le seuil « plus de 100 € » est strictement supérieur à 100.
- Tous les prix des fichiers fournis sont en EUR.
- Les offres sans valeur numérique de data sont exclues de la moyenne en Go ; les autres indicateurs les incluent.
- Les libellés de destination sont comptés tels quels, y compris les régions et forfaits monde.

## Article SEO

`article-internet-croisiere-esim.md` contient l'article prêt à éditer et publier, avec métadonnées SEO, structure, tableaux, FAQ, idées d'images et sources.

# Regenerer le dashboard pour tester le code

Il faut placer les CSV dans 
'donnees-test-mybestsim/'
avant d’exécuter
'python generate_dashboard.py'
