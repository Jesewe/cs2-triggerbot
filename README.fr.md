<div align="center">
   <img src="src/img/icon.png" alt="CS2 TriggerBot" width="200" height="200">
   <h1>🎯 CS2 TriggerBot 🎯</h1>
   <p>Votre assistant de visée ultime pour Counter-Strike 2</p>
   <a href="#fonctionnalités"><strong>Fonctionnalités</strong></a> •
   <a href="#installation"><strong>Installation</strong></a> •
   <a href="#utilisation"><strong>Utilisation</strong></a> •
   <a href="#personnalisation"><strong>Personnalisation</strong></a> •
   <a href="#dépannage"><strong>Dépannage</strong></a> •
   <a href="#contribution"><strong>Contribution</strong></a>
</div>

---

# Aperçu
CS2 TriggerBot est un outil automatisé conçu pour Counter-Strike 2, qui aide à viser avec précision en déclenchant automatiquement un clic de souris lorsqu'un ennemi est détecté dans le réticule du joueur.

## Fonctionnalités
- **Tir automatique :** Déclenche automatiquement un clic de souris lorsqu'un ennemi est détecté.
- **Attachement au processus :** Se connecte au processus `cs2.exe` et lit les valeurs de mémoire pour prendre des décisions en temps réel.
- **Touche de déclenchement personnalisable :** Permet aux utilisateurs de définir leur propre touche de déclenchement pour l'activation.
- **Vérification des mises à jour :** Vérifie automatiquement la dernière version et avertit l'utilisateur si une mise à jour est disponible.
- **Journalisation des erreurs :** Enregistre les erreurs et les événements importants dans un fichier journal à des fins de débogage.

## Installation
1. **Cloner le dépôt :**
   ```bash
   git clone https://github.com/Jesewe/cs2-triggerbot.git
   cd cs2-triggerbot
   ```

2. **Installer les dépendances :**
   ```bash
   pip install -r requirements.txt
   ```

3. **Exécuter le script :**
   ```bash
   python main.py
   ```

## Utilisation
1. Assurez-vous que Counter-Strike 2 est en cours d'exécution.
2. Exécutez le script en utilisant la commande ci-dessus.
3. Le script vérifiera automatiquement les mises à jour et récupérera les offsets nécessaires depuis les sources fournies.
4. Une fois le script lancé, appuyez sur la touche de déclenchement configurée (par défaut : `X`) pour activer TriggerBot.
5. L'outil simulera automatiquement des clics de souris lorsque qu'un ennemi sera détecté dans le réticule.

## Personnalisation
- **Touche de déclenchement :** Vous pouvez changer la touche de déclenchement en modifiant la variable `TRIGGER_KEY` dans le script.
- **Répertoire des journaux :** Les fichiers journaux sont enregistrés par défaut dans le répertoire `%LOCALAPPDATA%\Requests\ItsJesewe\crashes`. Vous pouvez changer cela en modifiant la variable `LOG_DIRECTORY`.

## Dépannage
- **Échec de la récupération des offsets :** Assurez-vous que vous avez une connexion Internet active et que les URL sources sont accessibles.
- **Impossible d'ouvrir `cs2.exe` :** Assurez-vous que le jeu est en cours d'exécution et que vous avez les autorisations nécessaires.
- **Erreurs inattendues :** Consultez le fichier journal situé dans le répertoire des journaux pour plus de détails.

## Contribution
Les contributions sont les bienvenues ! Veuillez ouvrir un ticket ou soumettre une pull request sur le [dépôt GitHub](https://github.com/Jesewe/cs2-triggerbot).

## Avertissement
Ce script est uniquement destiné à des fins éducatives. L'utilisation de cheats ou de hacks dans les jeux en ligne est contraire aux conditions d'utilisation de la plupart des jeux et peut entraîner des bans ou d'autres sanctions. Utilisez ce script à vos propres risques.

## Licence
Ce projet est sous licence MIT. Consultez le fichier [LICENSE](LICENSE) pour plus de détails.