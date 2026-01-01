import os
import subprocess

# =====================
# CONFIG
# =====================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)  # S'assurer qu'on est dans le bon dossier

GIT_BRANCH = "main"  # ta branche actuelle
COMMIT_MESSAGE = "Mise à jour du classement BloodWars"

# =====================
# FONCTIONS
# =====================
def run(cmd):
    """Exécute une commande shell et affiche la sortie"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode

# =====================
# AJOUTER LES MODIFICATIONS
# =====================
print("📌 Ajout des fichiers modifiés...")
run("git add .")

# =====================
# Vérifier s'il y a quelque chose à commit
# =====================
status_output = subprocess.getoutput("git status --porcelain")
if not status_output.strip():
    print("ℹ️ Aucun changement à pousser.")
else:
    # =====================
    # COMMIT
    # =====================
    print("📦 Commit des modifications...")
    run(f'git commit -m "{COMMIT_MESSAGE}"')

    # =====================
    # PUSH
    # =====================
    print(f"🚀 Push vers la branche {GIT_BRANCH}...")
    run(f"git push origin {GIT_BRANCH}")

    print("✅ Push terminé, le site devrait être à jour sur GitHub Pages !")