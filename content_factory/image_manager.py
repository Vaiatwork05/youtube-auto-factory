# content_factory/image_manager.py
import os
import requests
import re
from collections import Counter
from PIL import Image, ImageDraw, ImageFont
import random
import time
from dotenv import load_dotenv
from utils import clean_filename, ensure_directory

class ImageManager:
    def __init__(self, download_folder="downloaded_images"):
        # Charger le .env
        load_dotenv()
        
        self.download_folder = download_folder
        self.unsplash_key = os.getenv('UNSPLASH_API_KEY')
        self.setup_directories()
    
    def setup_directories(self):
        """Crée le dossier de téléchargement"""
        ensure_directory(self.download_folder)
    
    def extract_keywords(self, text, max_keywords=5):
        """Extrait les mots-clés importants d'un texte"""
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        stop_words = {
            'this', 'that', 'with', 'from', 'have', 'were', 'their', 
            'what', 'when', 'which', 'they', 'will', 'would', 'could'
        }
        
        meaningful_words = [word for word in words if word not in stop_words]
        
        if not meaningful_words:
            meaningful_words = sorted(words, key=len, reverse=True)[:max_keywords]
        
        word_freq = Counter(meaningful_words)
        return [word for word, count in word_freq.most_common(max_keywords)]
    
    def search_unsplash(self, query, num_images=3):
        """Recherche d'images sur Unsplash"""
        try:
            if not self.unsplash_key or self.unsplash_key == 'votre_clé_unsplash_ici':
                print("⚠️ Mode placeholder - Clé Unsplash non configurée")
                return []
            
            print(f"🔍 Unsplash: {query}")
            
            headers = {'Authorization': f'Client-ID {self.unsplash_key}'}
            params = {
                'query': query,
                'count': num_images,
                'orientation': 'landscape'
            }
            
            response = requests.get(
                'https://api.unsplash.com/photos/random',
                headers=headers,
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                image_urls = [item['urls']['regular'] for item in data]
                print(f"✅ Unsplash: {len(image_urls)} images trouvées")
                return image_urls
            else:
                print(f"❌ Unsplash erreur: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Erreur Unsplash: {e}")
            return []
    
    def download_image(self, image_url, filename):
        """Télécharge une image depuis une URL"""
        try:
            filepath = os.path.join(self.download_folder, filename)
            
            response = requests.get(image_url, stream=True, timeout=15)
            response.raise_for_status()
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Vérifier que l'image est valide
            try:
                with Image.open(filepath) as img:
                    img.verify()
                return filepath
            except Exception:
                os.remove(filepath)
                return None
                
        except Exception as e:
            print(f"❌ Erreur téléchargement {filename}: {e}")
            return None
    
    def create_placeholder_image(self, query, index):
        """Crée une image de secours"""
        safe_query = clean_filename(query)
        filename = f"placeholder_{safe_query}_{index}.jpg"
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
