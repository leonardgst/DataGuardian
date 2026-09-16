# DataGuardian - Journal de développement n°1

## Objectif de l'itération

Mise en place du premier noyau fonctionnel de DataGuardian.

L'objectif était d'obtenir un profilage minimal d'un DataFrame Pandas afin de valider l'architecture générale du projet avant l'ajout des fonctionnalités avancées (alertes, contrats de données, validation ou détection de dérive). 【1-c41a88】【2-d265cd】

---

## Architecture mise en place

Arborescence actuelle :

```text
src/
└── dataguardian/
    ├── __init__.py
    ├── api.py
    ├── models.py
    ├── profiler.py
    └── report.py
```

### __init__.py

Expose les fonctions publiques du package.

Actuellement :

- profile_dataframe()

---

### api.py

Point d'entrée public de la librairie.

Responsabilités :

- fournir une interface stable aux utilisateurs ;
- masquer les détails internes d'implémentation ;
- déléguer les traitements aux modules métier.

---

### models.py

Définition des objets métier.

Objets créés :

- ColumnProfile
- DatasetProfile

Ces objets représentent les résultats du profilage.

Ils constituent le langage interne du projet.

---

### profiler.py

Premier moteur d'analyse.

Fonction implémentée :

- profile_dataframe()

Métriques calculées :

- nombre de lignes ;
- nombre de colonnes ;
- nombre de doublons stricts ;
- nombre de valeurs nulles ;
- nombre de valeurs non nulles ;
- cardinalité ;
- taux d'unicité.

Le résultat est retourné sous forme d'un objet DatasetProfile.

---

### report.py

Première base de sérialisation.

Fonction présente :

- conversion d'un DatasetProfile vers un dictionnaire.

Cette couche servira plus tard à produire :

- summary.json ;
- report.html ;
- autres formats d'export.

---

## Tests réalisés

Tests unitaires créés :

- comptage des lignes ;
- comptage des colonnes ;
- détection des doublons ;
- calcul des valeurs nulles ;
- calcul du taux d'unicité.

Tous les tests passent avec succès.

---

## Problèmes rencontrés

### Incompatibilité Python 3.14

L'environnement initial utilisait Python 3.14.

Cela a provoqué une erreur lors du chargement de NumPy :

```text
ImportError: DLL load failed while importing _multiarray_umath
```

Solution :

- suppression du premier environnement virtuel ;
- utilisation de Python 3.12 ;
- recréation du venv ;
- réinstallation complète des dépendances.

---

### Structure du package incorrecte

Les fichiers Python avaient initialement été placés directement dans :

```text
src/
```

au lieu de :

```text
src/dataguardian/
```

Conséquence :

```text
ModuleNotFoundError: No module named 'dataguardian'
```

Solution :

- création du package dataguardian ;
- déplacement des modules ;
- réinstallation du package en mode editable.

---

## État actuel du projet

Fonctionnel :

✅ Dépôt GitHub créé

✅ GitHub Actions opérationnel

✅ Package Python installable

✅ Architecture du projet en place

✅ Imports fonctionnels

✅ Premier moteur de profilage

✅ Objets métier définis

✅ Suite de tests initiale

✅ Exécution manuelle validée

✅ Environnement Python stabilisé sous Python 3.12

---

## Exemple d'utilisation actuel

```python
import pandas as pd

from dataguardian import profile_dataframe

df = pd.read_csv("examples/customers.csv")

profile = profile_dataframe(df)

print(profile)
```

Le résultat retourné est un objet `DatasetProfile` contenant les statistiques de base du dataset.

---

## Vision du flux d'exécution

```text
DataFrame
      ↓
profile_dataframe()
      ↓
DatasetProfile
      ↓
Exports futurs
(JSON / HTML)
      ↓
Alertes qualité
      ↓
Contrats de données
      ↓
Validation des livraisons futures
```

Cette architecture suit la logique définie dans le cahier des charges du projet : observer, diagnostiquer puis contractualiser la qualité des données. 【2-d265cd】

---

## Prochaine étape (Version 0.2)

Objectif :

Produire un premier rapport qualité exploitable.

Fonctionnalités visées :

- calcul du taux de nullité ;
- calcul du taux de doublons ;
- score de complétude ;
- premières alertes automatiques ;
- export summary.json.

Cette version commencera à transformer le simple moteur de profilage en véritable outil de contrôle de la qualité des données. 【2-d265cd】