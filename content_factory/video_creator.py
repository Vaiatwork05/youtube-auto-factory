import os
from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
from PIL import Image
from content_factory.image_manager import ImageManager
from content_factory.audio_generator import AudioGenerator

class VideoCreator:
    def __init__(self):
        self.video_duration = 30  # 30 secondes maintenant
        self.resolution = (1280, 720)
        self.image_manager = ImageManager()
        self.audio_generator = AudioGenerator()
    
    def create_professional_video(self, script_data, output_dir="output"):
        """Crée une vidéo professionnelle avec voix off et images"""
        
        os.makedirs(output_dir, exist_ok=True)
        print("🎬 Création vidéo professionnelle...")
        
        # 1. Générer l'audio
        print("🎙️ Génération de la voix off...")
        audio_path = self.audio_generator.generate_audio(script_data, script_data["title"])
        
        # 2. Préparer l'image de fond avec texte
        print("🖼️ Préparation des visuels...")
        image_path = self.image_manager.get_random_science_image()
        
        # Nettoyer le texte pour l'overlay
        clean_title = script_data["title"].replace('?', '').replace('!', '').replace(':', '')
        words = script_data["script"].split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if len(test_line) < 40:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Créer l'image avec overlay
        if image_path:
            final_image = self.image_manager.create_text_overlay(image_path, clean_title, lines)
            if final_image:
                image_path = os.path.join(output_dir, "final_frame.jpg")
                final_image.save(image_path)
        
        # 3. Créer la vidéo
        print("🎥 Assemblage vidéo...")
        
        # Clip image
        image_clip = ImageClip(image_path, duration=self.video_duration)
        
        # Clip audio si généré
        if audio_path and os.path.exists(audio_path):
            audio_clip = AudioFileClip(audio_path)
            # Ajuster la durée de la vidéo à celle de l'audio
            actual_duration = audio_clip.duration
            image_clip = image_clip.set_duration(actual_duration)
            image_clip = image_clip.set_audio(audio_clip)
        
        # Exporter
        clean_filename = clean_title.replace(' ', '_').replace('/', '_')
        output_path = os.path.join(output_dir, f"video_{clean_filename}.mp4")
        
        image_clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
        
        # Nettoyage
        for temp_file in [image_path, audio_path] if audio_path else [image_path]:
            if temp_file and os.path.exists(temp_file) and "temp" in temp_file:
                os.remove(temp_file)
        
        print(f"✅ Vidéo professionnelle créée: {output_path}")
        return output_path

    def create_simple_video(self, script_data, output_dir="output"):
        """Alias pour compatibilité"""
        return self.create_professional_video(script_data, output_dir)
