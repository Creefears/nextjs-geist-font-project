# Moniteur USB avec Interface Graphique

Application de surveillance des périphériques USB avec interface graphique permettant de configurer des actions personnalisées pour chaque périphérique.

## Fonctionnalités

- Interface graphique moderne et intuitive
- Détection en temps réel des périphériques USB
- Configuration personnalisée des actions par périphérique :
  - Actions à la connexion
  - Actions à la déconnexion
- Types d'actions disponibles :
  - Lancement d'applications
  - Fermeture d'applications
  - Exécution de commandes personnalisées
- Icône dans la barre des tâches avec menu contextuel
- Notifications système lors des événements USB
- Activation/désactivation rapide de la surveillance
- Logging détaillé des événements

## Installation

1. Assurez-vous d'avoir Python 3.7+ installé
2. Installez les dépendances :
```bash
pip install -r requirements.txt
```
3. Exécutez le script d'installation :
```bash
install.bat
```

## Utilisation

1. Lancez l'application :
```bash
python usb_monitor.py
```

2. Une icône apparaît dans la barre des tâches
3. Double-cliquez sur l'icône pour ouvrir la configuration
4. Dans la fenêtre de configuration :
   - La liste de gauche affiche les périphériques USB connectés
   - Sélectionnez un périphérique pour configurer ses actions
   - Utilisez les boutons pour ajouter/supprimer des actions

## Interface de Configuration

### Fenêtre Principale
- Liste des périphériques USB détectés
- Actions configurées pour chaque périphérique
- Boutons d'ajout/suppression d'actions

### Configuration des Actions
Pour chaque périphérique, vous pouvez configurer :
- Actions à la connexion
- Actions à la déconnexion

Types d'actions disponibles :
1. Lancer une application
2. Fermer une application
3. Exécuter une commande

## Menu de la Barre des Tâches

- **Configuration** : Ouvre la fenêtre de configuration
- **Surveillance active** : Active/désactive la surveillance USB
- **Quitter** : Ferme l'application

## Notifications

L'application affiche des notifications système pour :
- Connexion de périphériques
- Déconnexion de périphériques
- Activation/désactivation de la surveillance
- Exécution des actions configurées

## Fichiers de Configuration

### device_actions.json
Stocke les configurations des actions pour chaque périphérique :
```json
{
    "Nom du périphérique (ID)": {
        "connect": {
            "type": "Lancer une application",
            "path": "chemin/vers/application.exe"
        },
        "disconnect": {
            "type": "Fermer une application",
            "path": "nom_application.exe"
        }
    }
}
```

## Logs

Les événements sont enregistrés dans `logs/usb_monitor.log` :
- Connexions/déconnexions de périphériques
- Actions exécutées
- Erreurs éventuelles

## Dépannage

1. **L'interface ne s'affiche pas**
   - Vérifiez que PyQt6 est correctement installé
   - Consultez les logs pour les erreurs

2. **Actions non exécutées**
   - Vérifiez les chemins des applications
   - Assurez-vous que la surveillance est active
   - Consultez les logs pour plus de détails

3. **Périphérique non détecté**
   - Reconnectez le périphérique
   - Vérifiez les pilotes Windows
   - Redémarrez l'application

## Sécurité et Performance

- Validation des chemins d'accès
- Gestion sécurisée des processus
- Faible utilisation des ressources
- Surveillance en arrière-plan

## Développement

Pour contribuer au projet :
1. Fork le dépôt
2. Créez une branche pour votre fonctionnalité
3. Soumettez une pull request

### Structure du Projet
```
usb_monitor/
├── usb_monitor.py    # Script principal et surveillance
├── gui.py           # Interface graphique
├── resources/       # Ressources (icônes, etc.)
├── logs/           # Fichiers de logs
└── device_actions.json  # Configuration des actions
```

## Support

Pour obtenir de l'aide :
1. Consultez les logs dans `logs/usb_monitor.log`
2. Vérifiez la configuration dans `device_actions.json`
3. Ouvrez une issue sur GitHub

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.
