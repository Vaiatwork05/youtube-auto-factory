# content_factory/image_manager.py
import os
import requests
import logging
from PIL import Image, ImageDraw, ImageFont
import random
import time
from pathlib import Path
from utils import clean_filename, safe_path_join, ensure_directory

class ImageManager:
    def __init__(self, unsplash_access_key=None):
        self.output_dir = "output/images"
        self.unsplash_access_key = unsplash_access_key or os.getenv('UNSPLASH_ACCESS_KEY')
        ensure_directory(self.output_dir)
        
        # Configuration des couleurs pour les placeholders
        self.colors = [
            (70, 130, 180),    # Bleu acier
            (46, 139, 87),     # Vert mer
            (178, 34, 34),     # Rouge brique
            (148, 0, 211),     # Violet
            (255, 140, 0),     # Orange foncé
            (60, 179, 113),    # Vert medium
            (123, 104, 238),   # Violet medium
            (205, 92, 92)      # Rouge indien
        ]
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_images_for_content(self, content_data, num_images=8):
        """
        Récupère les images pour le contenu - MÉTHODE MANQUANTE AJOUTÉE
        """
        self.logger.info(f"🖼️  Récupération de {num_images} images pour le contenu")
        
        # Extraire les mots-clés
        keywords = self._extract_keywords_from_content(content_data)
        self.logger.info(f"🔑 Mots-clés extraits: {keywords}")
        
        # Récupérer les images avec fallback
        images = self.get_images_with_fallback(keywords, num_images)
        
        self.logger.info(f"✅ {len(images)} images obtenues")
        return images
    
    def get_images_with_fallback(self, keywords, num_images):
        """
        Système de fallback pour la récupération d'images
        """
        images = []
        
        # 1. Essayer Unsplash d'abord
        if self.unsplash_access_key:
            self.logger.info("🌅 Tentative de récupération via Unsplash...")
            unsplash_images = self._try_unsplash_search(keywords, num_images)
            images.extend(unsplash_images)
        
        # 2. Compléter avec des placeholders si nécessaire
        if len(images) < num_images:
            missing_count = num_images - len(images)
            self.logger.info(f"🔄 Création de {missing_count} placeholders...")
            placeholders = self._create_placeholder_images(keywords, missing_count)
            images.extend(placeholders)
        
        return images[:num_images]
    
    def _extract_keywords_from_content(self, content_data):
        """
        Extrait les mots-clés du contenu
        """
        keywords = []
        
        # Priorité 1: Mots-clés explicites
        if content_data.get('keywords'):
            keywords.extend(content_data['keywords'])
        
        # Priorité 2: Titre
        if content_data.get('title'):
            title_keywords = self._extract_keywords_from_text(content_data['title'])
            keywords.extend(title_keywords)
        
        # Priorité 3: Description/script
        if content_data.get('description'):
            desc_keywords = self._extract_keywords_from_text(content_data['description'])
            keywords.extend(desc_keywords)
        
        # Éliminer les doublons et vides
        keywords = [k for k in keywords if k and len(k) > 2]
        keywords = list(dict.fromkeys(keywords))  # Garder l'ordre
        
        # Limiter à 5 mots-clés maximum
        return keywords[:5]
    
    def _extract_keywords_from_text(self, text):
        """
        Extrait les mots-clés d'un texte
        """
        # Mots à exclure
        stop_words = {'le', 'la', 'les', 'de', 'des', 'du', 'et', 'ou', 'dans', 'pour', 'avec', 'sur', 'par'}
        
        # Nettoyer et séparer les mots
        words = text.lower().split()
        keywords = []
        
        for word in words:
            # Nettoyer le mot
            clean_word = ''.join(c for c in word if c.isalnum() or c in ('-', '_'))
            if (clean_word and len(clean_word) > 2 and 
                clean_word not in stop_words and
                not clean_word.isnumeric()):
                keywords.append(clean_word)
        
        return keywords
    
    def _try_unsplash_search(self, keywords, num_images):
        """
        Tente une recherche Unsplash avec gestion d'erreurs
        """
        images = []
        
        for keyword in keywords[:3]:  # Maximum 3 mots-clés pour Unsplash
            if len(images) >= num_images:
                break
                
            try:
                self.logger.info(f"🔍 Recherche Unsplash: '{keyword}'")
                unsplash_images = self.unsplash_search(keyword, num_images - len(images))
                images.extend(unsplash_images)
                time.sleep(0.5)  # Respect rate limit
                
            except Exception as e:
                self.logger.error(f"❌ Erreur Unsplash pour '{keyword}': {e}")
                continue
        
        return images
    
    def unsplash_search(self, query, count=5):
        """
        Recherche d'images sur Unsplash - EXISTANT DANS VOTRE CODE
        """
        try:
            if not self.unsplash_access_key:
                raise ValueError("Clé API Unsplash non configurée")
            
            headers = {
                'Authorization': f'Client-ID {self.unsplash_access_key}'
            }
            
            params = {
                'query': query,
                'per_page': count,
                'orientation': 'landscape'
            }
            
            response = requests.get(
                'https://api.unsplash.com/search/photos',
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 401:
                self.logger.error("❌ Erreur 401 Unsplash: Clé API invalide")
                return []
            elif response.status_code != 200:
                self.logger.error(f"❌ Erreur Unsplash {response.status_code}: {response.text}")
                return []
            
            data = response.json()
            images = []
            
            for photo in data.get('results', [])[:count]:
                image_url = photo['urls']['regular']
                image_filename = f"unsplash_{query}_{photo['id']}.jpg"
                image_path = safe_path_join(self.output_dir, image_filename)
                
                # Télécharger l'image
                if self._download_image(image_url, image_path):
                    images.append(image_path)
            
            self.logger.info(f"✅ {len(images)} images Unsplash téléchargées pour '{query}'")
            return images
            
        except requests.exceptions.Timeout:
            self.logger.error(f"❌ Timeout Unsplash pour '{query}'")
            return []
        except Exception as e:
            self.logger.error(f"❌ Erreur recherche Unsplash: {e}")
            return []
    
    def _download_image(self, url, save_path):
        """
        Télécharge une image depuis une URL
        """
        try:
            response = requests.get(url, timeout=10, stream=True)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erreur téléchargement image: {e}")
            return False
    
    def _create_placeholder_images(self, keywords, count):
        """
        Crée des images placeholder de haute qualité
        """
        placeholders = []
        
        for i in range(count):
            keyword = keywords[i % len(keywords)] if keywords else "image"
            placeholder_path = self.create_placeholder_image(keyword, i)
            placeholders.append(placeholder_path)
        
        return placeholders
    
    def create_placeholder_image(self, keyword, index):
        """
        Crée une image placeholder attrayante - EXISTANT DANS VOTRE CODE
        """
        try:
            # Dimensions HD
            width, height = 1280, 720
            
            # Créer l'image avec fond coloré
            color = random.choice(self.colors)
            img = Image.new('RGB', (width, height), color=color)
            draw = ImageDraw.Draw(img)
            
            # Essayer de charger une police, sinon utiliser la police par défaut
            try:
                font_size = 60
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            # Calculer la position du texte
            text = keyword.upper()
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # Ajouter le texte avec ombre
            shadow_color = (0, 0, 0, 128)
            text_color = (255, 255, 255)
            
            # Ombre
            draw.text((x+2, y+2), text, font=font, fill=shadow_color)
            # Texte principal
            draw.text((x, y), text, font=font, fill=text_color)
            
            # Sauvegarder l'image
            filename = f"placeholder_{clean_filename(keyword)}_{index}.jpg"
            filepath = safe_path_join(self.output_dir, filename)
            img.save(filepath, quality=85)
            
            self.logger.info(f"🖼️  Placeholder créé: {filename}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"❌ Erreur création placeholder: {e}")
            # Fallback ultra simple
            filename = f"placeholder_{keyword}_{index}.jpg"
            filepath = safe_path_join(self.output_dir, filename)
            Image.new('RGB', (1280, 720), color=(100, 100, 100)).save(filepath)
            return filepath
    
    def cleanup_old_images(self, keep_count=20):
        """
        Nettoie les anciennes images
        """
        try:
            image_files = list(Path(self.output_dir).glob("*.jpg"))
            
            if len(image_files) > keep_count:
                # Trier par date de modification
                image_files.sort(key=lambda x: x.stat().st_mtime)
                
                # Supprimer les plus anciens
                for old_file in image_files[:-keep_count]:
                    old_file.unlink()
                    self.logger.info(f"🗑️  Image supprimée: {old_file}")
                    
        except Exception as e:
            self.logger.error(f"❌ Erreur nettoyage images: {e}")


# Fonction utilitaire pour usage direct
def get_images_for_content(content_data, num_images=8):
    """
    Fonction helper pour récupérer des images
    """
    manager = ImageManager()
    return manager.get_images_for_content(content_data, num_images)


# Test du module
if __name__ == "__main__":
    def test_image_manager():
        """Test du ImageManager"""
        print("🧪 Test du ImageManager...")
        
        manager = ImageManager()
        
        # Données de test
        test_content = {
            'title': 'La beauté de la nature et des paysages',
            'description': 'Découvrez les plus beaux paysages naturels du monde',
            'keywords': ['nature', 'paysage', 'montagne', 'forêt']
        }
        
        # Test de la méthode manquante
        images = manager.get_images_for_content(test_content, num_images=4)
        
        print(f"✅ {len(images)} images obtenues:")
        for img in images:
            print(f"   - {img}")
        
        return len(images) > 0
    
    # Exécuter le test
    test_image_manager()        filename = f"placeholder_{safe_query}_{index}.jpg"
        filepath = os.path.join(self.download_folder, filename)
        
        try:
            colors = [
                (74, 144, 226), (231, 76, 60), (39, 174, 96),
                (155, 89, 182), (241, 196, 15)
            ]
            
            color = colors[index % len(colors)]
            img = Image.new('RGB', (1920, 1080), color=color)
            draw = ImageDraw.Draw(img)
            
            # Essayer différentes polices
            try:
                font_size = 48
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                except:
                    font = ImageFont.load_default()
            
            text = f"{query.upper()}"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (1920 - text_width) // 2
            y = (1080 - 48) // 2
            
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
            img.save(filepath, quality=95)
            print(f"🖼️ Placeholder créé: {filename}")
            
        except Exception as e:
            print(f"❌ Erreur création placeholder: {e}")
            open(filepath, 'a').close()
        
        return filepath
    
    def search_images_by_keywords(self, keywords, text_segment="", num_images=5):
        """Recherche des images avec Unsplash + fallback"""
        if not keywords:
            keywords = self.extract_keywords(text_segment)
        
        print(f"🔑 Mots-clés: {keywords}")
        
        downloaded_images = []
        
        # Essayer Unsplash pour chaque mot-clé
        for keyword in keywords[:3]:
            if len(downloaded_images) >= num_images:
                break
                
            print(f"🎯 Recherche Unsplash: '{keyword}'")
            unsplash_urls = self.search_unsplash(keyword, min(2, num_images - len(downloaded_images)))
            
            for i, image_url in enumerate(unsplash_urls):
                filename = clean_filename(f"{keyword}_{i}_{int(time.time())}.jpg")
                local_path = self.download_image(image_url, filename)
                
                if local_path:
                    downloaded_images.append(local_path)
                    print(f"⬇️ Image téléchargée: {filename}")
            
            time.sleep(0.5)  # Pause entre requêtes
        
        # Compléter avec des placeholders si nécessaire
        while len(downloaded_images) < num_images:
            placeholder_keyword = keywords[len(downloaded_images) % len(keywords)] if keywords else "science"
            placeholder = self.create_placeholder_image(placeholder_keyword, len(downloaded_images))
            downloaded_images.append(placeholder)
        
        print(f"✅ {len(downloaded_images)} images obtenues")
        return downloaded_images[:num_images]
    
    def get_images_for_content(self, content_data, num_images=10):
        """Obtient des images pertinentes pour le contenu"""
        script = content_data.get('script', '')
        title = content_data.get('title', '')
        
        full_text = f"{title} {script}"
        keywords = self.extract_keywords(full_text)
        
        print(f"📝 Analyse: {title}")
        print(f"🔍 Mots-clés extraits: {keywords}")
        
        return self.search_images_by_keywords(keywords, full_text, num_images)

# Fonctions utilitaires
def get_images_for_content(content_data, num_images=10):
    manager = ImageManager()
    return manager.get_images_for_content(content_data, num_images)

def extract_keywords(text, max_keywords=5):
    manager = ImageManager()
    return manager.extract_keywords(text, max_keywords)
