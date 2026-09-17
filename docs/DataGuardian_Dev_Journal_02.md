# DataGuardian - Journal de développement n°2

## Objectif de l'itération

Faire évoluer DataGuardian d'un simple moteur de profilage vers un premier outil de diagnostic de qualité des données.

Cette itération introduit :
- de nouvelles métriques de qualité ;
- un système d'alertes automatiques ;
- l'export JSON des résultats ;
- les premiers tests du moteur qualité.

---

## Évolutions du modèle de données

### Ajout de QualityIssue

Création d'une nouvelle dataclass permettant de représenter une anomalie détectée, avec un niveau de sévérité, une colonne concernée et un message explicatif.

### Évolution de ColumnProfile

Ajout des métriques :
- null_rate
- completeness

Formules :

```text
null_rate = null_count / row_count
completeness = non_null_count / row_count
```

### Évolution de DatasetProfile

Ajout des métriques :
- duplicate_rate
- completeness_score
- issues

Formules :

```text
duplicate_rate = duplicate_rows / row_count
completeness_score = total_non_null / total_cells
```

---

## Création du moteur qualité

Nouveau module :

```text
quality.py
```

Fonction principale :

```python
detect_quality_issues()
```

Règles implémentées :
- WARNING si le taux de doublons dépasse 5 % ;
- ERROR si une colonne est totalement vide ;
- WARNING si le taux de nullité dépasse 20 % ;
- WARNING si le taux d'unicité est inférieur à 10 %.

---

## Évolution du moteur de profilage

Mise à jour de `profiler.py` pour calculer :

### Niveau dataset
- duplicate_rate
- completeness_score

### Niveau colonne
- null_rate
- completeness

Intégration automatique du moteur qualité afin d'alimenter :

```python
profile.issues
```

---

## Export JSON

Mise à jour de `report.py` avec une nouvelle fonction :

```python
save_summary_json()
```

Cette fonction génère un fichier :

```text
summary.json
```

contenant :
- les métriques globales ;
- les métriques par colonne ;
- les alertes détectées.

---

## Tests ajoutés

Création de :

```text
tests/test_quality.py
```

Tests validés :
- détection d'un taux de nullité élevé ;
- détection d'une colonne vide ;
- détection d'un taux de doublons élevé.

Tous les tests passent avec succès.

---

## Validation manuelle

Création d'un dataset d'exemple volontairement dégradé :

```text
dirty_customers.csv
```

Validation réalisée :
- profilage du dataset ;
- détection des alertes ;
- génération du fichier summary.json ;
- vérification du contenu exporté.

Résultat :

Profil calculé correctement OK

Alertes détectées OK

Export JSON fonctionnel OK

Tests unitaires au vert OK

---

## Problème rencontré

### GitHub Actions en échec

Erreur :

```text
TOMLDecodeError: Invalid statement
```

Cause identifiée : présence de balises HTML (`<br>` et `&gt;`) dans `pyproject.toml`.

Correction :
- nettoyage du fichier ;
- réécriture avec une syntaxe TOML valide.

Résultat :

```bash
pip install -e .
```

fonctionne de nouveau dans GitHub Actions.

---

## État actuel du projet

✅ Package Python installable

✅ CI GitHub Actions fonctionnelle

✅ Profilage structurel

✅ Calcul des métriques qualité

✅ Détection d'anomalies

✅ Export JSON

✅ Suite de tests automatisés

✅ Dataset d'exemple

---

## Position dans la roadmap

```text
DataFrame
      ↓
Profilage
      ↓
DatasetProfile
      ↓
Détection d'anomalies
      ↓
QualityIssue
      ↓
summary.json
```

Les phases « Observer » et « Diagnostiquer » sont désormais couvertes.

---

## Prochaine étape (Version 0.3)

Objectif : produire un rapport qualité plus lisible et exploitable.

Pistes :
- score qualité global ;
- consolidation des niveaux de sévérité ;
- génération d'un rapport HTML ;
- hiérarchisation des anomalies ;
- métadonnées d'exécution ;
- amélioration de la présentation des résultats.
