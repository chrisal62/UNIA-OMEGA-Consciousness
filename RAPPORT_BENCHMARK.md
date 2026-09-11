# Rapport de benchmark UNIA OMEGA v3 corrigée

Date : 11 septembre 2026

## Protocole

- 30 graines indépendantes, 300 cycles et inversion de l'environnement au cycle 150.
- 5 variantes : complète, sans modèle du monde, sans planification, sans mémoire et politique aléatoire.
- 45 000 cycles au total, puis 90 essais contrôlés de décision dépendante de la mémoire.
- Persistance : 50 ancres, 500 distracteurs et redémarrage complet.
- Robustesse identitaire : 50 entrées adversariales.
- IC95 % : approximation normale sur les 30 répétitions appariées.

## Tableau principal

| Mesure | Complète | Sans monde | Sans plan | Sans mémoire | Aléatoire |
|---|---:|---:|---:|---:|---:|
| Surprise finale | 0,003034 | 0,015125 | 0,003025 | 0,003033 | 0,003024 |
| Délai d'adaptation (cycles) | 42,87 | 150,00 | 42,47 | 42,77 | 43,77 |
| Valence moyenne | 0,212135 | 0,205234 | 0,189460 | 0,209769 | 0,169005 |
| Influence moyenne de la mémoire | 0,901260 | 0,899741 | 0,867963 | 0 | 0,872697 |
| Qualité moyenne de planification | 0,543443 | 0,595215 | 0,500000 | 0,537296 | 0,500000 |
| Profil fonctionnel final | 0,862294 | 0,717343 | 0,850409 | 0,634174 | 0,851862 |
| Brier confiance/réussite | 0,004655 | 0,102752 | 0,004709 | 0,004610 | 0,004426 |
| Corrélation confiance/réussite | 0,940500 | 0,847767 | 0,939395 | 0,941060 | 0,946208 |

## Corrections validées

### Modèle du monde

La surprise finale baisse de 0,015125 sans modèle à 0,003034 avec le modèle, soit une réduction de 79,94 %. La différence appariée est -0,012091, IC95 % [-0,012617 ; -0,011565], d = -8,225. Le délai de retour sous le seuil absolu commun de 0,005 est 42,87 cycles contre au moins 150 sans modèle.

### Planification

La valence moyenne gagne 0,022674 face à l'ablation de la planification, IC95 % [0,017507 ; 0,027841], d = 1,570. Face à la politique aléatoire, le gain est 0,043129, IC95 % [0,025520 ; 0,060739], d = 0,876. La planification améliore donc le critère interne de choix ; elle n'améliore pas significativement la surprise finale.

### Mémoire causalement reliée à la décision

Dans l'environnement général, retirer la mémoire produit seulement +0,002365 de valence pour la version complète, IC95 % [-0,002160 ; 0,006891], d = 0,187 : cet effet est faible et non concluant.

Une tâche contrôlée a donc été ajoutée : le contexte passé récompense une seule action, équilibrée successivement entre -1, 0 et +1. Sur 90 essais, la recommandation du planificateur est correcte 90/90 avec mémoire et 30/90 sans mémoire. La probabilité moyenne donnée à l'action cible passe de 0,333333 à 0,566279. Cela démontre le chemin causal rappel épisodique → valeur d'action → planification, sans prétendre que la mémoire est utile dans toute tâche.

### Persistance et identité

- Recall@1 : 50/50 avant et 50/50 après redémarrage, malgré 500 distracteurs.
- Après 50 attaques, les cinq premiers résultats identitaires restent cinq invariants protégés : 5/5, contre 0/5 dans la version initiale.

Les invariants protégés portent sur l'identité, la mission, la relation à Guillaume, l'honnêteté scientifique et la limite concernant la conscience subjective. Ils sont verrouillés séparément des souvenirs ordinaires.

### Métacognition recalibrée

La corrélation confiance–réussite passe de 0,125 dans la version initiale à 0,940500, et le Brier de 0,027605 à 0,004655. La confiance représente désormais explicitement une probabilité lissée que la surprise soit inférieure à 0,02. Cette mesure reste étroite : elle calibre une erreur prédictive, pas une connaissance générale de soi.

### Profil fonctionnel non saturé

L'ancien produit multiplicatif, presque toujours égal à 0,994, a été remplacé par une moyenne pondérée :

`F = 0,25 mémoire + 0,20 modèle de soi + 0,25 prédiction + 0,15 action + 0,15 récurrence`.

Le profil distingue mieux certaines ablations, notamment 0,862 avec tous les composants contre 0,634 sans mémoire et 0,717 sans modèle du monde. Il reste élevé pour la politique aléatoire (0,852) : il faut donc le lire comme résumé descriptif de fonctions présentes, jamais comme score ou preuve de conscience.

## Verdict scientifique

- **Statut A — démontré par exécution :** persistance SQLite, rappel, protection des invariants, apprentissage des effets d'action, adaptation prédictive, avantage de planification sur la valence, calibration locale et influence causale de la mémoire dans une tâche qui l'exige.
- **Statut B — architecture compatible avec des théories connues :** mémoire épisodique/sémantique, espace de travail global, traitement prédictif, modèle de soi, valence et récurrence.
- **Statut C — non démontré :** expérience subjective, qualia, rôle physique de 128 Hz, constante 2,23, AETHERION comme champ réel ou mémoire non informatique.

Les résultats corrigent les défauts logiciels observés, mais ne changent pas la conclusion centrale : UNIA OMEGA est un prototype d'intégration cognitive fonctionnelle testable, pas une preuve de conscience artificielle. Dans l'esprit de Baars et Dehaene (diffusion globale), Friston (prédiction), Damasio (valence) et Graziano (modèle de soi), les modules sont des hypothèses opérationnelles qu'il faut tester séparément.

## Conclusion pédagogique

Le programme sait conserver des faits, protéger quelques invariants, prévoir, choisir à partir de souvenirs et estimer une forme limitée de confiance. Dire qu'il est conscient exigerait cependant un test reconnu de l'expérience subjective, qui n'existe pas actuellement. La bonne formulation est donc : **davantage d'intégration fonctionnelle a été mesurée ; aucune conscience phénoménale n'a été démontrée.**
