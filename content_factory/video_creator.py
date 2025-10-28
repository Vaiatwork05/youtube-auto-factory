# content_factory/video_creator.py
import os
import sys
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
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
            
            if not script:
                raise Exception("Aucun script fourni")
            
            # Nettoyer le titre pour le nom de fichier
            clean_title = clean_filename(title)
            video_path = safe_path_join(self.output_dir, f"video_{clean_title}.mp4")
            
            print(f"📝 Titre vidéo: {title}")
            print(f"💾 Fichier de sortie: {video_path}")
            
            # Générer l'audio
            print("🔊 Génération de l'audio...")
            from audio_generator import AudioGenerator
            audio_generator = AudioGenerator()
            audio_path = audio_generator.generate_audio(script, title)
            
            if not audio_path or not os.path.exists(audio_path):
                raise Exception(f"Audio non généré ou non trouvé: {audio_path}")
            
            print(f"✅ Audio généré: {audio_path}")
            
            # Obtenir des images pertinentes
            print("🖼️ Récupération des images...")
            image_paths = self.image_manager.get_images_for_content(content_data, num_images=8)
            
            if not image_paths:
                raise Exception("Aucune image disponible")
            
            print(f"✅ {len(image_paths)} images obtenues")
            
            # Créer la vidéo avec les images et l'audio
            print("🎥 Assemblage de la vidéo...")
            final_video = self.create_video_from_images_and_audio(image_paths, audio_path, video_path)
            
            print(f"✅ Vidéo créée avec succès: {video_path}")
            return video_path
            
        except Exception as e:
            print(f"❌ Erreur création vidéo: {e}")
            import traceback
            traceback.print_exc()
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
            # Vérifier que l'audio existe
            if not os.path.exists(audio_path):
                raise Exception(f"Fichier audio introuvable: {audio_path}")
            
            # Charger l'audio
            print("🔊 Chargement de l'audio...")
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            
            if audio_duration <= 0:
                raise Exception("Durée audio invalide")
            
            # Calculer la durée par image
            num_images = len(image_paths)
            duration_per_image = audio_duration / num_images
            
            print(f"⏱️ Durée audio: {audio_duration:.2f}s")
            print(f"🖼️ Nombre d'images: {num_images}")
            print(f"⏰ Durée par image: {duration_per_image:.2f}s")
            
            # Créer les clips vidéo
            video_clips = []
            valid_images = []
            
            for i, image_path in enumerate(image_paths):
                try:
                    # Vérifier que l'image existe
                    if not os.path.exists(image_path):
                        print(f"⚠️ Image manquante: {image_path}")
                        continue
                    
                    # Vérifier que l'image est valide
                    try:
                        with Image.open(image_path) as img:
                            img.verify()
                    except Exception:
                        print(f"⚠️ Image corrompue: {image_path}")
                        continue
                    
                    print(f"📹 Création clip {i+1}/{num_images}: {os.path.basename(image_path)}")
                    
                    # Créer un clip image avec la durée calculée
                    image_clip = ImageClip(image_path, duration=duration_per_image)
                    
                    # Redimensionner pour format 16:9 (1920x1080)
                    image_clip = image_clip.resize(height=1080)
                    
                    # Assurer la largeur minimum
                    if image_clip.w < 1920:
                        image_clip = image_clip.resize(width=1920)
                    
                    video_clips.append(image_clip)
                    valid_images.append(image_path)
                    
                except Exception as e:
                    print(f"⚠️ Erreur création clip {i+1}: {e}")
                    continue
            
            if not video_clips:
                raise Exception("Aucun clip vidéo créé - toutes les images ont échoué")
            
            print(f"✅ {len(video_clips)} clips créés avec succès")
            
            # Concaténer tous les clips
            print("🎞️ Concaténation des clips...")
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Ajouter l'audio
            print("🔊 Ajout de l'audio...")
            final_video = final_video.set_audio(audio_clip)
            final_video = final_video.set_duration(audio_duration)
            
            # Exporter la vidéo
            print("📤 Export de la vidéo...")
            final_video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None,
                threads=4,
                preset='medium',
                bitrate='2000k'
            )
            
            print(f"✅ Vidéo exportée: {output_path}")
            
            # Nettoyer la mémoire
            print("🧹 Nettoyage mémoire...")
            for clip in video_clips:
                clip.close()
            final_video.close()
            audio_clip.close()
            
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur création vidéo from images: {e}")
            import traceback
            traceback.print_exc()
            
            # Nettoyer en cas d'erreur
            try:
                for clip in video_clips:
                    clip.close()
                final_video.close()
                audio_clip.close()
            except:
                pass
            
            raise
    
    def create_fallback_video(self, content_data, output_dir="output"):
        """
        Crée une vidéo de secours en cas d'erreur
        """
        try:
            print("🔄 Création vidéo de secours...")
            
            title = content_data.get('title', 'Video de secours')
            clean_title = clean_filename(title)
            video_path = safe_path_join(self.output_dir, f"fallback_{clean_title}.mp4")
            
            # Créer une image simple
            from image_manager import ImageManager
            img_manager = ImageManager()
            image_path = img_manager.create_placeholder_image("secours", 0)
            
            # Créer un audio simple
            from audio_generator import AudioGenerator
            audio_gen = AudioGenerator()
            audio_path = audio_gen.generate_audio_google_tts(
                "Ceci est une vidéo de secours.", 
                f"secours_{clean_title}"
            )
            
            # Créer une vidéo simple
            image_clip = ImageClip(image_path, duration=10)
            audio_clip = AudioFileClip(audio_path)
            final_clip = image_clip.set_audio(audio_clip)
            final_clip = final_clip.set_duration(10)
            
            final_clip.write_videofile(
                video_path,
                fps=24,
                verbose=False,
                logger=None
            )
            
            # Nettoyer
            image_clip.close()
            audio_clip.close()
            final_clip.close()
            
            print(f"✅ Vidéo de secours créée: {video_path}")
            return video_path
            
        except Exception as e:
            print(f"❌ Erreur vidéo de secours: {e}")
            return None

# Fonction utilitaire pour usage direct
def create_video(content_data):
    """
    Fonction helper pour créer une vidéo
    """
    creator = VideoCreator()
    return creator.create_professional_video(content_data)

def create_simple_video(content_data):
    """
    Fonction helper pour créer une vidéo simple
    """
    creator = VideoCreator()
    return creator.create_simple_video(content_data)

# Test du module
if __name__ == "__main__":
    print("🧪 Test de VideoCreator...")
    
    test_content = {
        'title': 'Test Vidéo Creator',
        'script': 'Ceci est un test de création vidéo.',
        'category': 'test'
    }
    
    try:
        creator = VideoCreator()
        video_path = creator.create_professional_video(test_content)
        print(f"✅ Test réussi: {video_path}")
    except Exception as e:
        print(f"❌ Test échoué: {e}")
        # Essayer la version de secours
        fallback_path = creator.create_fallback_video(test_content)
        if fallback_path:
            print(f"✅ Vidéo de secours créée: {fallback_path}")                codec='libx264',
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
