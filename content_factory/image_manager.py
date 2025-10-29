# content_factory/image_manager.py

import os
import sys
import time
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Imports des modules du projet
from content_factory.utils import clean_filename, safe_path_join, ensure_directory
from content_factory.config_loader import ConfigLoader 
from PIL import Image # Nécessaire pour le redimensionnement

# --- CONSTANTES ---
# Utilisation de l'API Unsplash par défaut
UNSPLASH_BASE_URL = "https://api.unsplash.com/search/photos"

class ImageManager:
    """
    Gère l'acquisition, le téléchargement et le cache des images.
    Utilise l'API Unsplash avec un système de cache local pour optimiser les appels.
    """
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.image_config = self.config['IMAGE_MANAGER']
        self.paths = self.config['PATHS']

        # Paramètres Unsplash
        self.api_key: str = self.config['SECRETS'].get('UNSPLASH_API_KEY', None)
        
        # Chemins et paramètres de gestion
        self.download_dir: str = safe_path_join(self.paths['OUTPUT_ROOT'], self.paths['IMAGE_DIR'])
        self.cache_enabled: bool = self.image_config.get('CACHE_IMAGES', True)
        self.cleanup_enabled: bool = self.image_config.get('CLEANUP_OLD_IMAGES', True)
        self.max_images_to_keep: int = self.image_config.get('MAX_IMAGES_TO_KEEP', 50)
        
        # Paramètres de redimensionnement (synchronisés avec VideoCreator)
        self.target_resolution: List[int] = self.config['VIDEO_CREATOR'].get('RESOLUTION', [1280, 720])
        
        if not self.api_key:
            print("❌ ERREUR: UNSPLASH_API_KEY non configurée. La recherche d'images échouera.")
        
        ensure_directory(self.download_dir)

    def get_images_for_content(self, content_data: Dict[str, Any], num_images: int) -> List[str]:
        """
        Trouve les images pour un contenu donné, en utilisant le cache si possible.
        """
        if not self.api_key:
            return []

        images: List[str] = []
        keywords: List[str] = content_data.get('keywords', [])
        
        print(f"\n🖼️ Recherche d'images pour {len(keywords)} mots-clés (max {num_images} images)...")

        for keyword in keywords:
            if len(images) >= num_images:
                break
                
            keyword = keyword.strip()
            
            # 1. Tenter le cache
            cached_path = self._get_from_cache(keyword)
            if cached_path:
                images.append(cached_path)
                print(f"   Cache HIT: '{keyword}' -> {os.path.basename(cached_path)}")
                continue

            # 2. Tenter l'API (si le cache a échoué)
            image_path = self._fetch_and_download_image(keyword)
            if image_path:
                images.append(image_path)
                print(f"   API SUCCESS: '{keyword}' -> {os.path.basename(image_path)}")
            else:
                print(f"   API FAILED: '{keyword}' n'a retourné aucune image.")

        # Nettoyage à la fin du processus si activé
        if self.cleanup_enabled:
            self._cleanup_old_files()

        # Retourne les images trouvées (peut être moins que num_images)
        return images[:num_images]

    # --- Gestion du Cache ---

    def _get_cache_path(self, keyword: str) -> str:
        """Retourne un nom de fichier standardisé pour le cache."""
        clean_kw = clean_filename(keyword)[:30]
        return safe_path_join(self.download_dir, f"cache_{clean_kw}.jpg")

    def _get_from_cache(self, keyword: str) -> Optional[str]:
        """Vérifie si une image existe déjà pour ce mot-clé."""
        if not self.cache_enabled:
            return None
            
        cache_path = self._get_cache_path(keyword)
        
        if os.path.exists(cache_path):
            # Mettre à jour la date d'accès pour le nettoyage futur
            os.utime(cache_path, None) 
            return cache_path
            
        return None

    def _save_to_cache(self, keyword: str, image_content: bytes) -> Optional[str]:
        """Sauvegarde le contenu d'une image téléchargée sur le disque."""
        cache_path = self._get_cache_path(keyword)
        try:
            # 1. Sauvegarde brute
            with open(cache_path, 'wb') as f:
                f.write(image_content)
                
            # 2. Redimensionnement (pour accélérer l'assemblage vidéo)
            self._resize_and_save_image(cache_path, self.target_resolution)
            
            return cache_path
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde/redimensionnement du cache: {e}")
            return None

    # --- Requête API ---

    def _fetch_and_download_image(self, keyword: str) -> Optional[str]:
        """Appelle l'API Unsplash, télécharge et met en cache l'image."""
        
        headers = {
            "Authorization": f"Client-ID {self.api_key}",
            "Accept-Version": "v1"
        }
        params = {
            "query": keyword,
            "orientation": "landscape", # Format 16:9
            "per_page": 1, # On ne prend que la meilleure image
        }
        
        try:
            response = requests.get(UNSPLASH_BASE_URL, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data or not data.get('results'):
                return None

            # On prend la première image (la plus pertinente)
            image_info = data['results'][0]
            # Utilisation du lien 'regular' pour une bonne résolution
            download_url = image_info['urls']['regular'] 
            
            # Téléchargement effectif de l'image
            image_response = requests.get(download_url, stream=True, timeout=15)
            image_response.raise_for_status()
            
            # Mise en cache et redimensionnement
            return self._save_to_cache(keyword, image_response.content)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur API/Téléchargement Unsplash pour '{keyword}': {e}")
            return None

    # --- Support PIL (Redimensionnement) ---

    def _resize_and_save_image(self, path: str, target_size: List[int]):
        """Redimensionne et ré-enregistre l'image pour optimiser l'assemblage vidéo."""
        
        try:
            target_width, target_height = target_size[0], target_size[1]
            img = Image.open(path)
            
            # Calculer le ratio pour que l'image couvre l'espace 16:9 (cover)
            original_width, original_height = img.size
            target_ratio = target_width / target_height
            original_ratio = original_width / original_height
            
            if original_ratio > target_ratio:
                # L'original est plus large -> rogner les côtés
                new_width = int(target_ratio * original_height)
                left = (original_width - new_width) // 2
                right = left + new_width
                img = img.crop((left, 0, right, original_height))
            elif original_ratio < target_ratio:
                # L'original est plus haut -> rogner le haut et le bas
                new_height = int(original_width / target_ratio)
                top = (original_height - new_height) // 2
                bottom = top + new_height
                img = img.crop((0, top, original_width, bottom))

            # Redimensionnement final à la résolution cible
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            
            # Ré-enregistrement en JPG optimisé
            img.save(path, format='JPEG', quality=85)
            
        except Exception as e:
            print(f"⚠️ Échec du redimensionnement PIL pour {path}: {e}")
            # Laisser le fichier original (non redimensionné)
            pass

    # --- Nettoyage ---

    def _cleanup_old_files(self):
        """Supprime les fichiers les moins récemment accédés si la limite est dépassée."""
        if not self.cleanup_enabled:
            return

        all_files = [
            safe_path_join(self.download_dir, f)
            for f in os.listdir(self.download_dir)
            if os.path.isfile(safe_path_join(self.download_dir, f))
        ]
        
        if len(all_files) <= self.max_images_to_keep:
            return

        # Trier par temps d'accès (plus vieux en premier)
        all_files.sort(key=os.path.getatime)
        
        # Calculer le nombre de fichiers à supprimer
        files_to_delete = len(all_files) - self.max_images_to_keep
        
        if files_to_delete > 0:
            print(f"🧹 Nettoyage: Suppression de {files_to_delete} anciens fichiers du cache...")
            for i in range(files_to_delete):
                try:
                    os.remove(all_files[i])
                except Exception as e:
                    print(f"⚠️ Erreur lors de la suppression de {os.path.basename(all_files[i])}: {e}")
        
# --- Fonction d'Export et de Test ---

def get_images(content_data: Dict[str, Any], num_images: int) -> List[str]:
    """Fonction d'export simple."""
    manager = ImageManager()
    return manager.get_images_for_content(content_data, num_images)

if __name__ == "__main__":
    print("🧪 Test ImageManager (Nécessite une clé UNSPLASH_API_KEY valide dans la config)...")
    
    # ⚠️ IMPORTANT: Pour le test, la clé Unsplash doit être dans votre config.yaml ou .env
    
    try:
        manager = ImageManager()
        
        test_data = {
            'title': 'Test de la ville de Paris',
            'script': 'La tour Eiffel et la Seine en plein soleil.',
            'keywords': ['Tour Eiffel', 'Paris', 'Seine', 'Architecture']
        }
        
        num_images_needed = 4
        results = manager.get_images_for_content(test_data, num_images_needed)
        
        print("\n=== RAPPORT DE TEST IMAGE ===")
        print(f"Résultats obtenus: {len(results)}/{num_images_needed}")
        
        if len(results) == num_images_needed:
            print("✅ Succès: Toutes les images ont été trouvées et mises en cache/téléchargées.")
            print("Liste des fichiers:")
            for r in results:
                 print(f" - {os.path.basename(r)}")
            sys.exit(0)
        else:
            print("❌ Échec: Le nombre d'images trouvées n'est pas le nombre attendu.")
            print("Vérifiez votre clé API et la connexion.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Erreur critique lors du test: {e}")
        sys.exit(1)
