# Guide pour exécuter l'application

Ce guide vous explique comment configurer et exécuter l'application en mode développement.

---

## 1. Installation des dépendances Python

1. Assurez-vous que Python est installé sur votre machine.
2. Installez les dépendances nécessaires en exécutant les dépendances spécifiées dans le fichier `requirements.txt` présent dans le répertoire du projet :

```bash
pip install -r requirements.txt
```

## 2. Mode développement

En mode développement, TailwindCSS est configuré pour recompiler automatiquement les styles.

Naviguez dans le répertoire `app/` de l'application et lancez la commande suivante : 

```bash
npm run dev
```

## 3. Exécution de l'application

Pour exécuter l'application, executez le script principal : 

```bash
python app.py
```