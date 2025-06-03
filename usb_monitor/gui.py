import sys
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QComboBox, QPushButton, 
                            QListWidget, QDialog, QLineEdit, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
import wmi

class ActionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurer l'action")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Type d'action
        self.action_type = QComboBox()
        self.action_type.addItems(["Lancer une application", "Fermer une application", "Exécuter une commande"])
        layout.addWidget(QLabel("Type d'action:"))
        layout.addWidget(self.action_type)
        
        # Chemin ou commande
        self.path_input = QLineEdit()
        layout.addWidget(QLabel("Chemin/Commande:"))
        layout.addWidget(self.path_input)
        
        # Boutons
        buttons = QHBoxLayout()
        save_btn = QPushButton("Enregistrer")
        cancel_btn = QPushButton("Annuler")
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        buttons.addWidget(save_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        self.setLayout(layout)
    
    def get_action_data(self):
        return {
            "type": self.action_type.currentText(),
            "path": self.path_input.text()
        }

class USBMonitorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Moniteur USB")
        self.setMinimumSize(800, 600)
        
        # Initialisation WMI
        self.wmi = wmi.WMI()
        
        # Chargement de la configuration
        self.load_config()
        
        # Création de l'interface
        self.setup_ui()
        
        # Timer pour la mise à jour des périphériques
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_device_list)
        self.update_timer.start(1000)  # Mise à jour toutes les secondes
    
    def load_config(self):
        try:
            with open('device_actions.json', 'r') as f:
                self.device_actions = json.load(f)
        except FileNotFoundError:
            self.device_actions = {}
    
    def save_config(self):
        with open('device_actions.json', 'w') as f:
            json.dump(self.device_actions, f, indent=4)
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout()
        
        # Panneau gauche - Liste des périphériques
        left_panel = QVBoxLayout()
        left_panel.addWidget(QLabel("Périphériques USB connectés:"))
        
        self.device_list = QListWidget()
        left_panel.addWidget(self.device_list)
        
        # Bouton pour rafraîchir la liste
        refresh_btn = QPushButton("Rafraîchir")
        refresh_btn.clicked.connect(self.update_device_list)
        left_panel.addWidget(refresh_btn)
        
        # Panneau droit - Configuration des actions
        right_panel = QVBoxLayout()
        right_panel.addWidget(QLabel("Actions configurées:"))
        
        self.action_list = QListWidget()
        right_panel.addWidget(self.action_list)
        
        # Boutons d'action
        button_layout = QHBoxLayout()
        
        add_connect_action = QPushButton("Ajouter action connexion")
        add_connect_action.clicked.connect(lambda: self.add_action("connect"))
        
        add_disconnect_action = QPushButton("Ajouter action déconnexion")
        add_disconnect_action.clicked.connect(lambda: self.add_action("disconnect"))
        
        remove_action = QPushButton("Supprimer action")
        remove_action.clicked.connect(self.remove_action)
        
        button_layout.addWidget(add_connect_action)
        button_layout.addWidget(add_disconnect_action)
        button_layout.addWidget(remove_action)
        
        right_panel.addLayout(button_layout)
        
        # Ajout des panneaux au layout principal
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        
        layout.addWidget(left_widget)
        layout.addWidget(right_widget)
        
        central_widget.setLayout(layout)
        
        # Mise à jour initiale de la liste des périphériques
        self.update_device_list()
        self.update_action_list()
    
    def update_device_list(self):
        self.device_list.clear()
        for device in self.wmi.Win32_PnPEntity():
            if device.DeviceID:
                item_text = f"{device.Name} ({device.DeviceID})"
                self.device_list.addItem(item_text)
    
    def update_action_list(self):
        self.action_list.clear()
        selected_device = self.device_list.currentItem()
        if selected_device and selected_device.text() in self.device_actions:
            actions = self.device_actions[selected_device.text()]
            for event_type, action in actions.items():
                self.action_list.addItem(f"{event_type}: {action['type']} - {action['path']}")
    
    def add_action(self, event_type):
        selected_device = self.device_list.currentItem()
        if not selected_device:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner un périphérique")
            return
        
        dialog = ActionDialog(self)
        if dialog.exec():
            action_data = dialog.get_action_data()
            device_id = selected_device.text()
            
            if device_id not in self.device_actions:
                self.device_actions[device_id] = {}
            
            self.device_actions[device_id][event_type] = action_data
            self.save_config()
            self.update_action_list()
    
    def remove_action(self):
        selected_action = self.action_list.currentItem()
        selected_device = self.device_list.currentItem()
        
        if not selected_action or not selected_device:
            QMessageBox.warning(self, "Erreur", "Veuillez sélectionner une action à supprimer")
            return
        
        event_type = selected_action.text().split(':')[0]
        device_id = selected_device.text()
        
        if device_id in self.device_actions and event_type in self.device_actions[device_id]:
            del self.device_actions[device_id][event_type]
            if not self.device_actions[device_id]:  # Si plus d'actions pour ce périphérique
                del self.device_actions[device_id]
            self.save_config()
            self.update_action_list()

def main():
    app = QApplication(sys.argv)
    window = USBMonitorGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
