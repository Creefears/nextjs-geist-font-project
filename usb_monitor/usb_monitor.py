import os
import sys
import time
import wmi
import json
import psutil
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QThread, pyqtSignal

class USBMonitorWorker(QThread):
    device_changed = pyqtSignal(str, str)  # (device_id, event_type)

    def __init__(self):
        super().__init__()
        self.setup_logging()
        self.wmi = wmi.WMI()
        self.running = True
        
    def setup_logging(self):
        """Configure le système de logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            filename=log_dir / 'usb_monitor.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def execute_action(self, action_data):
        """Exécute une action configurée"""
        try:
            action_type = action_data['type']
            path = action_data['path']
            
            if action_type == "Lancer une application":
                if not any(proc.name().lower() == Path(path).name.lower() 
                          for proc in psutil.process_iter(['name'])):
                    subprocess.Popen(path)
                    self.logger.info(f"Application lancée: {path}")
                    
            elif action_type == "Fermer une application":
                for proc in psutil.process_iter(['name']):
                    try:
                        if Path(path).name.lower() in proc.name().lower():
                            proc.terminate()
                            self.logger.info(f"Application fermée: {path}")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                        
            elif action_type == "Exécuter une commande":
                subprocess.Popen(path, shell=True)
                self.logger.info(f"Commande exécutée: {path}")
                
        except Exception as e:
            self.logger.error(f"Erreur lors de l'exécution de l'action: {e}")

    def load_actions(self):
        """Charge les actions configurées depuis le fichier JSON"""
        try:
            with open('device_actions.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def run(self):
        """Thread principal de surveillance des périphériques"""
        known_devices = set()
        
        while self.running:
            try:
                # Obtenir la liste actuelle des périphériques
                current_devices = set()
                for device in self.wmi.Win32_PnPEntity():
                    if device.DeviceID:
                        current_devices.add(f"{device.Name} ({device.DeviceID})")
                
                # Détecter les nouveaux périphériques
                for device in current_devices - known_devices:
                    self.logger.info(f"Périphérique connecté: {device}")
                    self.device_changed.emit(device, "connect")
                
                # Détecter les périphériques déconnectés
                for device in known_devices - current_devices:
                    self.logger.info(f"Périphérique déconnecté: {device}")
                    self.device_changed.emit(device, "disconnect")
                
                known_devices = current_devices
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Erreur lors de la surveillance: {e}")
                time.sleep(1)
    
    def stop(self):
        """Arrête le thread de surveillance"""
        self.running = False
        self.wait()

class USBMonitor:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.setup_tray()
        self.worker = USBMonitorWorker()
        self.worker.device_changed.connect(self.handle_device_change)
        self.actions = self.worker.load_actions()
    
    def setup_tray(self):
        """Configure l'icône de la barre des tâches"""
        self.tray = QSystemTrayIcon()
        
        # Charger l'icône
        icon_path = os.path.join(os.path.dirname(__file__), 'resources', 'icon.svg')
        if os.path.exists(icon_path):
            self.tray.setIcon(QIcon(icon_path))
        
        self.tray.setToolTip("Moniteur USB")
        
        # Menu contextuel
        menu = QMenu()
        
        # Action de configuration
        config_action = menu.addAction("Configuration")
        config_action.triggered.connect(self.show_config)
        
        # Séparateur
        menu.addSeparator()
        
        # État de surveillance
        self.monitor_action = menu.addAction("Surveillance active")
        self.monitor_action.setCheckable(True)
        self.monitor_action.setChecked(True)
        self.monitor_action.triggered.connect(self.toggle_monitoring)
        
        # Séparateur
        menu.addSeparator()
        
        # Action pour quitter
        quit_action = menu.addAction("Quitter")
        quit_action.triggered.connect(self.quit_app)
        
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.tray_activated)
        self.tray.show()
    
    def show_config(self):
        """Affiche la fenêtre de configuration"""
        from gui import USBMonitorGUI
        if not hasattr(self, 'config_window') or not self.config_window.isVisible():
            self.config_window = USBMonitorGUI()
            self.config_window.show()
        else:
            self.config_window.activateWindow()
            self.config_window.raise_()
    
    def toggle_monitoring(self, checked):
        """Active ou désactive la surveillance USB"""
        if checked:
            self.worker.running = True
            self.worker.start()
            self.tray.showMessage(
                "Moniteur USB",
                "Surveillance USB activée",
                QSystemTrayIcon.Information,
                2000
            )
        else:
            self.worker.running = False
            self.worker.wait()
            self.tray.showMessage(
                "Moniteur USB",
                "Surveillance USB désactivée",
                QSystemTrayIcon.Information,
                2000
            )
    
    def tray_activated(self, reason):
        """Gère les clics sur l'icône de la barre des tâches"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_config()
    
    def handle_device_change(self, device_id, event_type):
        """Gère les changements d'état des périphériques"""
        # Afficher une notification
        event_type_fr = "connecté" if event_type == "connect" else "déconnecté"
        self.tray.showMessage(
            "Périphérique USB",
            f"{device_id} {event_type_fr}",
            QSystemTrayIcon.Information,
            2000
        )
        
        # Exécuter l'action configurée
        if device_id in self.actions and event_type in self.actions[device_id]:
            action = self.actions[device_id][event_type]
            self.worker.execute_action(action)
    
    def quit_app(self):
        """Arrête l'application"""
        self.worker.stop()
        self.app.quit()
    
    def run(self):
        """Lance l'application"""
        self.worker.start()
        return self.app.exec()

if __name__ == "__main__":
    monitor = USBMonitor()
    sys.exit(monitor.run())
