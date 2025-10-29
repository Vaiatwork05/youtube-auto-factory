# scripts/disable_youtube_uploader.py
import re
import os
import shutil # Utilisé pour une gestion de sauvegarde plus sûre
import sys
from typing import Optional

# Chemin relatif du script d'exécution
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Chemin absolu du fichier cible
TARGET_FILE_PATH = os.path.join(SCRIPT_DIR, '..', 'content_factory', 'auto_content_engine.py')
BACKUP_FILE_PATH = f'{TARGET_FILE_PATH}.bak'

# --- EXPRESSIONS RÉGULIÈRES AMÉLIORÉES ---

# 1. Capture l'importation de YouTubeUploader, y compris les espaces avant l'instruction
#    Rend l'importation résistante aux changements d'espacement.
IMPORT_PATTERN = re.compile(
    r'^(\s*from\s+youtube_uploader\s+import\s+YouTubeUploader\s*)$', 
    re.MULTILINE
)

# 2. Capture l'appel à la fonction d'upload (même si elle est commentée)
#    Cible l'appel dans la fonction handle_upload que nous avons optimisée
UPLOAD_CALL_PATTERN = re.compile(
    r'(\s*uploader\.upload_video\s*\([^#\n]+\))', # Capture l'appel uploader.upload_video(...)
    re.MULTILINE
)


def disable_youtube_uploader(target_file: str = TARGET_FILE_PATH):
    """
    Désactive l'appel à YouTubeUploader() et son import dans le fichier cible.
    Utilise des expressions régulières robustes.
    """
    
    if not os.path.exists(target_file):
        print(f"❌ Erreur critique : Fichier cible non trouvé : {target_file}")
        sys.exit(1) # Fait échouer l'étape du workflow
        
    print(f"⚙️ Tentative de désactivation dans {os.path.basename(target_file)}...")

    try:
        # Lecture du contenu
        with open(target_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Création d'une sauvegarde sécurisée
        shutil.copyfile(target_file, BACKUP_FILE_PATH)
        print(f"Sauvegarde créée: {os.path.basename(BACKUP_FILE_PATH)}")

        new_content = content
        
        # --- 1. Remplacement de l'IMPORT ---
        # Remplace l'import par le même import précédé d'un '# '
        new_content, count_import = IMPORT_PATTERN.subn(
            r'# \1 # Désactivé via script',
            new_content
        )
        
        # --- 2. Remplacement de l'APPEL À L'UPLOAD ---
        # Cible l'appel et le met en commentaire, en s'assurant qu'il n'est pas déjà commenté
        new_content, count_call = UPLOAD_CALL_PATTERN.subn(
            r'# \1 # Désactivé',
            new_content
        )
        
        # Vérification si des changements ont été appliqués
        if count_import == 0 and count_call == 0:
            print("Aucune modification nécessaire ou les lignes étaient déjà commentées.")
            # Supprimer la sauvegarde inutile si rien n'a changé
            os.remove(BACKUP_FILE_PATH)
            return

        # Écriture du nouveau contenu
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Succès : {count_import} import(s) et {count_call} appel(s) désactivé(s).")
        # Suppression de la sauvegarde après succès
        os.remove(BACKUP_FILE_PATH)
        

    except Exception as e:
        print(f"❌ Échec de la modification du fichier: {e}")
        traceback_info = traceback.format_exc()
        print(traceback_info)
        
        # Rétablissement de la sauvegarde
        if os.path.exists(BACKUP_FILE_PATH):
            shutil.move(BACKUP_FILE_PATH, target_file)
            print("Restauration du fichier original réussie.")
        
        sys.exit(1) # Fait échouer l'étape du workflow

if __name__ == "__main__":
    import traceback
    disable_youtube_uploader()

