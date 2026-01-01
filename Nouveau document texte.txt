@echo off
cd /d "%~dp0"

REM -----------------------------
REM Lancer le scraping
REM -----------------------------
echo 🚀 Lancement du script scrap_classement.py
python scrap_classement.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors du scraping, arrêt du batch
    pause
    exit /b %ERRORLEVEL%
)

REM -----------------------------
REM Lancer la génération du site
REM -----------------------------
echo 🚀 Lancement du script generate_site.py
python generate_site.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors de la génération du site, arrêt du batch
    pause
    exit /b %ERRORLEVEL%
)

REM -----------------------------
REM Lancer le push vers GitHub
REM -----------------------------
echo 🚀 Lancement du script push_to_github.py
python push_to_github.py
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Erreur lors du push, vérifiez git
    pause
    exit /b %ERRORLEVEL%
)

echo ✅ Tous les scripts ont été exécutés avec succès
pause