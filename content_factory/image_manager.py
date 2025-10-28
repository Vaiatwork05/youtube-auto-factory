import os
import requests
from PIL import Image, ImageDraw, ImageFont
import random

class ImageManager:
    def __init__(self):
        self.images_dir = "content_factory/images"
        os.makedirs(self.images_dir, exist_ok=True)
        self.science_images = [
            "https://images.unsplash.com/photo-1502136969935-8d8eef54d77b?w=800",  # Espace
            "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=800",  # Atomes
            "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800",  # ADN
            "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800",  # Étoiles
        ]
    
    def download_image(self, url, filename):
        """Télécharge une image depuis Unsplash"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                filepath = os.path.join(self.images_dir, filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return filepath
        except Exception as e:
            print(f"🚨 Erreur téléchargement image: {e}")
        return None
    
    def get_random_science_image(self):
        """Retourne le chemin d'une image scientifique aléatoire"""
        # Télécharger une image si nécessaire
        image_url = random.choice(self.science_images)
        filename = f"science_bg_{random.randint(1000, 9999)}.jpg"
        return self.download_image(image_url, filename)
    
    def create_text_overlay(self, image_path, title, text_lines):
        """Crée un overlay de texte sur une image"""
        try:
            # Ouvrir l'image de fond
            bg_image = Image.open(image_path)
            bg_image = bg_image.resize((1280, 720))
            
            # Créer un overlay semi-transparent
            overlay = Image.new('RGBA', (1280, 720), (0, 0, 0, 180))
            
            # Combiner image et overlay
            bg_image = bg_image.convert('RGBA')
            result = Image.alpha_composite(bg_image, overlay)
            
            draw = ImageDraw.Draw(result)
            
            # Titre
            try:
                title_font = ImageFont.truetype("arial.ttf", 48)
                text_font = ImageFont.truetype("arial.ttf", 32)
            except:
                title_font = ImageFont.load_default()
                text_font = ImageFont.load_default()
            
            # Dessiner le titre
            draw.text((100, 80), title, fill=(255, 255, 0), font=title_font)
            
            # Dessiner le texte
            y_position = 180
            for line in text_lines[:5]:
                draw.text((100, y_position), line, fill=(255, 255, 255), font=text_font)
                y_position += 50
            
            # Footer
            draw.text((100, 650), "Science Auto Daily • Abonnez-vous !", 
                     fill=(200, 200, 200), font=text_font)
            
            return result.convert('RGB')
            
        except Exception as e:
            print(f"🚨 Erreur création overlay: {e}")
            return None

# Test
if __name__ == "__main__":
    manager = ImageManager()
    image_path = manager.get_random_science_image()
    if image_path:
        print(f"✅ Image téléchargée: {image_path}")
