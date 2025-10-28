import os
import re
from collections import Counter
from PIL import Image, ImageDraw, ImageFont
import random
import time

class ImageManager:
    def __init__(self, download_folder="downloaded_images"):
        self.download_folder = download_folder
        self.setup_directories()
    
    def setup_directories(self):
        """Crée le dossier de téléchargement"""
        os.makedirs(self.download_folder, exist_ok=True)
    
    def extract_keywords(self, text, max_keywords=5):
        """Extrait les mots-clés importants"""
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
    
    def create_placeholder_image(self, query, index):
        """Crée une image placeholder (à remplacer par vraies images)"""
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_query}_{index}.jpg"
        filepath = os.path.join(self.download_folder, filename)
        
        try:
            img = Image.new('RGB', (800, 600), color=(random.randint(50, 200), 
                                                     random.randint(50, 200), 
                                                     random.randint(50, 200)))
            draw = ImageDraw.Draw(img)
            
            # Essayer différentes polices
            try:
                font = ImageFont.truetype("arial.ttf", 30)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
                except:
                    font = ImageFont.load_default()
            
            text = f"Image: {query}"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (800 - text_width) // 2
            y = 300
            
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
            img.save(filepath)
            
        except Exception as e:
            print(f"❌ Erreur création image: {e}")
            open(filepath, 'a').close()
        
        return filepath
    
    def search_images_by_keywords(self, keywords, text_segment="", num_images=3):
        """Recherche des images basées sur les mots-clés"""
        if not keywords:
            keywords = self.extract_keywords(text_segment)
        
        print(f"🔍 Recherche images avec mots-clés: {keywords}")
        
        images = []
        for i in range(num_images):
            query = keywords[i % len(keywords)] if keywords else "science"
            image_path = self.create_placeholder_image(query, i)
            images.append(image_path)
        
        return images
    
    def get_images_for_content(self, content_data, num_images=5):
        """Obtient des images pour le contenu"""
        script = content_data.get('script', '')
        keywords = self.extract_keywords(script)
        return self.search_images_by_keywords(keywords, script, num_images)        filename = f"{safe_query}_{index}_{int(time.time())}.jpg"
        filepath = os.path.join(self.download_folder, filename)
        
        # Créer une image simple avec PIL (dans la vraie implémentation, téléchargez de vraies images)
        try:
            img = Image.new('RGB', (800, 600), color=(random.randint(0, 255), 
                                                     random.randint(0, 255), 
                                                     random.randint(0, 255)))
            
            # Ajouter du texte sur l'image
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(img)
            
            # Utiliser une police par défaut
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            
            # Dessiner le texte
            text = f"Image: {query}"
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (800 - text_width) // 2
            y = (600 - text_height) // 2
            
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
            img.save(filepath)
            
            print(f"✅ Image créée: {filepath}")
            
        except Exception as e:
            print(f"❌ Erreur création image: {e}")
            # Créer un fichier vide comme fallback
            open(filepath, 'a').close()
        
        return filepath
    
    def search_images_by_keywords(self, keywords, text_segment="", num_images=3):
        """
        Recherche des images basées sur des mots-clés spécifiques
        """
        if not keywords:
            keywords = self.extract_keywords(text_segment)
        
        search_queries = self.generate_search_queries(keywords, text_segment)
        print(f"📋 Requêtes générées: {search_queries}")
        
        all_images = []
        images_per_query = max(1, num_images // len(search_queries)) if search_queries else num_images
        
        for query in search_queries:
            try:
                query_images = self.search_images(query, images_per_query)
                all_images.extend(query_images)
                print(f"✅ {len(query_images)} images trouvées pour '{query}'")
            except Exception as e:
                print(f"❌ Erreur recherche '{query}': {e}")
        
        # Si pas assez d'images, en ajouter plus
        while len(all_images) < num_images and search_queries:
            extra_query = random.choice(search_queries)
            try:
                extra_images = self.search_images(extra_query, 1)
                all_images.extend(extra_images)
            except:
                break
        
        return all_images[:num_images]
    
    def get_images_for_text_segments(self, text_segments, images_per_segment=2):
        """
        Récupère des images spécifiques pour chaque segment de texte
        """
        segment_images = []
        
        print(f"🎯 Génération d'images pour {len(text_segments)} segments de texte")
        
        for i, segment in enumerate(text_segments):
            print(f"\n📝 Segment {i+1}: {segment[:80]}...")
            
            # Extraire les mots-clés du segment
            keywords = self.extract_keywords(segment)
            print(f"   Mots-clés: {keywords}")
            
            # Rechercher des images spécifiques pour ce segment
            segment_specific_images = self.search_images_by_keywords(
                keywords, segment, images_per_segment
            )
            
            if segment_specific_images:
                selected_image = segment_specific_images[0]
                segment_images.append(selected_image)
                print(f"   🖼️ Image assignée: {os.path.basename(selected_image)}")
            else:
                # Fallback: image par défaut
                default_image = self.create_placeholder_image("default", i)
                segment_images.append(default_image)
                print(f"   ⚠️ Image par défaut assignée")
        
        return segment_images
    
    def download_real_image(self, query, filename=None):
        """
        Télécharge une vraie image depuis une API (exemple avec Unsplash)
        À implémenter avec votre service préféré
        """
        # Exemple avec Unsplash (vous aurez besoin d'une clé API)
        """
        import requests
        
        ACCESS_KEY = "votre_cle_unsplash_ici"
        url = f"https://api.unsplash.com/photos/random"
        params = {
            'query': query,
            'client_id': ACCESS_KEY,
            'count': 1
        }
        
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                image_url = data[0]['urls']['regular']
                
                # Télécharger l'image
                if not filename:
                    filename = f"{query.replace(' ', '_')}_{int(time.time())}.jpg"
                
                filepath = os.path.join(self.download_folder, filename)
                urllib.request.urlretrieve(image_url, filepath)
                return filepath
        except Exception as e:
            print(f"Erreur téléchargement Unsplash: {e}")
        """
        
        # Pour l'instant, retourner un placeholder
        return self.create_placeholder_image(query, 0)
    
    def cleanup_old_images(self, keep_recent=20):
        """
        Nettoie les anciennes images pour éviter l'accumulation
        """
        try:
            images = [os.path.join(self.download_folder, f) 
                     for f in os.listdir(self.download_folder) 
                     if f.endswith(('.jpg', '.png', '.jpeg'))]
            
            images.sort(key=os.path.getmtime, reverse=True)
            
            for old_image in images[keep_recent:]:
                try:
                    os.remove(old_image)
                    print(f"🗑️ Image supprimée: {os.path.basename(old_image)}")
                except Exception as e:
                    print(f"❌ Erreur suppression {old_image}: {e}")
                    
        except Exception as e:
            print(f"❌ Erreur nettoyage images: {e}")

# Fonction utilitaire pour usage externe
def get_images_for_segments(text_segments, images_per_segment=2):
    """
    Fonction helper pour obtenir des images pour des segments de texte
    """
    manager = ImageManager()
    return manager.get_images_for_text_segments(text_segments, images_per_segment)

def extract_keywords_from_text(text, max_keywords=5):
    """
    Fonction helper pour extraire les mots-clés d'un texte
    """
    manager = ImageManager()
    return manager.extract_keywords(text, max_keywords)

# Test du module
if __name__ == "__main__":
    # Test de la fonctionnalité
    test_texts = [
        "Artificial intelligence is transforming modern technology and creating new opportunities for innovation in various industries.",
        "Climate change affects global weather patterns and requires immediate international cooperation to mitigate its effects.",
        "The history of space exploration shows humanity's incredible journey from Earth to the Moon and beyond."
    ]
    
    manager = ImageManager()
    
    print("🧪 Test du ImageManager")
    print("=" * 50)
    
    for i, text in enumerate(test_texts):
        print(f"\nTest {i+1}:")
        print(f"Texte: {text[:60]}...")
        
        keywords = manager.extract_keywords(text)
        print(f"Mots-clés: {keywords}")
        
        images = manager.get_images_for_text_segments([text], 1)
        print(f"Image générée: {os.path.basename(images[0])}")
    
    print("\n✅ Test terminé avec succès!")
