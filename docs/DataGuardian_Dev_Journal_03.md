# DataGuardian - Journal de développement n°3

## Objectif de l'itération

Introduire un premier système de reporting HTML afin de rendre les résultats du moteur de qualité facilement consultables par un utilisateur sans avoir à lire directement les fichiers JSON.

---

## Fonctionnalité principale

### Génération d'un rapport HTML

Création du module :

```text
src/dataguardian/html_report.py
```

Fonction implémentée :

```python
generate_html_report(profile, filepath)
```

Cette fonction génère un rapport HTML autonome contenant :

- les informations globales du dataset ;
- les métriques de qualité ;
- les alertes détectées ;
- les métriques détaillées des colonnes.

---

## Contenu du rapport

### Dataset Overview

Affichage des métriques globales :

- nombre de lignes ;
- nombre de colonnes ;
- taux de doublons ;
- score de complétude.

### Quality Issues

Table listant :

- la sévérité ;
- la colonne concernée ;
- le message explicatif.

### Column Metrics

Table présentant :

- nom de colonne ;
- type ;
- complétude ;
- taux de nullité ;
- taux d'unicité.

---

## Export des artefacts

Le projet produit désormais deux sorties principales :

```text
artifacts/
├── summary.json
└── report.html
```

Le JSON reste destiné aux systèmes automatisés.

Le rapport HTML est destiné à la consultation humaine.

---

## Mise à jour de l'API publique

Mise à jour de :

```text
src/dataguardian/__init__.py
```

Export des fonctions :

```python
profile_dataframe
save_summary_json
generate_html_report
```

---

## Tests ajoutés

Nouveau fichier :

```text
tests/test_html_report.py
```

Vérifications réalisées :

- génération du fichier HTML ;
- présence du titre du rapport ;
- validation de la création physique du fichier.

---

## Problème rencontré

### Script d'exemple placé dans les tests

Un fichier de démonstration avait été placé dans :

```text
tests/test_export.py
```

Pytest tentait de l'exécuter lors de la phase de collecte.

Conséquence :

```text
FileNotFoundError
```

Correction :

- suppression du faux test ;
- déplacement du script dans le dossier `examples/` ;
- création d'un véritable test unitaire dédié à l'export JSON.

Résultat :

✅ GitHub Actions de nouveau au vert.

---

## Validation manuelle

Script d'exemple exécuté avec succès :

```text
examples/report_demo.py
```

Résultats obtenus :

✅ Génération de `summary.json`

✅ Génération de `report.html`

✅ Affichage correct du rapport dans un navigateur

✅ Suite de tests entièrement validée

---

## État actuel du projet

Fonctionnel :

✅ Profilage structurel

✅ Métriques de qualité

✅ Moteur d'anomalies

✅ Export JSON

✅ Rapport HTML

✅ Jeux de données d'exemple

✅ Tests automatisés

✅ GitHub Actions

---

## Position dans la roadmap

```text
DataFrame
      ↓
Profilage
      ↓
Métriques qualité
      ↓
Alertes
      ↓
summary.json
      ↓
report.html
```

Le projet couvre désormais les étapes :

- Observer
- Diagnostiquer
- Rapporter

---

## Prochaine étape envisagée (Version 0.4)

Objectif :

Introduire les premiers contrats de données réutilisables.

Fonctionnalités candidates :

- génération d'un contrat YAML ;
- description du schéma attendu ;
- contraintes de complétude ;
- contraintes d'unicité ;
- préparation du mode validation.
