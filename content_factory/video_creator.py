# content_factory/video_creator.py (Intégration config.yaml)

import os
import sys
import time
import re
import traceback
import subprocess
from typing import Dict, Any, List, Optional, Tuple

# Import centralisé des dépendances
from content_factory.utils import clean_filename, safe_path_join, ensure_directory
from content_factory.config_loader import ConfigLoader # Import critique pour la configuration
from PIL import Image, ImageDraw, ImageFont # Import anticipé pour les fallbacks PIL
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips # Import anticipé pour l'assemblage

# --- CONSTANTES TECHNIQUES (NON NÉCESSITANT PAS D'ÊTRE DANS CONFIG) ---
VIDEO_CODEC = 'libx264'
AUDIO_CODEC = 'aac'

class VideoCreator:
    """
    Crée une vidéo en utilisant des clips images et un fichier audio, en s'appuyant
    sur les paramètres définis dans config.yaml.
    """
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.video_config = self.config['VIDEO_CREATOR']
        self.paths = self.config['PATHS']
        
        # Chemins basés sur la configuration
        self.output_dir = safe_path_join(self.paths['OUTPUT_ROOT'], self.paths['VIDEO_DIR'])
        self.audio_dir = safe_path_join(self.paths['OUTPUT_ROOT'], self.paths['AUDIO_DIR'])
        self.image_dir = safe_path_join(self.paths['OUTPUT_ROOT'], self.paths['IMAGE_DIR'])
        
        # Paramètres configurables
        self.resolution: Tuple[int, int] = tuple(self.video_config.get('RESOLUTION', [1280, 720]))
        self.fps: int = self.video_config.get('FPS', 24)
        self.bitrate: str = self.video_config.get('BITRATE', '5000k')
        self.num_images: int = self.video_config.get('IMAGES_PER_VIDEO', 10)
        self.fallback_duration_s: int = self.video_config.get('FALLBACK_DURATION_S', 15)
        
        ensure_directory(self.output_dir)
    
    def create_professional_video(self, content_data: Dict[str, Any]) -> Optional[str]:
        """Fonction principale pour créer une vidéo."""
        try:
            print("\n🎬 Démarrage de la production vidéo...")
            
            title = content_data.get('title', 'Vidéo Automatique')
            script = content_data.get('script', 'Contenu généré.')
            clean_title = clean_filename(title)
            
            video_path = safe_path_join(self.output_dir, f"video_{clean_title}.mp4")
            
            # --- ÉTAPE 1: Générer/Obtenir l'Audio ---
            audio_path = self._generate_audio(script, clean_title)
            if not audio_path or os.path.getsize(audio_path) < 1024:
                 raise RuntimeError("Échec de la génération audio ou fichier trop petit.")
            
            # --- ÉTAPE 2: Obtenir les Images ---
            image_paths = self._get_images(content_data, self.num_images)
            
            if not image_paths:
                print("❌ Aucune image disponible. Tentative de vidéo de secours.")
                return self._create_fallback_video(content_data)

            # --- ÉTAPE 3: Assembler la Vidéo ---
            print("🎥 Assemblage vidéo...")
            result_path = self._create_video_from_assets(image_paths, audio_path, video_path)
            
            # 100 KB minimum
            if result_path and os.path.exists(result_path) and os.path.getsize(result_path) > 100 * 1024: 
                file_size = os.path.getsize(result_path)
                print(f"✅ Vidéo créée avec succès: {result_path} ({file_size / (1024*1024):.2f} Mo)")
                return result_path
            else:
                print("❌ Échec de la création du fichier final à partir des assets.")
                return self._create_fallback_video(content_data)
                
        except Exception as e:
            print(f"❌ Erreur critique dans create_professional_video: {e}")
            traceback.print_exc(file=sys.stdout) # Affichage de la trace en mode debug
            print("Tentative de vidéo de secours...")
            return self._create_fallback_video(content_data)
    
    # --- Méthodes d'Acquisition (Utilise les chemins configurés) ---

    def _generate_audio(self, text: str, clean_title: str) -> Optional[str]:
        """Génère l'audio via AudioGenerator, avec fallback silencieux."""
        try:
            from content_factory.audio_generator import generate_audio as generate_proj_audio
            return generate_proj_audio(text, clean_title)
        except ImportError:
            print("⚠️ Module AudioGenerator non trouvé.")
        except Exception as e:
            print(f"⚠️ Erreur génération audio projet: {e}")
        
        # Fallback 1: Audio silencieux FFmpeg (basé sur la durée de secours configurée)
        audio_path = safe_path_join(self.audio_dir, f"audio_fallback_{clean_title}.mp3")
        try:
            print(f"🔊 Fallback : Création d'un audio silencieux de {self.fallback_duration_s}s...")
            subprocess.run([
                'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
                '-t', str(self.fallback_duration_s), '-acodec', 'libmp3lame', '-y', audio_path
            ], check=True, capture_output=True, timeout=30)
            return audio_path
        except Exception as e:
            print(f"⚠️ Erreur FFmpeg pour audio silencieux: {e}")
            return None

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
        """Crée des images de secours simples (nécessite PIL) dans le répertoire configuré."""
        images = []
        ensure_directory(self.image_dir)
        
        try:
            for i in range(num_images):
                img_path = safe_path_join(self.image_dir, f"placeholder_{clean_filename(base_title)}_{i}.jpg")
                text = f"ERREUR IMAGES - Clip {i+1}"
                self._create_simple_image(img_path, text)
                images.append(img_path)
            return images
        except Exception:
            print("❌ La bibliothèque PIL n'est pas installée ou erreur. Impossible de créer des images de secours.")
            return []

    def _create_simple_image(self, path: str, text: str):
        """Crée une image simple avec résolution configurable (nécessite PIL)."""
        
        # Résolution de l'image de secours basée sur la configuration
        img = Image.new('RGB', self.resolution, color=(53, 94, 159))
        draw = ImageDraw.Draw(img)
        
        try:
            # Essayer une police commune en CI/CD
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
        except Exception:
            # Fallback
            font = ImageFont.load_default()
        
        # Centrage du texte
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.resolution[0] - text_width) // 2
        y = (self.resolution[1] - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        img.save(path, quality=85)
    
    # --- Méthode d'Assemblage Critique ---

    def _create_video_from_assets(self, image_paths: List[str], audio_path: str, output_path: str) -> Optional[str]:
        """Assemble les clips vidéo et audio (nécessite moviepy)."""
        
        # Vérifications
        if not os.path.exists(audio_path) or not image_paths:
            print("Erreur assets: Fichier audio ou images manquants.")
            return None
        
        try:
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            if audio_duration < 1.0:
                audio_duration = self.fallback_duration_s
                print(f"⚠️ Durée audio trop courte (< 1s), ajustée à {self.fallback_duration_s}s (fallback).")
            
            duration_per_image = audio_duration / len(image_paths)
            
            print(f"⏱️ Durée audio: {audio_duration:.1f}s | ⏰ Durée/image: {duration_per_image:.1f}s")
            
            # Créer les clips images
            video_clips = []
            for i, img_path in enumerate(image_paths):
                clip = ImageClip(img_path, duration=duration_per_image)
                # Redimensionnement à la résolution configurée
                clip = clip.resize(newsize=self.resolution) 
                video_clips.append(clip)
            
            # Concaténer et synchroniser
            final_video = concatenate_videoclips(video_clips, method="compose")
            final_video = final_video.set_audio(audio_clip)
            final_video = final_video.set_duration(audio_duration)
            
            # Exporter avec paramètres configurés
            final_video.write_videofile(
                output_path,
                fps=self.fps,
                codec=VIDEO_CODEC,
                audio_codec=AUDIO_CODEC,
                bitrate=self.bitrate, 
                verbose=False,
                logger=None,
                threads=4
            )
            
            return output_path
            
        finally:
            # Nettoyage des ressources
            if 'audio_clip' in locals() and audio_clip: audio_clip.close()
            if 'video_clips' in locals(): 
                for clip in video_clips: 
                    if clip: clip.close()
            if 'final_video' in locals() and final_video: final_video.close()

    # --- Méthode de Secours Ultime ---

    def _create_fallback_video(self, content_data: Dict[str, Any]) -> Optional[str]:
        """Crée une vidéo de secours ultra simple (image fixe et durée de secours)."""
        
        title = content_data.get('title', 'Vidéo Secours')
        video_path = safe_path_join(self.output_dir, f"fallback_{clean_filename(title)}.mp4")
        
        # 1. Créer l'image de secours
        img_path = safe_path_join(self.image_dir, "fallback_ultra.jpg")
        ensure_directory(self.image_dir)
        self._create_simple_image(img_path, f"Échec Critique - {title[:30]}")
        
        # 2. Créer la vidéo
        clip = ImageClip(img_path, duration=self.fallback_duration_s)
        clip = clip.resize(newsize=self.resolution)
        
        # Exportation simple
        clip.write_videofile(
            video_path,
            fps=self.fps,
            codec=VIDEO_CODEC,
            verbose=False,
            logger=None
        )
        clip.close()
        
        print(f"✅ Vidéo de secours finale créée: {video_path}")
        return video_path
        
# --- Fonction d'Export ---
def create_video(content_data: Dict[str, Any]) -> Optional[str]:
    """Fonction principale pour créer une vidéo"""
    creator = VideoCreator()
    return creator.create_professional_video(content_data)

# --- Bloc de Test (Non modifié, nécessite toujours les mocks pour fonctionner) ---
# ...
