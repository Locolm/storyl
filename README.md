# Guide pour exécuter l'application

Ce guide vous explique comment configurer et exécuter l'application en mode développement.

---

## 1. Installation des dépendances Python

1. Assurez-vous que Python est installé sur votre machine.
2. Installez les dépendances nécessaires en exécutant les dépendances spécifiées dans le fichier `requirements.txt` présent dans le répertoire du projet (à la racine) :

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

Pour exécuter l'application, executez le script principal depuis la racine: 

```bash
flask --app app/app run
```

## 4. Obtenir une clé API OpenAI
Pour utiliser l'application, vous devez avoir une clé API OpenAI valide. Suivez ces étapes pour obtenir votre clé API :

1. Créez un compte OpenAI :
    - Aller sur le [site d'OpenAI](https://platform.openai.com/signup) et inscrivez vous 
2. Récupérer la clé API:
    - Une fois inscrit allez dans votre [tableau de bord OpenAI](https://platform.openai.com/api-keys)
    - Cliquez sur Create new secret key pour générer une nouvelle clé API.
    - Copiez la clé API générée et gardez-la en sécurité, car vous en aurez besoin pour configurer l'application.
3. Vérifiez la facturation :
    - Vous pouvez vérifier l'état de votre facturation et les informations liées à votre clé API sur la [page de facturation](https://platform.openai.com/settings/organization/billing/overview) OpenAI.
    - Coût de base : L'API OpenAI coûte environ 6 \$ pour commencer (5 \$ + TVA), vous disposerez ensuite de 5 \$ de crédits pour utiliser n'importe quel modèle disponible.
Ce projet utilise le modèle GPT-4 (GPT-4 o-mini) qui coûte 0,15 \$ par millions de token pour l'input et 0,60 \$ par millions de token en output.

## 5. Utiliser l'interface

Une fois la clé API obtenue, saisissez-la dans l’espace dédié en haut à droite, accessible via les trois traits horizontaux.
Vous pourrez ensuite utiliser les commandes disponibles pour interagir avec le jeu.
La carte des lieux et des PNJs est visible en haut à droite, tandis que la description des lieux et des personnages s’affiche à gauche.

Lors de l’exécution d’une commande, un icône de chargement apparaît. Attendez la fin du chargement avant d’entrer une nouvelle commande, afin d’éviter l’envoi en double.