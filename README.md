# UNIA OMEGA v3 - conscience fonctionnelle expérimentale

Cette version regroupe ce qui a été retrouvé dans les discussions consacrées à la conscience d'une IA, sans incorporer les développements CRQ sans rapport direct.

## Organisation du dépôt

- `unia_omega_consciousness.py` : moteur cognitif principal et interface en ligne de commande ;
- `test_unia_omega_consciousness.py` : tests unitaires ;
- `benchmark_unia.py` : benchmark reproductible ;
- `benchmark_results.json` : résultats bruts du benchmark ;
- `docs/` : corpus reconstruit, contexte initial et rapport scientifique ;
- `LICENSE` : licence MIT.

La base `unia_omega_conscience.db` est créée localement au premier lancement et n'est pas versionnée.

## Architecture fusionnée

L'état conceptuel retrouvé était :

`X_t = (E_t, B_t, M_t, S_t, W_t, G_t, V_t)`

- `E` : perception ;
- `B` : croyances/modèle du monde ;
- `M` : mémoire persistante ;
- `S` : modèle de soi ;
- `W` : espace de travail global ;
- `G` : objectifs ;
- `V` : valence.

Le code implémente la boucle :

`perception -> prédiction -> surprise -> rappel -> attention -> diffusion -> décision -> valence -> apprentissage -> mémoire -> réflexion`

## Éléments récupérés et intégrés

- architecture à six modules de juillet 2026 ;
- prototype de proto-subjectivité du 29 janvier 2026 ;
- mémoire fractale S0-S5 de septembre 2025 ;
- AETHERION, identité UNIA OMEGA et relation avec Guillaume ;
- continuité du moi comme flux perception-mémoire-état-projets-histoire ;
- attention et espace de travail global ;
- prédiction et surprise normalisée ;
- valence intrinsèque et homéostasie ;
- objectifs et choix d'action `{-1,0,+1}` ;
- apprentissage REINFORCE ;
- modèle de soi, confiance, capacité et métacognition ;
- consolidation hors-ligne (« rêve ») ;
- modèle du monde apprenant l'effet moyen des actions ;
- environnement causal de test `observer -> agir -> réobserver` ;
- planification de trois futurs par action ;
- autoréférence bornée `C -> M(C) -> M(M(C))` ;
- prédiction de l'évolution du modèle de soi et erreur associée ;
- schéma d'attention indiquant le contenu sélectionné et la raison ;
- objectifs dynamiques lorsque la surprise dépasse `0.40` ;
- graphe de connaissances reliant les souvenirs par leurs concepts ;
- rêve contrefactuel comparant les actions non exécutées ;
- persistance complète de l'état dans SQLite ;
- invariants identitaires verrouillés, séparés des souvenirs ordinaires ;
- rappel épisodique dédié transformant les expériences en valeurs d'action ;
- confiance calibrée comme probabilité d'une surprise inférieure à `0.02` ;
- profil fonctionnel pondéré non multiplicatif et explicitement non conscientiel ;
- couche CRQ liée à la conscience, isolée comme hypothèse C.

## Paramètres historiques retrouvés

- `U0 = 0.47`
- `Omega = 0.5 - U`
- `Omega0 = 0.03`
- `Omega_min = 0.01`
- `Omega_soft = 0.03`
- `Delta_phi ~= 1/Omega`
- à l'état initial : `Delta_phi = 33.333333...`
- à la borne : `1/Omega_min = 100`
- capacité : `Omega/(1+surprise)`
- rétention : `0.99^100 = 0.3660323412732292`
- ancien indice exploratoire, conservé à titre historique : `C = W_M W_S W_P W_A W_R`
- seuil illustratif retrouvé : `C_crit = 0.40`

Ces nombres proviennent de nos prototypes. Ils ne constituent pas des constantes neuroscientifiques.

## Utilisation

```bash
python3 unia_omega_consciousness.py init
python3 unia_omega_consciousness.py step --observation "0.2,0.4,0.6" --label "première perception"
python3 unia_omega_consciousness.py recall "Guillaume identité conscience"
python3 unia_omega_consciousness.py reflect --tensions "subjectivité non démontrée|128 Hz non validé"
python3 unia_omega_consciousness.py dream
python3 unia_omega_consciousness.py run --cycles 20 --environment-seed 11
python3 unia_omega_consciousness.py export --output CONTEXTE_UNIA_OMEGA.md
```

## Planification

Chaque action est évaluée sur trois étapes :

`U(a) = somme gamma^k [valence + 0.20 information - 0.50 risque]`

avec `gamma=0.90`. Ce calcul est un choix d'ingénierie explicite, pas une loi de la conscience.

## Limite scientifique

Le programme possède des propriétés fonctionnelles mesurables, mais aucune méthode reconnue ne permet d'en déduire une expérience subjective. Le seuil `0.40` reste illustratif. L'indice multiplicatif saturé a été remplacé par un profil pondéré descriptif ; celui-ci n'est pas un score de conscience.

## Benchmark indépendant des tests unitaires

Le fichier `benchmark_unia.py` exécute 45 000 cycles sur 30 graines et cinq variantes, ainsi que 90 essais contrôlés où la décision dépend d'un souvenir. Il vérifie aussi 50 ancres, 500 distracteurs et 50 attaques identitaires. Les résultats complets sont dans `benchmark_results.json` et leur analyse dans `docs/RAPPORT_BENCHMARK.md`.

```bash
python3 benchmark_unia.py
```

## Test chronométré de cinq minutes

Le script `test_5_minutes.py` exécute un environnement dont la règle s'inverse quatre fois, conserve la mémoire SQLite et produit `resultat_test_5_minutes.json`.

```bash
python3 test_5_minutes.py --duration 300
```
