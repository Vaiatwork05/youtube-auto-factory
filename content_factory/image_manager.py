# content_factory/video_creator.py
import os
import sys
import time
import re
import traceback
from typing import Dict, Any, List, Optional

# Imports des dépendances des autres modules du projet
from content_factory.utils import clean_filename, safe_path_join, ensure_directory
# NOTE: AudioGenerator et ImageManager sont importés dans les méthodes pour la gestion des fallbacks (bon choix).

# --- CONSTANTES ---
DEFAULT_VIDEO_DIR = "output/videos"
DEFAULT_AUDIO_DIR = "output/audio"
DEFAULT_IMAGE_DIR = "output/images"
VIDEO_FPS = 24
VIDEO_CODEC = 'libx264'
AUDIO_CODEC = 'aac'
VIDEO_RESOLUTION = (1280, 720) # 720p (HD 16:9)

class VideoCreator:
    """
    Crée une vidéo en utilisant des clips images et un fichier audio.
    Gère les fallbacks pour l'audio, les images et la vidéo finale.
    """
    def __init__(self):
        self.output_dir = DEFAULT_VIDEO_DIR
        ensure_directory(self.output_dir)
    
    def create_professional_video(self, content_data: Dict[str, Any]) -> Optional[str]:
        """
        Fonction principale pour créer une vidéo, avec un meilleur nom.
        """
        try:
            print("\n🎬 Démarrage de la production vidéo...")
            
            title = content_data.get('title', 'Vidéo Automatique')
            script = content_data.get('script', 'Contenu généré.')
            clean_title = clean_filename(title)
            
            video_path = safe_path_join(self.output_dir, f"video_{clean_title}.mp4")
            
            print(f"📝 Titre: {title}")
            
            # --- ÉTAPE 1: Générer/Obtenir l'Audio ---
            audio_path = self._generate_audio(script, clean_title)
            if not audio_path or os.path.getsize(audio_path) < 1024:
                 raise RuntimeError("Échec de la génération audio ou fichier trop petit.")
            
            # --- ÉTAPE 2: Obtenir les Images ---
            num_images = 6 
            image_paths = self._get_images(content_data, num_images)
            
            if not image_paths:
                print("❌ Aucune image disponible (même les fallbacks ont échoué). Tentative de vidéo de secours.")
                # Renvoie un échec pour passer à la vidéo de secours globale
                return self._create_fallback_video(content_data)

            # --- ÉTAPE 3: Assembler la Vidéo ---
            print("🎥 Assemblage vidéo...")
            result_path = self._create_video_from_assets(image_paths, audio_path, video_path)
            
            if result_path and os.path.exists(result_path) and os.path.getsize(result_path) > 10 * 1024: # 10KB min
                file_size = os.path.getsize(result_path)
                print(f"✅ Vidéo créée avec succès: {result_path} ({file_size / (1024*1024):.2f} Mo)")
                return result_path
            else:
                # Échec de la création de la vidéo à partir des assets
                print("❌ Échec de la création du fichier final à partir des assets.")
                return self._create_fallback_video(content_data) # Tente le dernier secours
                
        except Exception as e:
            print(f"❌ Erreur critique dans create_professional_video: {e}")
            print("Tentative de vidéo de secours...")
            return self._create_fallback_video(content_data)
    
    # --- Méthodes d'Acquisition ---

    def _generate_audio(self, text: str, clean_title: str) -> Optional[str]:
        """Génère l'audio via AudioGenerator, avec fallback silencieux."""
        try:
            from content_factory.audio_generator import generate_audio as generate_proj_audio # Utilise la fonction d'export
            return generate_proj_audio(text, clean_title)
        except ImportError:
            print("⚠️ Module AudioGenerator non trouvé.")
        except Exception as e:
            print(f"⚠️ Erreur génération audio projet: {e}")
        
        # Fallback 1: Audio silencieux FFmpeg
        audio_path = safe_path_join(DEFAULT_AUDIO_DIR, f"audio_fallback_{clean_title}.mp3")
        ensure_directory(DEFAULT_AUDIO_DIR)
        try:
            import subprocess
            print("🔊 Fallback : Création d'un audio silencieux de 30s...")
            subprocess.run([
                'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-t', '30', '-acodec', 'libmp3lame', '-y', audio_path
            ], check=True, capture_output=True, timeout=30)
            return audio_path
        except Exception as e:
            print(f"⚠️ Erreur FFmpeg pour audio silencieux: {e}")
            return None # Échec total de l'audio

    def _get_images(self, content_data: Dict[str, Any], num_images: int) -> List[str]:
        """Récupère des images via ImageManager, avec fallback sur des images générées."""
        images = []
        try:
            from content_factory.image_manager import ImageManager
            manager = ImageManager()
            images = manager.get_images_for_content(content_data, num_images)
        except ImportError:
             print("⚠️ Module ImageManager non trouvé.")
        except Exception as e:
            print(f"⚠️ Erreur récupération images projet: {e}")
        
        # Fallback 1: Images de secours internes
        if not images or len(images) < num_images:
            print(f"🖼️ Fallback : Création de {num_images} images de secours simples.")
            images = self._create_fallback_images(num_images, content_data.get('title', 'Placeholder'))

        return images
    
    def _create_fallback_images(self, num_images: int, base_title: str) -> List[str]:
        """Crée des images de secours simples (nécessite PIL)."""
        images = []
        ensure_directory(DEFAULT_IMAGE_DIR)
        
        try:
            from PIL import Image, ImageDraw, ImageFont
            for i in range(num_images):
                img_path = safe_path_join(DEFAULT_IMAGE_DIR, f"placeholder_{clean_filename(base_title)}_{i}.jpg")
                text = f"ERREUR IMAGES - Clip {i+1}"
                self._create_simple_image(img_path, text)
                images.append(img_path)
            return images
        except ImportError:
            print("❌ La bibliothèque PIL n'est pas installée. Impossible de créer des images de secours.")
            return []

    # --- Méthodes de Support ---

    def _create_simple_image(self, path: str, text: str):
        """Crée une image simple 1280x720 avec texte (nécessite PIL)."""
        from PIL import Image, ImageDraw, ImageFont # Imports supposés réussis ici
        
        img = Image.new('RGB', VIDEO_RESOLUTION, color=(53, 94, 159))
        draw = ImageDraw.Draw(img)
        
        try:
            # Tente Arial, sinon Fallback sur la police du système ou la police par défaut
            font = ImageFont.truetype("arial.ttf", 60)
        except Exception:
             try:
                # Chemin typique sur Linux (pour GitHub Actions)
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
             except Exception:
                font = ImageFont.load_default()
        
        # Centrer le texte (Calcul de la Bbox plus précis pour le centrage)
        # Nécessite PIL 8.0+ pour draw.textbbox
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (VIDEO_RESOLUTION[0] - text_width) // 2
        y = (VIDEO_RESOLUTION[1] - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        img.save(path, quality=85)
    
    # --- Méthode d'Assemblage Critique ---

    def _create_video_from_assets(self, image_paths: List[str], audio_path: str, output_path: str) -> Optional[str]:
        """Assemble les clips vidéo et audio (nécessite moviepy)."""
        try:
            from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
        except ImportError:
            print("❌ La bibliothèque moviepy n'est pas installée. Impossible d'assembler la vidéo.")
            return None

        # Vérifications
        if not os.path.exists(audio_path) or not image_paths:
            print("Erreur assets: Fichier audio ou images manquants.")
            return None
        
        try:
            # Durée et calcul
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            if audio_duration < 1.0: # Minimum 1 seconde
                audio_duration = 10.0
                print("⚠️ Durée audio trop courte (< 1s), ajustée à 10s.")
            
            duration_per_image = audio_duration / len(image_paths)
            
            print(f"⏱️ Durée audio: {audio_duration:.1f}s | ⏰ Durée/image: {duration_per_image:.1f}s")
            
            # Créer les clips images
            video_clips = []
            for i, img_path in enumerate(image_paths):
                # Utiliser la taille fixée et s'assurer que l'image est redimensionnée pour le format 16:9
                clip = ImageClip(img_path, duration=duration_per_image).set_opacity(1.0)
                # Redimensionnement avec mise à l'échelle pour s'adapter à la résolution (remplace le resize height=720)
                clip = clip.resize(newsize=VIDEO_RESOLUTION) 
                video_clips.append(clip)
            
            # Concaténer
            final_video = concatenate_videoclips(video_clips, method="compose")
            final_video = final_video.set_audio(audio_clip)
            final_video = final_video.set_duration(audio_duration)
            
            # Exporter avec paramètres optimisés
            final_video.write_videofile(
                output_path,
                fps=VIDEO_FPS,
                codec=VIDEO_CODEC,
                audio_codec=AUDIO_CODEC,
                bitrate='5000k', # Augmentation du bitrate pour meilleure qualité (5 Mbps est bon pour 720p)
                verbose=False,
                logger=None,
                threads=4
            )
            
            return output_path
            
        finally:
            # Nettoyage des ressources (très important pour les performances en CI)
            if 'audio_clip' in locals(): audio_clip.close()
            if 'video_clips' in locals(): 
                for clip in video_clips: clip.close()
            if 'final_video' in locals(): final_video.close()

    # --- Méthode de Secours Ultime ---

    def _create_fallback_video(self, content_data: Dict[str, Any]) -> Optional[str]:
        """Crée une vidéo de secours ultra simple (10s image fixe)."""
        try:
            from moviepy.editor import ImageClip
            from PIL import Image
        except ImportError:
            print("❌ moviepy/PIL manquant. Impossible de créer une vidéo de secours.")
            return None

        title = content_data.get('title', 'Vidéo Secours')
        video_path = safe_path_join(self.output_dir, f"fallback_{clean_filename(title)}.mp4")
        
        # 1. Créer l'image de secours
        img_path = safe_path_join(DEFAULT_IMAGE_DIR, "fallback_ultra.jpg")
        ensure_directory(DEFAULT_IMAGE_DIR)
        self._create_simple_image(img_path, f"Échec Critique - {title[:30]}")
        
        # 2. Créer la vidéo
        clip = ImageClip(img_path, duration=10)
        clip = clip.resize(newsize=VIDEO_RESOLUTION)
        
        # Exportation simple
        clip.write_videofile(
            video_path,
            fps=VIDEO_FPS,
            codec=VIDEO_CODEC,
            verbose=False,
            logger=None
        )
        clip.close()
        
        print(f"✅ Vidéo de secours finale créée: {video_path}")
        return video_path
        
    # La fonction _clean_filename est supprimée car elle est maintenant dans utils.py

# --- Fonction d'Export ---
def create_video(content_data: Dict[str, Any]) -> Optional[str]:
    """Fonction principale pour créer une vidéo"""
    creator = VideoCreator()
    return creator.create_professional_video(content_data)

# --- Bloc de Test ---
if __name__ == "__main__":
    print("🧪 Test VideoCreator...")
    
    # Simulation de données (pour éviter les dépendances réelles des autres modules lors du test)
    class MockAudioGenerator:
        def generate_audio(self, text, title):
            # Créer un fichier audio silencieux temporaire pour le test
            audio_path = os.path.join(DEFAULT_AUDIO_DIR, "test_audio.mp3")
            ensure_directory(DEFAULT_AUDIO_DIR)
            try:
                import subprocess
                subprocess.run(['ffmpeg', '-f', 'lavfi', '-i', 'anullsrc', '-t', '5', '-y', audio_path], check=True, capture_output=True, timeout=10)
                return audio_path
            except: return None
            
    class MockImageManager:
        def get_images_for_content(self, content_data, num_images):
            # Créer des images temporaires pour le test
            images = []
            ensure_directory(DEFAULT_IMAGE_DIR)
            try:
                from PIL import Image
                for i in range(num_images):
                    img_path = os.path.join(DEFAULT_IMAGE_DIR, f"test_img_{i}.jpg")
                    Image.new('RGB', (1280, 720), color=(150, 150, i*30)).save(img_path)
                    images.append(img_path)
                return images
            except: return []

    # Injecter les mocks pour le test (simule l'import si nécessaire)
    sys.modules['content_factory.audio_generator'] = type('module', (object,), {'generate_audio': MockAudioGenerator().generate_audio})
    sys.modules['content_factory.image_manager'] = type('module', (object,), {'ImageManager': MockImageManager})

    test_data = {
        'title': 'Test Vidéo Fonctionnel',
        'script': 'Ceci est un test du système de création vidéo pour vérifier l’assemblage final.',
        'keywords': ['test', 'video', 'systeme']
    }
    
    creator = VideoCreator()
    result = creator.create_professional_video(test_data)
    
    if result and os.path.exists(result):
        print(f"\n✅ Test réussi. Fichier généré: {result}")
        # Nettoyage optionnel
        # os.remove(result)
        sys.exit(0)
    else:
        print("\n❌ Test échoué. Vérifiez que moviepy, ffmpeg et PIL sont installés.")
        sys.exit(1)
