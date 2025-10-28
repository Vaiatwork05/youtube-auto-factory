import os
import requests
import re
from collections import Counter
from PIL import Image
import urllib.request
import time
import random

class ImageManager:
    def __init__(self, download_folder="downloaded_images"):
        self.download_folder = download_folder
        self.setup_directories()
        
    def setup_directories(self):
        """Crée le dossier de téléchargement s'il n'existe pas"""
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)
    
    def extract_keywords(self, text, max_keywords=5):
        """
        Extrait les mots-clés les plus importants d'un texte
        """
        # Nettoyer le texte et trouver les mots
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Liste des mots à exclure (stop words)
        stop_words = {
            'this', 'that', 'with', 'from', 'have', 'were', 'their', 
            'what', 'when', 'which', 'they', 'will', 'would', 'could',
            'about', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'under', 'while', 'since',
            'until', 'upon', 'toward', 'among', 'according', 'because'
        }
        
        # Filtrer les mots significatifs
        meaningful_words = [word for word in words if word not in stop_words]
        
        if not meaningful_words:
            # Fallback: prendre les mots les plus longs
            meaningful_words = sorted(words, key=len, reverse=True)[:max_keywords]
        
        # Compter les fréquences et retourner les plus courants
        word_freq = Counter(meaningful_words)
        return [word for word, count in word_freq.most_common(max_keywords)]
    
    def generate_search_queries(self, keywords, text_segment=""):
        """
        Génère des requêtes de recherche intelligentes basées sur les mots-clés
        """
        queries = []
        
        if not keywords:
            # Fallback: extraire les noms propres du texte
            proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', text_segment)
            if proper_nouns:
                queries.extend(proper_nouns[:3])
            return queries or ["abstract"]
        
        # Combinaisons de mots-clés
        if len(keywords) >= 2:
            queries.append(f"{keywords[0]} {keywords[1]}")
            queries.append(f"{keywords[0]} concept")
        
        # Mots-clés individuels
        queries.extend(keywords[:3])
        
        # Ajouter des termes contextuels
        if "technology" in text_segment.lower():
            queries.append("technology innovation")
        if "science" in text_segment.lower():
            queries.append("scientific discovery")
        if "future" in text_segment.lower():
            queries.append("futuristic technology")
        if "history" in text_segment.lower():
            queries.append("historical event")
        
        return list(set(queries))  # Supprimer les doublons
    
    def search_images(self, query, num_images=3):
        """
        Recherche des images basées sur une requête
        Note: À adapter avec votre API d'images préférée
        """
        # Cette fonction simule la recherche d'images
        # Remplacez par votre logique de recherche réelle (Unsplash, Pexels, etc.)
        
        print(f"🔍 Recherche d'images pour: '{query}'")
        
        # Simulation - en production, utilisez une vraie API
        simulated_images = []
        for i in range(num_images):
            # Créer une image de placeholder avec le texte de la requête
            img_path = self.create_placeholder_image(query, i)
            simulated_images.append(img_path)
        
        return simulated_images
    
    def create_placeholder_image(self, query, index):
        """
        Crée une image placeholder avec le texte de la requête
        À remplacer par de vraies images d'API
        """
        # Créer un nom de fichier basé sur la requête
        safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"{safe_query}_{index}_{int(time.time())}.jpg"
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
