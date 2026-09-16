# DataGuardian - Journal de mise en place du projet

## Objectif

Création du dépôt GitHub du projet **DataGuardian**, une librairie Python de profilage, validation et contrôle qualité de données.

---

# Étape 1 - Création du dépôt GitHub

Création d'un nouveau dépôt GitHub :

```text
DataGuardian
```

Le dépôt servira à :

- stocker le code source ;
- suivre l'historique des modifications ;
- héberger la documentation ;
- exécuter automatiquement les tests via GitHub Actions.

---

# Étape 2 - Configuration SSH

Création d'une paire de clés SSH afin de pouvoir communiquer avec GitHub sans saisir ses identifiants à chaque push.

Commande utilisée :

```powershell
ssh-keygen -t ed25519 -C "goussetleonard@gmail.com"
```

Emplacement de la clé :

```text
C:\Users\leongous\.ssh
```

Fichiers générés :

```text
id_ed25519
id_ed25519.pub
```

---

# Étape 3 - Emplacement du projet

Choix du dossier local :

```text
C:\Users\leongous\Documents\Projets
```

Le projet est cloné dans :

```text
C:\Users\leongous\Documents\Projets\DataGuardian
```

---

# Étape 4 - Premier commit

```powershell
git add .
git commit -m "Initial project structure"
git push origin main
```

---

# Étape 5 - README

Création du fichier README.md.

---

# Étape 6 - .gitignore

Création du fichier .gitignore pour exclure les fichiers temporaires et l'environnement virtuel.

---

# Étape 7 - GitHub Actions

Arborescence :

```text
.github/
└── workflows/
    └── ci.yml
```

Le workflow :

- démarre une machine Ubuntu ;
- clone le dépôt ;
- installe Python 3.11 ;
- installe pytest ;
- installe le package ;
- exécute les tests.

---

# Étape 8 - Première erreur rencontrée

Erreur :

```text
pytest: command not found
```

Correction :

```yaml
pip install pytest
```

---

# Étape 9 - Premier test automatisé

```python
def test_smoke():
    assert True
```

---

# Résultat actuel

Dépôt GitHub créé : OK

Git local configuré : OK

Clé SSH configurée : OK

README créé : OK

.gitignore créé : OK

Workflow GitHub Actions créé : OK

Pytest installé dans la CI : OK

Premier test automatisé : OK

Workflow au vert : OK

---

# Prochaines étapes

- Finaliser la structure du package Python
- Créer le pyproject.toml complet
- Développer le MVP de profilage
- Générer un premier rapport JSON
- Ajouter les tests métier
