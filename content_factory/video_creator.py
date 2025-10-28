import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
from PIL import Image
import numpy as np
from utils import clean_filename, safe_path_join, ensure_directory

class VideoCreator:
    def __init__(self):
        from image_manager import ImageManager
        self.image_manager = ImageManager()
        self.output_dir = "output/videos"
        ensure_directory(self.output_dir)
    
    def create_professional_video(self, content_data, output_dir="output"):
        """
        Crée une vidéo professionnelle synchronisée
        """
        try:
            print("🎬 Création vidéo professionnelle...")
            
            # Obtenir le script et titre
            script = content_data.get('script', '')
            title = content_data.get('title', 'Video')
            
            # Nettoyer le titre pour le nom de fichier
            clean_title = clean_filename(title)
            video_path = safe_path_join(self.output_dir, f"video_{clean_title}.mp3")
            
            # Générer l'audio
            from audio_generator import AudioGenerator
            audio_generator = AudioGenerator()
            audio_path = audio_generator.generate_audio(script, title)
            
            if not audio_path or not os.path.exists(audio_path):
                raise Exception("Audio non généré")
            
            # Obtenir des images pertinentes
            image_paths = self.image_manager.get_images_for_content(content_data, num_images=10)
            
            if not image_paths:
                raise Exception("Aucune image disponible")
            
            print(f"🖼️ {len(image_paths)} images disponibles")
            
            # Créer la vidéo avec les images et l'audio
            final_video = self.create_video_from_images_and_audio(image_paths, audio_path, video_path)
            
            print(f"✅ Vidéo créée: {video_path}")
            return video_path
            
        except Exception as e:
            print(f"❌ Erreur création vidéo: {e}")
            raise
    
    def create_simple_video(self, content_data):
        """
        Version simplifiée pour la compatibilité
        """
        return self.create_professional_video(content_data)
    
    def create_video_from_images_and_audio(self, image_paths, audio_path, output_path):
        """
        Crée une vidéo à partir d'images et d'audio
        """
        try:
            # Charger l'audio
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            
            # Calculer la durée par image
            num_images = len(image_paths)
            duration_per_image = audio_duration / num_images
            
            print(f"⏱️ Durée audio: {audio_duration:.2f}s, {num_images} images, {duration_per_image:.2f}s par image")
            
            # Créer les clips vidéo
            video_clips = []
            for i, image_path in enumerate(image_paths):
                try:
                    # Créer un clip image avec la durée calculée
                    image_clip = ImageClip(image_path, duration=duration_per_image)
                    
                    # Redimensionner si nécessaire
                    image_clip = image_clip.resize(height=1080)
                    
                    video_clips.append(image_clip)
                    print(f"📹 Clip {i+1} créé: {os.path.basename(image_path)}")
                    
                except Exception as e:
                    print(f"⚠️ Erreur clip {i+1}: {e}")
                    continue
            
            if not video_clips:
                raise Exception("Aucun clip vidéo créé")
            
            # Concaténer tous les clips
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Ajouter l'audio
            final_video = final_video.set_audio(audio_clip)
            
            # Exporter la vidéo
            final_video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None
            )
            
            # Fermer les clips pour libérer la mémoire
            for clip in video_clips:
                clip.close()
            final_video.close()
            audio_clip.close()
            
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur création vidéo from images: {e}")
            raise
