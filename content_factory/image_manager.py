# content_factory/image_manager.py (VERSION FINALE CORRIGÉE)

import os
import time
import requests
import random
import re
from typing import Dict, Any, List, Optional
from PIL import Image

from content_factory.utils import clean_filename, safe_path_join, ensure_directory
from content_factory.config_loader import ConfigLoader 

UNSPLASH_BASE_URL = "https://api.unsplash.com/search/photos"

class ImageManager:
    """Gestionnaire d'images avec clé Unsplash corrigée."""
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.paths = self.config.get('PATHS', {})
        
        # 🔥 CORRECTION : Utilisez juste cette clé
        self.api_key = "ZM4rxcqbMoqb3qfda_dy0oTfLspiEsXsST"
        
        # Chemins
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        self.download_dir = safe_path_join(output_root, 'images')
        ensure_directory(self.download_dir)
        
        # Test immédiat de la clé
        self._test_unsplash_key()
        
    def _test_unsplash_key(self):
        """Teste la clé Unsplash au démarrage."""
        print("🔑 Test de la clé Unsplash...")
        
        if not self.api_key:
            print("❌ Aucune clé Unsplash configurée")
            return
            
        try:
            headers = {"Authorization": f"Client-ID {self.api_key}"}
            params = {"query": "test", "per_page": 1}
            
            response = requests.get(UNSPLASH_BASE_URL, headers=headers, params=params, timeout=10)
            
            if response.status_code == 200:
                print("✅ Clé Unsplash VALIDE - Connexion réussie")
            elif response.status_code == 401:
                print("❌ Clé Unsplash INVALIDE - Erreur 401")
            else:
                print(f"⚠️ Statut Unsplash: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Erreur test Unsplash: {e}")

    def get_images_for_content(self, content_data: Dict[str, Any], num_images: int = 3) -> List[str]:
        """Récupère des images avec la clé corrigée."""
        
        if not self.api_key:
            print("🔑 Mode fallback - Pas de clé Unsplash")
            return self._generate_fallback_images(content_data, num_images)
        
        keywords = self._get_search_keywords(content_data)
        print(f"🖼️ Recherche de {num_images} images avec clé Unsplash...")
        
        images = []
        for keyword in keywords[:10]:  # Limiter les recherches
            if len(images) >= num_images:
                break
                
            image_path = self._download_unsplash_image(keyword)
            if image_path:
                images.append(image_path)
                print(f"   ✅ {keyword}")
            else:
                print(f"   ❌ {keyword}")
        
        # Fallback si pas assez d'images
        if len(images) < num_images:
            fallbacks = self._generate_fallback_images(content_data, num_images - len(images))
            images.extend(fallbacks)
            
        return images

    def _get_search_keywords(self, content_data: Dict[str, Any]) -> List[str]:
        """Génère des mots-clés de recherche."""
        keywords = content_data.get('keywords', [])
        title = content_data.get('title', '')
        
        # Extraire des mots du titre
        if title:
            title_words = re.findall(r'\b\w{4,}\b', title.lower())
            keywords.extend(title_words)
        
        # Dédupliquer
        return list(set(keywords))[:15]

    def _download_unsplash_image(self, keyword: str) -> Optional[str]:
        """Télécharge une image depuis Unsplash."""
        try:
            headers = {"Authorization": f"Client-ID {self.api_key}"}
            params = {
                "query": keyword,
                "orientation": "portrait",  # Format vertical
                "per_page": 1
            }
            
            response = requests.get(UNSPLASH_BASE_URL, headers=headers, params=params, timeout=15)
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            if not data.get('results'):
                return None
            
            # Télécharger l'image
            image_url = data['results'][0]['urls']['regular']
            image_response = requests.get(image_url, stream=True, timeout=20)
            image_response.raise_for_status()
            
            # Sauvegarder
            filename = f"unsplash_{clean_filename(keyword)}_{int(time.time())}.jpg"
            filepath = safe_path_join(self.download_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in image_response.iter_content(1024):
                    f.write(chunk)
            
            return filepath
            
        except Exception:
            return None

    def _generate_fallback_images(self, content_data: Dict[str, Any], num_images: int) -> List[str]:
        """Génère des images de fallback colorées."""
        images = []
        title = content_data.get('title', 'YouTube Shorts')
        
        colors = [(70, 130, 180), (34, 139, 34), (255, 140, 0)]
        
        for i in range(num_images):
            color = colors[i % len(colors)]
            img = Image.new('RGB', (1080, 1920), color=color)
            
            filename = f"fallback_{clean_filename(title)}_{i}.jpg"
            filepath = safe_path_join(self.download_dir, filename)
            img.save(filepath, 'JPEG', quality=90)
            
            images.append(filepath)
            print(f"   🎨 Fallback {i+1}")
        
        return images

def get_images(content_data: Dict[str, Any], num_images: int = 3) -> List[str]:
    """Fonction d'export."""
    try:
        manager = ImageManager()
        return manager.get_images_for_content(content_data, num_images)
    except Exception as e:
        print(f"❌ Erreur images: {e}")
        return []
