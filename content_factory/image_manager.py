# content_factory/image_manager.py
import os
import requests
from dotenv import load_dotenv

class ImageManager:
    def __init__(self, download_folder="downloaded_images"):
        # ⭐ CHARGER LE .env ⭐
        load_dotenv()
        
        self.download_folder = os.getenv('IMAGE_DOWNLOAD_FOLDER', download_folder)
        self.unsplash_key = os.getenv('UNSPLASH_API_KEY')
        self.max_images_to_keep = int(os.getenv('MAX_IMAGES_TO_KEEP', 50))
        self.setup_directories()
    
    def setup_directories(self):
        """Crée les dossiers nécessaires"""
        os.makedirs(self.download_folder, exist_ok=True)
        os.makedirs('output/audio', exist_ok=True)
        os.makedirs('output/videos', exist_ok=True)
    
    def check_unsplash_config(self):
        """Vérifie la configuration Unsplash"""
        if not self.unsplash_key or self.unsplash_key == 'votre_clé_unsplash_ici':
            print("⚠️ Mode placeholder - Clé Unsplash non configurée")
            return False
        return True
    
    # ... le reste de votre code ...
