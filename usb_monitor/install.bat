@echo off
echo Installation du Moniteur USB...

REM Vérifie si Python est installé
python --version >nul 2>&1
if errorlevel 1 (
    echo Python n'est pas installé. Veuillez installer Python 3.x
    pause
    exit /b 1
)

REM Vérifie si pip est installé
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip n'est pas installé. Installation de pip...
    python -m ensurepip --default-pip
)

REM Installe les dépendances
echo Installation des dépendances...
pip install -r requirements.txt

REM Crée le dossier logs s'il n'existe pas
if not exist "logs" mkdir logs

REM Crée un raccourci dans le dossier de démarrage
echo Création du raccourci de démarrage automatique...
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $Shortcut = $WS.CreateShortcut($env:APPDATA + '\Microsoft\Windows\Start Menu\Programs\Startup\USB_Monitor.lnk'); $Shortcut.TargetPath = 'pythonw.exe'; $Shortcut.Arguments = '%~dp0usb_monitor.py'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()"

echo Installation terminée !
echo Le moniteur USB démarrera automatiquement au prochain démarrage de Windows.
echo Pour le lancer maintenant, exécutez : python usb_monitor.py
pause
