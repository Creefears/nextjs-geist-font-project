# Script PowerShell pour télécharger et installer le Moniteur USB
Write-Host "Installation du Moniteur USB..." -ForegroundColor Green

# Vérifier si Python est installé
try {
    $pythonVersion = python --version
    Write-Host "Python détecté : $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "Python n'est pas installé. Veuillez installer Python 3.7+ depuis https://www.python.org/downloads/" -ForegroundColor Red
    Exit 1
}

# Créer le dossier d'installation s'il n'existe pas
$installDir = "$env:USERPROFILE\UsbMonitor"
if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir | Out-Null
    Write-Host "Dossier d'installation créé : $installDir" -ForegroundColor Green
}

# Se déplacer dans le dossier d'installation
Set-Location $installDir

# Extraire l'archive si elle existe
$zipFile = Get-ChildItem -Filter "usb_monitor_*.zip" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if ($zipFile) {
    Write-Host "Extraction de l'archive..." -ForegroundColor Green
    Expand-Archive -Path $zipFile.FullName -DestinationPath . -Force
}

# Installer les dépendances
Write-Host "Installation des dépendances Python..." -ForegroundColor Green
python -m pip install --upgrade pip
pip install -r requirements.txt

# Créer le dossier logs
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "Dossier logs créé" -ForegroundColor Green
}

# Créer un raccourci sur le bureau
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("$env:USERPROFILE\Desktop\Moniteur USB.lnk")
$Shortcut.TargetPath = "pythonw.exe"
$Shortcut.Arguments = "usb_monitor.py"
$Shortcut.WorkingDirectory = $installDir
$Shortcut.Save()
Write-Host "Raccourci créé sur le bureau" -ForegroundColor Green

# Créer un raccourci dans le menu Démarrer
$startupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$Shortcut = $WshShell.CreateShortcut("$startupFolder\Moniteur USB.lnk")
$Shortcut.TargetPath = "pythonw.exe"
$Shortcut.Arguments = "usb_monitor.py"
$Shortcut.WorkingDirectory = $installDir
$Shortcut.Save()
Write-Host "Raccourci créé dans le dossier Démarrage" -ForegroundColor Green

Write-Host "`nInstallation terminée !" -ForegroundColor Green
Write-Host "Vous pouvez maintenant :" -ForegroundColor Yellow
Write-Host "1. Lancer l'application depuis le raccourci sur le bureau" -ForegroundColor Yellow
Write-Host "2. L'application démarrera automatiquement au prochain démarrage de Windows" -ForegroundColor Yellow
Write-Host "`nAppuyez sur une touche pour fermer..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
