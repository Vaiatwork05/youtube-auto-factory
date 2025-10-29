# scripts/disable_youtube_uploader.py

import re
import os

FILE_PATH = 'content_factory/auto_content_engine.py'
BACKUP_PATH = f'{FILE_PATH}.bak'

def disable_youtube_uploader():
    """Désactive l'appel à YouTubeUploader() dans le fichier cible, ainsi que son import."""
    
    if not os.path.exists(FILE_PATH):
        print(f"Erreur : Le fichier cible n'existe pas : {FILE_PATH}")
        return

    try:
        # Lecture du contenu
        with open(FILE_PATH, 'r') as f:
            content = f.read()

        # Création d'une sauvegarde
        with open(BACKUP_PATH, 'w') as f_bak:
            f_bak.write(content)
            
        print(f"Sauvegarde créée : {BACKUP_PATH}")

        # 1. Remplacement : mettre en commentaire l'appel à YouTubeUploader()
        new_content = re.sub(
            r'YouTubeUploader\(\)', 
            '# YouTubeUploader()  # Désactivé temporairement', 
            content
        )
        
        # 2. Remplacement : Désactiver l'import s'il est présent
        new_content = re.sub(
            r'^from youtube_uploader import YouTubeUploader',
            '# from youtube_uploader import YouTubeUploader  # Désactivé',
            new_content,
            flags=re.MULTILINE
        )

        if new_content == content:
            print("Aucune modification nécessaire.")
            return

        # Écriture du nouveau contenu
        with open(FILE_PATH, 'w') as f:
            f.write(new_content)
        
        print(f"✅ Succès : YouTube Uploader désactivé dans {FILE_PATH}")

    except Exception as e:
        print(f"⚠️ Une erreur s'est produite lors de la modification du fichier : {e}")
        # Rétablir la sauvegarde en cas d'échec
        if os.path.exists(BACKUP_PATH):
            os.rename(BACKUP_PATH, FILE_PATH)
            print("Tentative de restauration du fichier original.")

if __name__ == "__main__":
    disable_youtube_uploader()
