# content_factory/video_creator.py
import os
import sys
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image
from utils import clean_filename, safe_path_join, ensure_directory

class VideoCreator:
    def __init__(self):
        # Import différé pour éviter les circulaires
        self.image_manager = None
        self.audio_generator = None
        self.output_dir = "output/videos"
        ensure_directory(self.output_dir)
    
    def _get_image_manager(self):
        """Import différé de ImageManager"""
        if self.image_manager is None:
            try:
                from content_factory.image_manager import ImageManager
                self.image_manager = ImageManager()
            except ImportError as e:
                print(f"❌ Erreur import ImageManager: {e}")
                # Fallback basique
                class FallbackImageManager:
                    def get_images_for_content(self, content_data, num_images=8):
                        print("🔄 Utilisation ImageManager de secours")
                        return [self.create_placeholder_image("fallback", i) for i in range(num_images)]
                    
                    def create_placeholder_image(self, keyword, index):
                        from PIL import Image, ImageDraw
                        img = Image.new('RGB', (1280, 720), color=(70, 130, 180))
                        filename = f"placeholder_{keyword}_{index}.jpg"
                        filepath = safe_path_join("output/images", filename)
                        ensure_directory("output/images")
                        img.save(filepath)
                        return filepath
                
                self.image_manager = FallbackImageManager()
        return self.image_manager
    
    def _get_audio_generator(self):
        """Import différé de AudioGenerator"""
        if self.audio_generator is None:
            try:
                from content_factory.audio_generator import AudioGenerator
                self.audio_generator = AudioGenerator()
            except ImportError as e:
                print(f"❌ Erreur import AudioGenerator: {e}")
                # Fallback basique
                class FallbackAudioGenerator:
                    def generate_audio(self, text, title):
                        print("🔄 Utilisation AudioGenerator de secours")
                        clean_title = clean_filename(title)
                        audio_path = safe_path_join("output/audio", f"audio_{clean_title}.mp3")
                        ensure_directory("output/audio")
                        # Créer un fichier audio minimal
                        with open(audio_path, 'wb') as f:
                            f.write(b'')  # Fichier vide
                        return audio_path
                
                self.audio_generator = FallbackAudioGenerator()
        return self.audio_generator
    
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
                script = f"Contenu sur le thème: {title}"
                print("⚠️ Aucun script fourni, utilisation du titre comme script")
            
            clean_title = clean_filename(title)
            video_path = safe_path_join(self.output_dir, f"video_{clean_title}.mp4")
            
            print(f"📝 Titre vidéo: {title}")
            print(f"💾 Fichier de sortie: {video_path}")
            
            # Générer l'audio
            print("🔊 Génération de l'audio...")
            audio_generator = self._get_audio_generator()
            audio_path = audio_generator.generate_audio(script, title)
            
            if not audio_path or not os.path.exists(audio_path):
                print(f"❌ Audio non généré ou non trouvé: {audio_path}")
                # Créer un chemin d'audio de secours
                audio_path = safe_path_join("output/audio", f"audio_{clean_title}.mp3")
                ensure_directory("output/audio")
                with open(audio_path, 'wb') as f:
                    f.write(b'')  # Fichier vide comme fallback
            
            print(f"✅ Audio disponible: {audio_path}")
            
            # Obtenir des images pertinentes
            print("🖼️ Récupération des images...")
            image_manager = self._get_image_manager()
            image_paths = image_manager.get_images_for_content(content_data, num_images=8)
            
            if not image_paths:
                print("❌ Aucune image disponible, création d'images par défaut")
                image_paths = [image_manager.create_placeholder_image("default", i) for i in range(8)]
            
            print(f"✅ {len(image_paths)} images obtenues")
            
            # Créer la vidéo avec les images et l'audio
            print("🎥 Assemblage de la vidéo...")
            final_video_path = self.create_video_from_images_and_audio(image_paths, audio_path, video_path)
            
            print(f"✅ Vidéo créée avec succès: {final_video_path}")
            return final_video_path
            
        except Exception as e:
            print(f"❌ Erreur création vidéo: {e}")
            import traceback
            traceback.print_exc()
            
            # Tentative de fallback
            try:
                print("🔄 Tentative de vidéo de secours...")
                return self.create_fallback_video(content_data)
            except Exception as fallback_error:
                print(f"❌ Échec vidéo de secours: {fallback_error}")
                return None
    
    def create_simple_video(self, content_data):
        """
        Version simplifiée pour la compatibilité
        """
        return self.create_professional_video(content_data)
    
    def create_video_from_images_and_audio(self, image_paths, audio_path, output_path):
        """
        Crée une vidéo à partir d'images et d'audio
        """
        video_clips = []
        audio_clip = None
        final_video = None
        
        try:
            # Vérifier que l'audio existe
            if not os.path.exists(audio_path):
                raise Exception(f"Fichier audio introuvable: {audio_path}")
            
            # Charger l'audio avec gestion d'erreur
            print("🔊 Chargement de l'audio...")
            try:
                audio_clip = AudioFileClip(audio_path)
                audio_duration = audio_clip.duration
                
                if audio_duration <= 0:
                    print("⚠️ Durée audio nulle, utilisation durée par défaut")
                    audio_duration = 30.0  # Durée par défaut
            except Exception as audio_error:
                print(f"⚠️ Erreur chargement audio: {audio_error}")
                audio_duration = 30.0  # Durée par défaut
                audio_clip = None
            
            # Calculer la durée par image
            num_images = len(image_paths)
            duration_per_image = audio_duration / num_images if num_images > 0 else 5.0
            
            print(f"⏱️ Durée vidéo: {audio_duration:.2f}s")
            print(f"🖼️ Nombre d'images: {num_images}")
            print(f"⏰ Durée par image: {duration_per_image:.2f}s")
            
            # Créer les clips vidéo
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
                    except Exception as img_error:
                        print(f"⚠️ Image corrompue {image_path}: {img_error}")
                        continue
                    
                    print(f"📹 Création clip {i+1}/{num_images}: {os.path.basename(image_path)}")
                    
                    # Créer un clip image avec la durée calculée
                    image_clip = ImageClip(image_path, duration=duration_per_image)
                    
                    # Redimensionner pour format 16:9 (1920x1080)
                    try:
                        image_clip = image_clip.resize(height=1080)
                        
                        # Centrer l'image si nécessaire
                        if image_clip.w < 1920:
                            image_clip = image_clip.resize(width=1920)
                        elif image_clip.w > 1920:
                            # Recadrer au centre
                            image_clip = image_clip.crop(
                                x_center=image_clip.w/2, 
                                y_center=image_clip.h/2, 
                                width=1920, 
                                height=1080
                            )
                    except Exception as resize_error:
                        print(f"⚠️ Erreur redimensionnement image: {resize_error}")
                        # Continuer avec l'image originale
                    
                    video_clips.append(image_clip)
                    
                except Exception as e:
                    print(f"⚠️ Erreur création clip {i+1}: {e}")
                    continue
            
            if not video_clips:
                raise Exception("Aucun clip vidéo créé - toutes les images ont échoué")
            
            print(f"✅ {len(video_clips)} clips créés avec succès")
            
            # Concaténer tous les clips
            print("🎞️ Concaténation des clips...")
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Ajouter l'audio si disponible
            if audio_clip:
                print("🔊 Ajout de l'audio...")
                final_video = final_video.set_audio(audio_clip)
                final_video = final_video.set_duration(audio_duration)
            else:
                print("⚠️ Aucun audio disponible, vidéo silencieuse")
                final_video = final_video.set_duration(audio_duration)
            
            # Exporter la vidéo
            print("📤 Export de la vidéo...")
            final_video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac' if audio_clip else None,
                verbose=False,
                logger=None,
                threads=4,
                preset='medium',
                bitrate='2000k'
            )
            
            print(f"✅ Vidéo exportée: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur création vidéo from images: {e}")
            import traceback
            traceback.print_exc()
            
            # Nettoyer avant de relancer l'erreur
            self._cleanup_clips(video_clips, audio_clip, final_video)
            raise
        
        finally:
            # Nettoyer la mémoire dans tous les cas
            self._cleanup_clips(video_clips, audio_clip, final_video)
    
    def _cleanup_clips(self, video_clips, audio_clip, final_video):
        """
        Nettoie tous les clips de la mémoire
        """
        print("🧹 Nettoyage mémoire...")
        try:
            for clip in video_clips:
                try:
                    if hasattr(clip, 'close'):
                        clip.close()
                except Exception as e:
                    print(f"⚠️ Erreur fermeture clip: {e}")
            
            if audio_clip and hasattr(audio_clip, 'close'):
                try:
                    audio_clip.close()
                except Exception as e:
                    print(f"⚠️ Erreur fermeture audio: {e}")
            
            if final_video and hasattr(final_video, 'close'):
                try:
                    final_video.close()
                except Exception as e:
                    print(f"⚠️ Erreur fermeture vidéo: {e}")
                    
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage: {e}")
    
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
            image_manager = self._get_image_manager()
            image_path = image_manager.create_placeholder_image("secours", 0)
            
            # Créer un clip image simple
            image_clip = ImageClip(image_path, duration=10)
            
            # Exporter la vidéo sans audio
            image_clip.write_videofile(
                video_path,
                fps=24,
                verbose=False,
                logger=None
            )
            
            # Nettoyer
            self._cleanup_clips([image_clip], None, None)
            
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
        'title': 'Test Vidéo Creator Corrigé',
        'script': 'Ceci est un test de création vidéo avec le système complètement corrigé.',
        'category': 'test',
        'keywords': ['test', 'vidéo
