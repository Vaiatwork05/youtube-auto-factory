import os
import tempfile
from moviepy.editor import ColorClip, CompositeVideoClip, ImageClip
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class VideoCreator:
    def __init__(self):
        self.video_duration = 10  # 10 secondes pour tester
        self.resolution = (1280, 720)  # HD
    
    def create_simple_video(self, script_data, output_dir="output"):
        """Crée une vidéo simple sans ImageMagick"""
        
        # Créer le dossier de sortie
        os.makedirs(output_dir, exist_ok=True)
        
        print("🎥 Création vidéo avec méthode simple...")
        
        # Créer une image avec du texte
        img = Image.new('RGB', self.resolution, color=(30, 30, 60))  # Fond bleu nuit
        draw = ImageDraw.Draw(img)
        
        # Utiliser une police basique
        try:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
        except:
            font = None
            title_font = None
        
        # Diviser le texte en lignes
        words = script_data["script"].split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if len(test_line) < 40:  # Limite de caractères par ligne
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Dessiner le titre
        draw.text((100, 100), script_data["title"], fill=(255, 255, 0), font=title_font)  # Jaune
        
        # Dessiner le texte
        y_position = 200
        for line in lines[:6]:  # Maximum 6 lignes
            if y_position < 600:  # Ne pas dépasser le bas de l'écran
                draw.text((100, y_position), line, fill=(255, 255, 255), font=font)  # Blanc
                y_position += 40
        
        # Ajouter un footer
        draw.text((100, 650), "Science Auto Daily • Abonnez-vous !", fill=(200, 200, 200), font=font)
        
        # Sauvegarder l'image temporaire
        temp_image_path = os.path.join(output_dir, "temp_frame.png")
        img.save(temp_image_path)
        
        # Créer une vidéo à partir de l'image
        image_clip = ImageClip(temp_image_path, duration=self.video_duration)
        
        # Exporter la vidéo
        output_path = os.path.join(output_dir, f"video_{script_data['title'].replace(' ', '_')}.mp4")
        image_clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Nettoyer
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
        
        print(f"✅ Vidéo créée: {output_path}")
        return output_path

# Test
if __name__ == "__main__":
    creator = VideoCreator()
    test_script = {
        "title": "Test Video",
        "script": "Ceci est un test de création vidéo automatique sans ImageMagick! La science nous entoure et ces vidéos automatiques vous l'expliquent simplement."
    }
    creator.create_simple_video(test_script)
