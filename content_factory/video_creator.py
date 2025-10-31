# content_factory/video_creator.py (VERSION CORRIGÉE)

import os
import time
import random
from typing import Dict, List, Any, Optional
from PIL import Image, ImageDraw, ImageFont

# Gestion des imports MoviePy
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False
    print("⚠️ MoviePy non disponible")

from content_factory.utils import clean_filename, safe_path_join, ensure_directory
from content_factory.config_loader import ConfigLoader
from content_factory.image_manager import get_images
from content_factory.audio_generator import generate_audio  # NOUVELLE SIGNATURE

class VideoCreator:
    """Créateur de vidéos avec support de la musique automatique."""
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.video_config = self.config.get('VIDEO_CREATOR', {})
        self.paths = self.config.get('PATHS', {})
        
        # CONFIGURATION DYNAMIQUE
        self.resolution = (1080, 1920)
        self.target_fps = 30
        self.max_duration = int(os.getenv('MAX_AUDIO_DURATION', 120))
        self.min_duration = int(os.getenv('MIN_AUDIO_DURATION', 15))
        
        # Chemins
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        video_dir = self.paths.get('VIDEO_DIR', 'videos')
        self.output_dir = safe_path_join(output_root, video_dir)
        ensure_directory(self.output_dir)
        
        print("🎬 VideoCreator - Intégration musique activée")

    def create_professional_video(self, content_data: Dict[str, Any]) -> Optional[str]:
        """Crée une vidéo avec support de la musique automatique."""
        print(f"\n🎬 CRÉATION SHORTS: {content_data['title']}")
        
        try:
            # 1. PRÉPARATION DES ASSETS
            assets = self._prepare_assets(content_data)
            if not assets:
                return None
            
            # 2. GÉNÉRATION AUDIO AVEC CONTENT_DATA POUR LA MUSIQUE
            script_for_tts = self._extract_clean_script(content_data)
            
            # CRITIQUE: Passage de content_data pour la recherche de musique
            audio_path = generate_audio(script_for_tts, content_data['title'], content_data)
            
            if not audio_path or not os.path.exists(audio_path):
                print("❌ Échec génération audio")
                return None
            
            # 3. MESURER LA DURÉE RÉELLE
            audio_duration = self._measure_audio_duration(audio_path)
            print(f"⏱️ Durée audio: {audio_duration:.1f} secondes")
            
            # Validation de la durée
            if audio_duration < self.min_duration:
                print(f"⚠️ Audio trop court ({audio_duration:.1f}s), utilisation durée minimum")
                audio_duration = self.min_duration
            elif audio_duration > self.max_duration:
                print(f"⚠️ Audio trop long ({audio_duration:.1f}s), tronqué à {self.max_duration}s")
                audio_duration = self.max_duration
            
            # 4. CRÉER LA VIDÉO AVEC LA DURÉE EXACTE
            final_video_path = self._create_adaptive_video(content_data, assets, audio_path, audio_duration)
            
            # Nettoyage
            self._cleanup_temp_files([audio_path] + assets.get('image_paths', []))
            
            return final_video_path
            
        except Exception as e:
            print(f"❌ Erreur création vidéo: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _extract_clean_script(self, content_data: Dict[str, Any]) -> str:
        """Extrait et nettoie le script pour le TTS."""
        script = content_data.get('script', '')
        
        # Pour les Shorts, on peut raccourcir légèrement si nécessaire
        if len(script) > 1000:
            print("📝 Script long détecté, optimisation pour Shorts...")
            lignes = script.split('\n')
            lignes_importantes = [l for l in lignes if any(mot in l for mot in ['Numéro', '💡', '🎯'])]
            script = '\n'.join(lignes_importantes[:20])
        
        return script

    def _prepare_assets(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare les assets en fonction du contenu."""
        print("🖼️ Préparation des assets...")
        
        # Récupérer les images
        image_paths = get_images(content_data, num_images=8)
        
        if not image_paths:
            print("❌ Aucune image disponible")
            return {}
        
        # Redimensionner pour Shorts
        processed_images = []
        for img_path in image_paths:
            processed_path = self._resize_for_shorts(img_path)
            if processed_path:
                processed_images.append(processed_path)
        
        return {
            'image_paths': processed_images,
            'content_data': content_data  # IMPORTANT: Garder les données
        }

    def _resize_for_shorts(self, image_path: str) -> Optional[str]:
        """Redimensionne une image pour le format 9:16."""
        try:
            img = Image.open(image_path)
            target_width, target_height = self.resolution
            
            # Redimensionner en gardant le ratio
            img_ratio = img.width / img.height
            target_ratio = target_width / target_height
            
            if img_ratio > target_ratio:
                new_height = target_height
                new_width = int(img.width * (target_height / img.height))
            else:
                new_width = target_width
                new_height = int(img.height * (target_width / img.width))
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Recadrer au centre
            left = (new_width - target_width) / 2
            top = (new_height - target_height) / 2
            right = (new_width + target_width) / 2
            bottom = (new_height + target_height) / 2
            
            img = img.crop((left, top, right, bottom))
            
            # Sauvegarder
            output_path = image_path.replace('.jpg', '_shorts.jpg')
            img.save(output_path, 'JPEG', quality=85)
            
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur redimensionnement: {e}")
            return None

    def _measure_audio_duration(self, audio_path: str) -> float:
        """Mesure la durée réelle du fichier audio."""
        if not HAS_MOVIEPY:
            return 45.0
        
        try:
            audio_clip = AudioFileClip(audio_path)
            duree = audio_clip.duration
            audio_clip.close()
            return duree
        except Exception as e:
            print(f"⚠️ Erreur mesure durée audio: {e}")
            return 45.0

    def _create_adaptive_video(self, content_data: Dict[str, Any], assets: Dict[str, Any], 
                             audio_path: str, audio_duration: float) -> Optional[str]:
        """Crée une vidéo qui s'adapte parfaitement à l'audio."""
        if not HAS_MOVIEPY:
            print("❌ MoviePy non disponible")
            return None
        
        try:
            # Charger l'audio avec sa durée réelle
            audio_clip = AudioFileClip(audio_path)
            video_duration = min(audio_clip.duration, self.max_duration)
            audio_clip = audio_clip.subclip(0, video_duration)
            
            print(f"🎬 Création vidéo de {video_duration:.1f} secondes")
            
            # Créer les clips vidéo adaptés
            video_clips = self._create_adaptive_clips(assets, video_duration)
            
            if not video_clips:
                print("❌ Aucun clip vidéo créé")
                return None
            
            # Assembler la vidéo
            final_video = self._assemble_video(video_clips, audio_clip)
            
            # Exporter
            filename = f"shorts_{clean_filename(content_data['title'])}.mp4"
            output_path = safe_path_join(self.output_dir, filename)
            
            print("📤 Exportation en cours...")
            final_video.write_videofile(
                output_path,
                fps=self.target_fps,
                codec='libx264',
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None
            )
            
            # Fermer les clips
            final_video.close()
            audio_clip.close()
            for clip in video_clips:
                clip.close()
            
            print(f"✅ Vidéo créée: {output_path}")
            print(f"📏 Durée finale: {video_duration:.1f}s")
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur création vidéo: {e}")
            return None

    def _create_adaptive_clips(self, assets: Dict[str, Any], total_duration: float) -> List[Any]:
        """Crée des clips vidéo adaptés à la durée totale."""
        if not HAS_MOVIEPY:
            return []
        
        image_paths = assets.get('image_paths', [])
        if not image_paths:
            return []
        
        clips = []
        
        # Calculer les durées pour remplir toute la durée audio
        durations = self._calculate_adaptive_durations(len(image_paths), total_duration)
        
        for i, img_path in enumerate(image_paths):
            if i >= len(durations):
                break
                
            try:
                clip = ImageClip(img_path, duration=durations[i])
                clip = clip.resize(height=self.resolution[1])
                clip = clip.set_position(('center', 'center'))
                clips.append(clip)
            except Exception as e:
                print(f"❌ Erreur clip {i}: {e}")
                continue
        
        return clips

    def _calculate_adaptive_durations(self, num_images: int, total_duration: float) -> List[float]:
        """Calcule des durées qui remplissent exactement la durée audio."""
        if num_images == 0:
            return []
        
        # Durée par image (variée pour un bon rythme)
        min_duration = float(os.getenv('MIN_IMAGE_DURATION', '2.5'))
        max_duration = float(os.getenv('MAX_IMAGE_DURATION', '5.0'))
        
        base_duration = random.uniform(min_duration, max_duration)
        durations = [base_duration * random.uniform(0.8, 1.2) for _ in range(num_images)]
        
        # Ajuster pour atteindre exactement la durée cible
        total_current = sum(durations)
        if total_current > 0:
            adjustment_factor = total_duration / total_current
            durations = [d * adjustment_factor for d in durations]
        
        print(f"   ⏱️ Durées images: {[f'{d:.1f}s' for d in durations]}")
        return durations

    def _assemble_video(self, video_clips: List[Any], audio_clip: Any) -> Any:
        """Assemble la vidéo finale."""
        if len(video_clips) > 1:
            final_video = concatenate_videoclips(video_clips, method="compose")
        else:
            final_video = video_clips[0]
        
        # Ajouter l'audio avec sa durée exacte
        final_video = final_video.set_audio(audio_clip)
        final_video = final_video.set_duration(audio_clip.duration)
        
        return final_video

    def _cleanup_temp_files(self, files: List[str]):
        """Nettoie les fichiers temporaires."""
        for file in files:
            try:
                if os.path.exists(file) and any(word in file for word in ['_shorts.jpg', 'audio_']):
                    if 'shorts_' not in file:  # Garder les vidéos finales
                        os.remove(file)
            except Exception as e:
                print(f"⚠️ Impossible de supprimer {file}: {e}")

def create_video(content_data: Dict[str, Any]) -> Optional[str]:
    """Fonction d'export principale."""
    try:
        creator = VideoCreator()
        return creator.create_professional_video(content_data)
    except Exception as e:
        print(f"❌ Erreur création vidéo: {e}")
        return None
