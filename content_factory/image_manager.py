# content_factory/image_manager.py (AVEC VOTRE VRAIE CLÉ)

import os
import time
import requests
import random
from typing import Dict, Any, List, Optional
from PIL import Image
from content_factory.utils import clean_filename, safe_path_join, ensure_directory

class ImageManager:
    """Gestionnaire d'images avec votre VRAIE clé Unsplash."""
    
    def __init__(self):
        # 🔥 VOTRE VRAIE CLÉ
        self.api_key = "ZM4rxcqbMoqb3qfda_dy0oTfLspiEsXsST55Egoh_j8"
        self.download_dir = safe_path_join("output", "images")
        ensure_directory(self.download_dir)
        
        # Test de la clé
        self.unsplash_actif = self._tester_votre_cle()
        print(f"🔑 Votre clé Unsplash: {'✅ ACTIVE' if self.unsplash_actif else '❌ INACTIVE'}")

    def _tester_votre_cle(self) -> bool:
        """Test de VOTRE clé spécifique."""
        try:
            headers = {"Authorization": f"Client-ID {self.api_key}"}
            response = requests.get(
                "https://api.unsplash.com/search/photos?query=test&per_page=1",
                headers=headers,
                timeout=10
            )
            
            print(f"📊 Statut API: {response.status_code}")
            
            if response.status_code == 200:
                return True
            elif response.status_code == 401:
                print("❌ Clé API invalide - Vérifiez votre clé Unsplash")
                return False
            elif response.status_code == 403:
                print("❌ Limite d'API atteinte - Attendez 1 heure")
                return False
            else:
                print(f"❌ Erreur inconnue: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur connexion: {e}")
            return False

    def get_images_for_content(self, content_data: Dict[str, Any], num_images: int = 3) -> List[str]:
        """Récupère des images avec votre clé."""
        
        images = []
        
        if self.unsplash_actif:
            print("🖼️ Recherche d'images sur Unsplash...")
            keywords = self._extraire_mots_cles(content_data)
            
            for keyword in keywords:
                if len(images) >= num_images:
                    break
                    
                image_path = self._telecharger_image(keyword)
                if image_path:
                    images.append(image_path)
                    print(f"   ✅ '{keyword}'")
                else:
                    print(f"   ❌ '{keyword}'")
        
        # Fallback si pas assez d'images
        if len(images) < num_images:
            manquant = num_images - len(images)
            print(f"🎨 Création de {manquant} image(s) fallback")
            images_fallback = self._creer_fallback(content_data, manquant)
            images.extend(images_fallback)
        
        print(f"📷 Total: {len(images)} images prêtes")
        return images

    def _telecharger_image(self, keyword: str) -> Optional[str]:
        """Télécharge une image avec VOTRE clé."""
        try:
            headers = {"Authorization": f"Client-ID {self.api_key}"}
            params = {
                "query": keyword,
                "orientation": "portrait",  # Format vertical
                "per_page": 1
            }
            
            response = requests.get(
                "https://api.unsplash.com/search/photos",
                headers=headers,
                params=params,
                timeout=15
            )
            
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
                for chunk in image_response.iter_content(8192):
                    f.write(chunk)
            
            return filepath
            
        except Exception as e:
            print(f"   ❌ Erreur téléchargement: {e}")
            return None

    def _creer_fallback(self, content_data: Dict[str, Any], num_images: int) -> List[str]:
        """Images de fallback colorées."""
        images = []
        title = content_data.get('title', 'YouTube Shorts')
        
        couleurs = [
            (70, 130, 180), (34, 139, 34), (255, 140, 0),
            (147, 112, 219), (220, 20, 60), (30, 144, 255)
        ]
        
        for i in range(num_images):
            couleur = random.choice(couleurs)
            image = Image.new('RGB', (1080, 1920), color=couleur)
            
            filename = f"fallback_{clean_filename(title)}_{i}.jpg"
            filepath = safe_path_join(self.download_dir, filename)
            image.save(filepath, 'JPEG', quality=90)
            
            images.append(filepath)
        
        return images

    def _extraire_mots_cles(self, content_data: Dict[str, Any]) -> List[str]:
        """Extrait les mots-clés."""
        keywords = content_data.get('keywords', [])
        title = content_data.get('title', '')
        
        # Mots du titre
        if title:
            mots = [mot for mot in title.split() if len(mot) > 3]
            keywords.extend(mots)
        
        return list(set(keywords))[:8]

def get_images(content_data: Dict[str, Any], num_images: int = 3) -> List[str]:
    """Fonction d'export."""
    try:
        manager = ImageManager()
        return manager.get_images_for_content(content_data, num_images)
    except Exception as e:
        print(f"❌ Erreur ImageManager: {e}")
        return []

# Test spécifique
if __name__ == "__main__":
    print("🧪 TEST AVEC VOTRE CLÉ UNSPLASH...")
    
    manager = ImageManager()
    
    if manager.unsplash_actif:
        print("🎉 Votre clé fonctionne ! Test de téléchargement...")
        
        # Test avec un mot-clé simple
        test_path = manager._telecharger_image("money")
        if test_path:
            print(f"✅ SUCCÈS - Image téléchargée: {test_path}")
        else:
            print("❌ Échec téléchargement test")
    else:
        print("😞 Votre clé ne fonctionne pas")
