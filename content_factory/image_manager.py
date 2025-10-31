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
from PIL import Image

# --- CONSTANTES ---
UNSPLASH_BASE_URL = "https://api.unsplash.com/search/photos"

class ImageManager:
    """
    Gère l'acquisition, le téléchargement et le cache des images.
    Version corrigée avec gestion robuste de la configuration.
    """
    def __init__(self):
        self.config = ConfigLoader().get_config()
        
        # CONFIGURATION ROBUSTE avec valeurs par défaut
        self.image_config = self.config.get('IMAGE_MANAGER', {})
        self.paths = self.config.get('PATHS', {})
        
        # Paramètres Unsplash - avec fallback
        self.api_key = os.getenv('UNSPLASH_API_KEY') or self.config.get('SECRETS', {}).get('UNSPLASH_API_KEY')
        
        # Chemins et paramètres avec valeurs par défaut
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        image_dir = self.paths.get('IMAGE_DIR', 'images')
        self.download_dir = safe_path_join(output_root, image_dir)
        
        self.cache_enabled = self.image_config.get('CACHE_IMAGES', True)
        self.cleanup_enabled = self.image_config.get('CLEANUP_OLD_IMAGES', False)  # Désactivé par défaut
        self.max_images_to_keep = self.image_config.get('MAX_IMAGES_TO_KEEP', 50)
        
        # Résolution cible avec fallback
        video_config = self.config.get('VIDEO_CREATOR', {})
        self.target_resolution = video_config.get('RESOLUTION', [1280, 720])
        
        if not self.api_key:
            print("⚠️ AVERTISSEMENT: UNSPLASH_API_KEY non configurée. Utilisation du mode fallback.")
        
        ensure_directory(self.download_dir)

    def get_images_for_content(self, content_data: Dict[str, Any], num_images: int) -> List[str]:
        """
        Trouve les images pour un contenu donné, avec fallback si API échoue.
        """
        # Si pas de clé API, retourner liste vide pour déclencher le fallback
        if not self.api_key:
            print("🔑 Pas de clé Unsplash - Mode fallback activé")
            return []

        images: List[str] = []
        keywords: List[str] = content_data.get('keywords', [])
        
        # Si pas de keywords, utiliser le titre
        if not keywords and 'title' in content_data:
            keywords = [content_data['title']]
        
        print(f"\n🖼️ Recherche d'images pour {len(keywords)} mots-clés...")

        for keyword in keywords:
            if len(images) >= num_images:
                break
                
            keyword = keyword.strip()
            if not keyword:
                continue
                
            # 1. Tenter le cache
            cached_path = self._get_from_cache(keyword)
            if cached_path:
                images.append(cached_path)
                print(f"   ✅ Cache: '{keyword}'")
                continue

            # 2. Tenter l'API
            image_path = self._fetch_and_download_image(keyword)
            if image_path:
                images.append(image_path)
                print(f"   ✅ API: '{keyword}'")
            else:
                print(f"   ❌ API échouée: '{keyword}'")

        # Nettoyage désactivé pour éviter les suppressions accidentelles
        # if self.cleanup_enabled:
        #     self._cleanup_old_files()

        return images[:num_images]

    # --- Gestion du Cache ---

    def _get_cache_path(self, keyword: str) -> str:
        """Retourne un nom de fichier standardisé pour le cache."""
        clean_kw = clean_filename(keyword)[:30]
        timestamp = int(time.time())
        return safe_path_join(self.download_dir, f"cache_{clean_kw}_{timestamp}.jpg")

    def _get_from_cache(self, keyword: str) -> Optional[str]:
        """Vérifie si une image existe déjà pour ce mot-clé."""
        if not self.cache_enabled:
            return None
            
        # Chercher dans les fichiers existants
        clean_kw = clean_filename(keyword)[:30]
        for filename in os.listdir(self.download_dir):
            if filename.startswith(f"cache_{clean_kw}") and filename.endswith('.jpg'):
                cache_path = safe_path_join(self.download_dir, filename)
                if os.path.exists(cache_path):
                    os.utime(cache_path, None) 
                    return cache_path
                    
        return None

    def _save_to_cache(self, keyword: str, image_content: bytes) -> Optional[str]:
        """Sauvegarde le contenu d'une image téléchargée sur le disque."""
        cache_path = self._get_cache_path(keyword)
        try:
            # Sauvegarde directe d'abord
            with open(cache_path, 'wb') as f:
                f.write(image_content)
                
            # Tentative de redimensionnement (optionnel)
            try:
                self._resize_and_save_image(cache_path, self.target_resolution)
            except Exception as resize_error:
                print(f"⚠️ Redimensionnement échoué, garde l'image originale: {resize_error}")
                
            return cache_path
        except Exception as e:
            print(f"❌ Erreur sauvegarde cache: {e}")
            # Nettoyer le fichier partiellement créé
            if os.path.exists(cache_path):
                os.remove(cache_path)
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
            "orientation": "landscape",
            "per_page": 1,
        }
        
        try:
            print(f"   🔍 Requête Unsplash: '{keyword}'")
            response = requests.get(UNSPLASH_BASE_URL, headers=headers, params=params, timeout=15)
            
            if response.status_code == 401:
                print(f"   ❌ Clé API Unsplash invalide")
                return None
            elif response.status_code == 403:
                print(f"   ❌ Limite d'API Unsplash atteinte")
                return None
                
            response.raise_for_status()
            data = response.json()
            
            if not data or not data.get('results'):
                print(f"   ❌ Aucun résultat pour '{keyword}'")
                return None

            # Prendre la première image
            image_info = data['results'][0]
            download_url = image_info['urls']['regular']
            
            # Téléchargement
            image_response = requests.get(download_url, stream=True, timeout=20)
            image_response.raise_for_status()
            
            return self._save_to_cache(keyword, image_response.content)
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erreur réseau: {e}")
            return None
        except Exception as e:
            print(f"   ❌ Erreur inattendue: {e}")
            return None

    # --- Support PIL (Redimensionnement) ---

    def _resize_and_save_image(self, path: str, target_size: List[int]):
        """Redimensionne et ré-enregistre l'image."""
        try:
            target_width, target_height = target_size
            img = Image.open(path)
            
            # Redimensionnement simple sans cropping
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            img.save(path, format='JPEG', quality=85)
            
        except Exception as e:
            # Si échec, l'image originale reste utilisable
            print(f"⚠️ Redimensionnement échoué: {e}")

    # --- Nettoyage (DÉSACTIVÉ pour sécurité) ---
    def _cleanup_old_files(self):
        """Désactivé pour éviter la suppression accidentelle."""
        print("🧹 Nettoyage désactivé pour sécurité")
        return

# --- Fonction d'Export ---

def get_images(content_data: Dict[str, Any], num_images: int) -> List[str]:
    """Fonction d'export simple avec gestion d'erreur."""
    try:
        manager = ImageManager()
        return manager.get_images_for_content(content_data, num_images)
    except Exception as e:
        print(f"❌ Erreur ImageManager: {e}")
        return []
