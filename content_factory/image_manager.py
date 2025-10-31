# content_factory/image_manager.py (VERSION .env)

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
    """Gestionnaire d'images avec support .env"""
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.paths = self.config.get('PATHS', {})
        
        # 🔥 PRIORITÉ : .env > config.yaml > clé en dur
        self.api_key = self._load_unsplash_key()
        
        # Chemins
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        self.download_dir = safe_path_join(output_root, 'images')
        ensure_directory(self.download_dir)
        
        print(f"🔑 Clé Unsplash: {'✅ Configurée' if self.api_key else '❌ Manquante'}")
        
    def _load_unsplash_key(self) -> Optional[str]:
        """Charge la clé Unsplash avec priorité .env"""
        # 1. .env file (priorité maximale)
        env_key = os.getenv('UNSPLASH_API_KEY')
        if env_key:
            print("✅ Clé chargée depuis .env")
            return env_key.strip()
        
        # 2. config.yaml
        config_key = self.config.get('SECRETS', {}).get('UNSPLASH_API_KEY')
        if config_key:
            print("✅ Clé chargée depuis config.yaml")
            return config_key.strip()
        
        # 3. Clé en dur (fallback)
        hardcoded_key = "ZM4rxcqbMoqb3qfda_dy0oTfLspiEsXsST"
        if hardcoded_key:
            print("✅ Clé intégrée utilisée")
            return hardcoded_key.strip()
            
        print("❌ Aucune clé Unsplash trouvée")
        return None

    def get_images_for_content(self, content_data: Dict[str, Any], num_images: int = 3) -> List[str]:
        """Récupère des images pour le contenu."""
        
        if not self.api_key:
            print("🔑 Mode fallback activé - Pas de clé Unsplash")
            return self._generate_fallback_images(content_data, num_images)
        
        # Test rapide de la clé
        if not self._test_unsplash_connection():
            print("🔑 Clé Unsplash invalide - Fallback activé")
            return self._generate_fallback_images(content_data, num_images)
        
        keywords = self._get_search_keywords(content_data)
        print(f"🖼️ Recherche de {num_images} images...")
        
        images = []
        for keyword in keywords[:8]:  # Limite les requêtes
            if len(images) >= num_images:
                break
                
            image_path = self._download_unsplash_image(keyword)
            if image_path:
                images.append(image_path)
                print(f"   ✅ {keyword}")
        
        # Compléter avec fallback si nécessaire
        if len(images) < num_images:
            needed = num_images - len(images)
            fallbacks = self._generate_fallback_images(content_data, needed)
            images.extend(fallbacks)
            print(f"   🔄 {needed} image(s) fallback ajoutée(s)")
            
        return images

    def _test_unsplash_connection(self) -> bool:
        """Teste la connexion Unsplash."""
        try:
            headers = {"Authorization": f"Client-ID {self.api_key}"}
            response = requests.get(
                f"{UNSPLASH_BASE_URL}?query=test&per_page=1", 
                headers=headers, 
                timeout=10
            )
            return response.status_code == 200
        except:
            return False

    def _get_search_keywords(self, content_data: Dict[str, Any]) -> List[str]:
        """Génère des mots-clés pertinents."""
        keywords = content_data.get('keywords', [])
        title = content_data.get('title', '')
        
        # Extraire les mots importants du titre
        if title:
            # Nettoyer le titre
            clean_title = re.sub(r'[^\w\s]', ' ', title)
            title_keywords = [word for word in clean_title.split() if len(word) > 3]
            keywords.extend(title_keywords)
        
        # Catégorie
        category = content_data.get('category', '')
        if category:
            keywords.append(category)
        
        # Dédupliquer et mélanger
        unique_keywords = list(set([kw.lower() for kw in keywords if kw]))
        random.shuffle(unique_keywords)
        
        return unique_keywords[:15]

    def _download_unsplash_image(self, keyword: str) -> Optional[str]:
        """Télécharge une image depuis Unsplash."""
        try:
            headers = {"Authorization": f"Client-ID {self.api_key}"}
            params = {
                "query": keyword,
                "orientation": "portrait",  # Format vertical pour Shorts
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
            
            # Sauvegarder avec nom unique
            timestamp = int(time.time())
            filename = f"unsplash_{clean_filename(keyword)}_{timestamp}.jpg"
            filepath = safe_path_join(self.download_dir, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in image_response.iter_content(8192):
                    f.write(chunk)
            
            return filepath
            
        except Exception as e:
            print(f"   ❌ Erreur téléchargement {keyword}: {e}")
            return None

    def _generate_fallback_images(self, content_data: Dict[str, Any], num_images: int) -> List[str]:
        """Génère des images de fallback colorées."""
        images = []
        title = content_data.get('title', 'YouTube Shorts')
        
        # Couleurs vibrantes pour Shorts
        colors = [
            (70, 130, 180),    # Bleu royal
            (34, 139, 34),     # Vert forêt  
            (255, 140, 0),     # Orange vif
            (147, 112, 219),   # Violet
            (220, 20, 60)      # Rouge
        ]
        
        for i in range(num_images):
            color = colors[i % len(colors)]
            
            # Créer image colorée
            img = Image.new('RGB', (1080, 1920), color=color)
            
            filename = f"fallback_{clean_filename(title)}_{i}.jpg"
            filepath = safe_path_join(self.download_dir, filename)
            img.save(filepath, 'JPEG', quality=90)
            
            images.append(filepath)
        
        return images

def get_images(content_data: Dict[str, Any], num_images: int = 3) -> List[str]:
    """Fonction d'export principale."""
    try:
        manager = ImageManager()
        return manager.get_images_for_content(content_data, num_images)
    except Exception as e:
        print(f"❌ Erreur ImageManager: {e}")
        # Fallback minimal
        try:
            manager = ImageManager()
            return manager._generate_fallback_images(content_data, num_images)
        except:
            return []

# Test
if __name__ == "__main__":
    print("🧪 Test ImageManager avec .env...")
    
    test_content = {
        'title': 'TOP 10 SECRETS CHOQUANTS',
        'keywords': ['secret', 'choc', 'révélation'],
        'category': 'psychologie'
    }
    
    images = get_images(test_content, 2)
    print(f"📷 Résultat: {len(images)} images")
