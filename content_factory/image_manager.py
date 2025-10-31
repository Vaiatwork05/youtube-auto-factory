# content_factory/image_manager.py

import os
import sys
import time
import requests
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont

# Imports des modules du projet
from content_factory.utils import clean_filename, safe_path_join, ensure_directory
from content_factory.config_loader import ConfigLoader 

# --- CONSTANTES ---
UNSPLASH_BASE_URL = "https://api.unsplash.com/search/photos"

class ImageManager:
    """
    Gère l'acquisition, le téléchargement et le cache des images.
    Optimisé pour fonctionner avec auto_content_engine.py
    """
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        
        # Configuration
        self.image_config = self.config.get('IMAGE_MANAGER', {})
        self.paths = self.config.get('PATHS', {})
        
        # Clé Unsplash - Priorité aux variables d'environnement
        self.api_key = self._get_unsplash_api_key()
        
        # Chemins
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        image_dir = self.paths.get('IMAGE_DIR', 'images')
        self.download_dir = safe_path_join(output_root, image_dir)
        
        # Paramètres
        self.cache_enabled = self.image_config.get('CACHE_IMAGES', True)
        self.target_resolution = self.config.get('VIDEO_CREATOR', {}).get('RESOLUTION', [1280, 720])
        
        if not self.api_key:
            print("⚠️ AVERTISSEMENT: UNSPLASH_API_KEY non configurée. Utilisation du mode fallback.")
        else:
            print(f"✅ Clé Unsplash configurée")
        
        ensure_directory(self.download_dir)

    def _get_unsplash_api_key(self) -> Optional[str]:
        """Récupère la clé API Unsplash depuis plusieurs sources"""
        # 1. Variable d'environnement (priorité)
        env_key = os.getenv('UNSPLASH_API_KEY')
        if env_key:
            return env_key
            
        # 2. Configuration du fichier
        config_key = self.config.get('SECRETS', {}).get('UNSPLASH_API_KEY')
        if config_key:
            return config_key
            
        # 3. Clé intégrée (votre clé)
        hardcoded_key = "ZM4rxcqbMoqb3qfda_dy0oTflspiEsXsST"
        return hardcoded_key

    def get_images_for_content(self, content_data: Dict[str, Any], num_images: int = 3) -> List[str]:
        """
        Trouve les images pour un contenu donné.
        Optimisé pour la structure de données de auto_content_engine.py
        """
        images: List[str] = []
        
        # Si pas de clé API, utiliser le fallback immédiatement
        if not self.api_key:
            print("🔑 Pas de clé Unsplash - Génération d'images fallback")
            return self._generate_fallback_images(content_data, num_images)

        # Générer les mots-clés de recherche optimisés
        search_keywords = self._generate_search_keywords(content_data)
        
        print(f"\n🖼️ Recherche de {num_images} images parmi {len(search_keywords)} mots-clés...")

        for keyword in search_keywords:
            if len(images) >= num_images:
                break
                
            keyword = keyword.strip()
            if not keyword:
                continue
                
            # 1. Vérifier le cache d'abord
            cached_path = self._get_from_cache(keyword)
            if cached_path:
                images.append(cached_path)
                print(f"   ✅ Cache: '{keyword}'")
                continue

            # 2. Tenter l'API Unsplash
            image_path = self._fetch_and_download_image(keyword)
            if image_path:
                images.append(image_path)
                print(f"   ✅ Unsplash: '{keyword}'")
            else:
                print(f"   ❌ Échec: '{keyword}'")

        # Si pas assez d'images Unsplash, compléter avec des fallbacks
        if len(images) < num_images:
            needed = num_images - len(images)
            print(f"   🔄 Complétion avec {needed} image(s) fallback")
            fallback_images = self._generate_fallback_images(content_data, needed)
            images.extend(fallback_images)

        return images[:num_images]

    def _generate_search_keywords(self, content_data: Dict[str, Any]) -> List[str]:
        """
        Génère des mots-clés de recherche optimisés pour les images.
        Basé sur la structure de données de auto_content_engine.py
        """
        keywords = []
        
        # 1. Mots-clés explicites (priorité)
        explicit_keywords = content_data.get('keywords', [])
        if explicit_keywords:
            keywords.extend(explicit_keywords)
        
        # 2. Titre découpé en mots-clés
        title = content_data.get('title', '')
        if title:
            # Nettoyer le titre et extraire les mots significatifs
            title_words = self._extract_keywords_from_title(title)
            keywords.extend(title_words)
        
        # 3. Thème principal
        theme = content_data.get('theme', '')
        if theme and theme not in keywords:
            keywords.append(theme)
        
        # 4. Type de contenu
        content_type = content_data.get('content_type', '')
        if content_type and content_type not in keywords:
            keywords.append(content_type)
        
        # 5. Mots-clés génériques basés sur le thème
        generic_keywords = self._get_generic_keywords(content_data)
        keywords.extend(generic_keywords)
        
        # Nettoyer et dédupliquer
        clean_keywords = []
        seen = set()
        for kw in keywords:
            if kw and kw.strip() and kw.strip().lower() not in seen:
                clean_kw = kw.strip()
                clean_keywords.append(clean_kw)
                seen.add(clean_kw.lower())
        
        print(f"   🔍 Mots-clés générés: {clean_keywords}")
        return clean_keywords

    def _extract_keywords_from_title(self, title: str) -> List[str]:
        """Extrait des mots-clés significatifs d'un titre."""
        # Mots à exclure
        stop_words = {'les', 'des', 'une', 'un', 'de', 'du', 'la', 'le', 'et', 'ou', 'dans', 'sur', 'pour', 'avec'}
        
        # Nettoyer le titre
        clean_title = ''.join(c for c in title if c.isalnum() or c.isspace())
        words = clean_title.split()
        
        # Filtrer les mots significatifs
        keywords = []
        for word in words:
            word_lower = word.lower()
            if (len(word) > 2 and 
                word_lower not in stop_words and 
                not word.isdigit()):
                keywords.append(word)
        
        return keywords

    def _get_generic_keywords(self, content_data: Dict[str, Any]) -> List[str]:
        """Ajoute des mots-clés génériques basés sur le thème."""
        theme = content_data.get('theme', '').lower()
        content_type = content_data.get('content_type', '').lower()
        
        generic_map = {
            'santé': ['santé', 'médecine', 'bien-être', 'santé publique', 'prévention'],
            'technologie': ['technologie', 'innovation', 'digital', 'tech', 'futur'],
            'éducation': ['éducation', 'apprentissage', 'savoir', 'connaissance', 'école'],
            'finance': ['finance', 'argent', 'économie', 'investissement', 'budget'],
            'développement personnel': ['développement personnel', 'motivation', 'succès', 'croissance'],
            'science': ['science', 'recherche', 'découverte', 'scientifique']
        }
        
        keywords = []
        
        # Mots-clés par thème
        if theme in generic_map:
            keywords.extend(generic_map[theme])
        
        # Mots-clés par type de contenu
        if 'tutoriel' in content_type:
            keywords.extend(['tutoriel', 'guide', 'apprentissage'])
        elif 'actualité' in content_type:
            keywords.extend(['actualité', 'news', 'information'])
        elif 'analyse' in content_type:
            keywords.extend(['analyse', 'étude', 'expert'])
        
        return keywords

    def _generate_fallback_images(self, content_data: Dict[str, Any], num_images: int) -> List[str]:
        """
        Génère des images de fallback colorées avec le titre.
        """
        images = []
        title = content_data.get('title', 'Contenu YouTube')
        theme = content_data.get('theme', 'général')
        
        # Couleurs par thème
        theme_colors = {
            'santé': [(70, 130, 180), (65, 105, 225), (100, 149, 237)],  # Bleus
            'technologie': [(47, 79, 79), (105, 105, 105), (169, 169, 169)],  # Gris
            'éducation': [(139, 0, 0), (178, 34, 34), (205, 92, 92)],  # Rouges
            'finance': [(34, 139, 34), (50, 205, 50), (144, 238, 144)],  # Verts
            'développement personnel': [(255, 140, 0), (255, 165, 0), (255, 215, 0)],  # Oranges
            'default': [(106, 90, 205), (123, 104, 238), (147, 112, 219)]  # Violets
        }
        
        colors = theme_colors.get(theme.lower(), theme_colors['default'])
        
        for i in range(num_images):
            color = colors[i % len(colors)]
            image_path = self._create_colored_image(title, color, i)
            if image_path:
                images.append(image_path)
                print(f"   🎨 Fallback {i+1}: '{title[:30]}...'")
        
        return images

    def _create_colored_image(self, title: str, color: tuple, index: int) -> str:
        """Crée une image colorée avec le titre."""
        try:
            width, height = self.target_resolution
            image = Image.new('RGB', (width, height), color=color)
            draw = ImageDraw.Draw(image)
            
            # Essayer de charger une police, sinon utiliser la police par défaut
            try:
                font_size = min(width // 20, 72)
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            # Préparer le texte
            title_lines = self._split_text(title, 30)  # 30 caractères par ligne max
            text = "\n".join(title_lines)
            
            # Calculer la position du texte
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Dessiner le texte
            draw.text((x, y), text, fill=(255, 255, 255), font=font, align="center")
            
            # Sauvegarder l'image
            filename = f"fallback_{clean_filename(title)}_{index}.jpg"
            image_path = safe_path_join(self.download_dir, filename)
            image.save(image_path, 'JPEG', quality=90)
            
            return image_path
            
        except Exception as e:
            print(f"❌ Erreur création image fallback: {e}")
            return ""

    def _split_text(self, text: str, max_chars: int) -> List[str]:
        """Découpe un texte en lignes de longueur maximale."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if len(' '.join(current_line + [word])) <= max_chars:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text[:max_chars]]

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
            with open(cache_path, 'wb') as f:
                f.write(image_content)
                
            # Redimensionner si nécessaire
            try:
                self._resize_and_save_image(cache_path, self.target_resolution)
            except Exception as resize_error:
                print(f"⚠️ Redimensionnement échoué: {resize_error}")
                
            return cache_path
        except Exception as e:
            print(f"❌ Erreur sauvegarde cache: {e}")
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return None

    # --- Requête API Unsplash ---

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
                return None

            # Prendre la première image
            image_info = data['results'][0]
            download_url = image_info['urls']['regular']
            
            # Téléchargement
            image_response = requests.get(download_url, stream=True, timeout=20)
            image_response.raise_for_status()
            
            return self._save_to_cache(keyword, image_response.content)
            
        except requests.exceptions.RequestException as e:
            return None
        except Exception as e:
            return None

    def _resize_and_save_image(self, path: str, target_size: List[int]):
        """Redimensionne et ré-enregistre l'image."""
        try:
            target_width, target_height = target_size
            img = Image.open(path)
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
            img.save(path, format='JPEG', quality=85)
        except Exception as e:
            print(f"⚠️ Redimensionnement échoué: {e}")

# --- Fonction d'Export ---

def get_images(content_data: Dict[str, Any], num_images: int = 3) -> List[str]:
    """
    Fonction d'export simple pour auto_content_engine.py
    Retourne toujours au moins des images fallback
    """
    try:
        manager = ImageManager()
        return manager.get_images_for_content(content_data, num_images)
    except Exception as e:
        print(f"❌ Erreur ImageManager: {e}")
        # Fallback minimal
        manager = ImageManager()
        return manager._generate_fallback_images(content_data, num_images)

def test_image_manager():
    """Teste le manager avec des données similaires à auto_content_engine.py"""
    test_content = {
        'title': 'Les Bienfaits de la Méditation sur la Santé Mentale',
        'theme': 'santé',
        'content_type': 'tutoriel',
        'keywords': ['méditation', 'santé mentale', 'bien-être']
    }
    
    print("🧪 Test ImageManager...")
    manager = ImageManager()
    images = manager.get_images_for_content(test_content, 3)
    print(f"📷 Images trouvées: {len(images)}")
    for img in images:
        print(f"   → {os.path.basename(img)}")

if __name__ == "__main__":
    test_image_manager()
