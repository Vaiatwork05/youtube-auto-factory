# content_factory/video_creator.py (VERSION COMPLÈTE AVEC MUSIC MANAGER)

import os
import time
import random
from typing import Dict, List, Any, Optional
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import numpy as np

try:
    from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
    from moviepy.audio.AudioClip import AudioClip
    from moviepy.video.fx.all import fadein, fadeout
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False
    print("❌ MoviePy non disponible")

from content_factory.utils import clean_filename, safe_path_join, ensure_directory
from content_factory.config_loader import ConfigLoader
from content_factory.image_manager import get_images

try:
    from content_factory.audio_generator import generate_audio
    HAS_AUDIO_GENERATOR = True
except ImportError:
    HAS_AUDIO_GENERATOR = False
    print("❌ AudioGenerator non disponible")

# =============================================================================
# IMPORT MUSIC MANAGER - CORRECTION AJOUTÉE
# =============================================================================

try:
    from content_factory.music_manager import MusicManager
    HAS_MUSIC_MANAGER = True
    print("✅ MusicManager disponible")
except ImportError as e:
    HAS_MUSIC_MANAGER = False
    print(f"❌ MusicManager indisponible: {e}")
except Exception as e:
    HAS_MUSIC_MANAGER = False
    print(f"❌ Erreur chargement MusicManager: {e}")

class BrainrotVideoCreator:
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.video_config = self.config.get('VIDEO_CREATOR', {})
        self.paths = self.config.get('PATHS', {})
        
        # 🔥 CORRECTION : Dimensions paires garanties pour H.264
        self.resolution = (1920, 1080)  # Format paysage standard (pairs)
        self.target_fps = 30
        self.max_duration = 59
        
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        video_dir = self.paths.get('VIDEO_DIR', 'videos')
        self.output_dir = safe_path_join(output_root, video_dir)
        ensure_directory(self.output_dir)
        
        # Configuration musique
        self.music_enabled = os.getenv('BACKGROUND_MUSIC_ENABLED', 'false').lower() == 'true'
        self.music_volume = float(os.getenv('BACKGROUND_MUSIC_VOLUME', '0.25'))
        
        print("🎬 BrainrotVideoCreator - Qualité MAX 1080p (H.264 Compatible)")
        print(f"🎵 Musique: {'✅ ACTIVÉE' if self.music_enabled else '❌ DÉSACTIVÉE'}")

    def create_video(self, content_data: Dict[str, Any], output_dir: str = None) -> Optional[str]:
        """Crée une vidéo brainrot - Version robuste avec gestion d'erreurs"""
        if output_dir:
            self.output_dir = output_dir
            ensure_directory(self.output_dir)
        
        return self.create_brainrot_video(content_data)

    def create_brainrot_video(self, content_data: Dict[str, Any]) -> Optional[str]:
        """Crée une vidéo brainrot ultra-optimisée avec musique"""
        print(f"\n🎬 CRÉATION BRAINROT ULTRA: {content_data['title']}")
        
        try:
            # Phase 1: Préparation des assets
            assets = self._prepare_ultra_assets(content_data)
            if not assets:
                print("❌ Aucun asset préparé")
                return None

            # Phase 2: Génération audio principal
            audio_path, audio_duration = self._generate_ultra_audio(content_data)
            if not audio_path:
                print("❌ Aucun audio généré")
                return None

            # Phase 3: Composition vidéo avec musique
            final_video_path = self._create_ultra_composition(content_data, assets, audio_path, audio_duration)
            
            if final_video_path and os.path.exists(final_video_path):
                file_size = os.path.getsize(final_video_path) / (1024 * 1024)
                print(f"🎉 VIDÉO ULTRA CRÉÉE: {final_video_path} ({file_size:.1f}MB)")
                self._cleanup_temp_files([audio_path] + assets.get('temp_files', []))
                return final_video_path
            
            print("❌ Aucun chemin vidéo retourné")
            return None
                
        except Exception as e:
            print(f"💥 ERREUR: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _prepare_ultra_assets(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare les assets visuels avec gestion d'erreur"""
        asset_paths = get_images(content_data, num_images=12)
        if not asset_paths:
            print("❌ Aucun asset path récupéré")
            return {}

        processed_assets = []
        temp_files = []
        
        for i, asset_path in enumerate(asset_paths):
            try:
                if asset_path.endswith('.gif'):
                    processed_path = self._process_ultra_gif(asset_path, i)
                else:
                    processed_path = self._apply_ultra_style(asset_path, content_data, i)
                
                if processed_path and processed_path != asset_path:
                    temp_files.append(processed_path)
                processed_assets.append(processed_path or asset_path)
                
            except Exception as e:
                print(f"⚠️ Erreur asset {i}: {e}")
                processed_assets.append(asset_path)  # Utiliser l'original en fallback
        
        print(f"📊 Assets ULTRA: {len(processed_assets)}")
        return {'asset_paths': processed_assets, 'temp_files': temp_files}

    def _apply_ultra_style(self, image_path: str, content_data: Dict, index: int) -> Optional[str]:
        """Applique le style brainrot aux images"""
        try:
            with Image.open(image_path) as img:
                img = self._resize_ultra_quality(img)
                
                if content_data.get('is_part1', True):
                    img = self._apply_mystery_ultra(img, index)
                else:
                    img = self._apply_shock_ultra(img, index)
                
                img = self._add_animated_borders(img, index)
                img = self._enhance_ultra_quality(img)
                
                base, ext = os.path.splitext(image_path)
                output_path = f"{base}_ultra{ext}"
                img.save(output_path, 'JPEG', quality=95, optimize=True, subsampling=0)
                
                return output_path
        except Exception as e:
            print(f"⚠️ Style ULTRA: {e}")
            return None

    def _resize_ultra_quality(self, img: Image.Image) -> Image.Image:
        """Redimensionne l'image avec dimensions paires pour H.264"""
        target_width, target_height = self.resolution
        
        # 🔥 CORRECTION : Garantir des dimensions paires
        target_width = target_width if target_width % 2 == 0 else target_width - 1
        target_height = target_height if target_height % 2 == 0 else target_height - 1
        
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            new_height = target_height
            new_width = int(img.width * (target_height / img.height))
        else:
            new_width = target_width
            new_height = int(img.height * (target_width / img.width))
        
        # 🔥 CORRECTION : Garantir des dimensions paires pour le resize
        new_width = new_width if new_width % 2 == 0 else new_width - 1
        new_height = new_height if new_height % 2 == 0 else new_height - 1
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        return img.crop((left, top, right, bottom))

    def _apply_mystery_ultra(self, img: Image.Image, index: int) -> Image.Image:
        """Style mystère pour partie 1"""
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)
        
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.9)
        
        if index % 3 == 0:
            img = img.filter(ImageFilter.GaussianBlur(0.8))
        
        return img

    def _apply_shock_ultra(self, img: Image.Image, index: int) -> Image.Image:
        """Style choc pour partie 2"""
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.5)
        
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.6)
        
        img = img.filter(ImageFilter.SHARPEN)
        
        if index % 2 == 0:
            img = img.filter(ImageFilter.EDGE_ENHANCE)
        
        return img

    def _add_animated_borders(self, img: Image.Image, index: int) -> Image.Image:
        """Ajoute des bordures animées"""
        border_size = 5
        colors = [(255, 0, 0), (0, 255, 255), (255, 255, 0), (0, 0, 255)]
        border_color = colors[index % len(colors)]
        
        new_img = Image.new('RGB', (img.width + border_size*2, img.height + border_size*2), border_color)
        new_img.paste(img, (border_size, border_size))
        
        return new_img

    def _enhance_ultra_quality(self, img: Image.Image) -> Image.Image:
        """Améliore la qualité de l'image"""
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(1.2)
        return img

    def _process_ultra_gif(self, gif_path: str, index: int) -> Optional[str]:
        """Traite les GIFs (placeholder)"""
        return None

    def _generate_ultra_audio(self, content_data: Dict) -> tuple[Optional[str], float]:
        """Génère l'audio avec gestion de durée"""
        if not HAS_AUDIO_GENERATOR:
            return self._create_ultra_fallback_audio(content_data)
        
        try:
            script = content_data.get('script', '')
            title = content_data.get('title', '')
            
            audio_path = generate_audio(script, title, content_data)
            
            if audio_path and os.path.exists(audio_path):
                duration = self._measure_audio_duration(audio_path)
                if duration > 0:
                    return audio_path, duration
            
            return self._create_ultra_fallback_audio(content_data)
        except Exception as e:
            print(f"❌ Audio ULTRA: {e}")
            return self._create_ultra_fallback_audio(content_data)

    def _create_ultra_fallback_audio(self, content_data: Dict) -> tuple[Optional[str], float]:
        """Audio de fallback"""
        if not HAS_MOVIEPY:
            return None, 45.0
        
        try:
            duration = random.uniform(45.0, 55.0)
            silent_clip = AudioClip(lambda t: 0, duration=duration)
            
            filename = f"ultra_fallback_audio_{int(time.time())}.wav"
            audio_path = safe_path_join(self.output_dir, filename)
            
            silent_clip.write_audiofile(audio_path, fps=44100, verbose=False, logger=None)
            silent_clip.close()
            
            return audio_path, duration
        except Exception:
            return None, 0.0

    def _measure_audio_duration(self, audio_path: str) -> float:
        """Mesure la durée audio"""
        if not HAS_MOVIEPY or not os.path.exists(audio_path):
            return 45.0
        
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            audio_clip.close()
            return duration
        except Exception:
            return 45.0

    def _create_ultra_composition(self, content_data: Dict, assets: Dict, 
                                audio_path: str, audio_duration: float) -> Optional[str]:
        """Crée la composition vidéo finale avec musique"""
        if not HAS_MOVIEPY:
            print("❌ MoviePy non disponible")
            return None
        
        audio_clip = None
        background_music = None
        video_clips = []
        final_video = None
        
        try:
            # Charger et préparer l'audio principal
            audio_clip = AudioFileClip(audio_path)
            video_duration = min(audio_clip.duration, self.max_duration)
            audio_clip = audio_clip.subclip(0, video_duration)
            
            print(f"⏱️ Durée ULTRA: {video_duration:.1f}s")
            
            # 🎵 PHASE MUSIQUE : Ajouter la musique de fond si activée
            final_audio = audio_clip
            if self.music_enabled and HAS_MUSIC_MANAGER:
                try:
                    print("🎵 Recherche de musique de fond...")
                    music_manager = MusicManager()
                    music_path = music_manager.find_brainrot_music(video_duration, content_data.get('category', ''))
                    
                    if music_path and os.path.exists(music_path):
                        print(f"🎵 Chargement musique: {os.path.basename(music_path)}")
                        background_music = AudioFileClip(music_path)
                        
                        # Ajuster la durée de la musique
                        if background_music.duration > video_duration:
                            background_music = background_music.subclip(0, video_duration)
                        else:
                            # Boucler la musique si trop courte
                            background_music = background_music.loop(duration=video_duration)
                        
                        # Appliquer le volume
                        background_music = background_music.volumex(self.music_volume)
                        
                        # Mixer l'audio principal avec la musique
                        from moviepy.audio.CompositeAudioClip import CompositeAudioClip
                        final_audio = CompositeAudioClip([audio_clip, background_music])
                        print(f"✅ Musique intégrée (volume: {self.music_volume})")
                    else:
                        print("🎵 Aucune musique trouvée - continuation sans musique")
                        
                except Exception as e:
                    print(f"⚠️ Erreur musique: {e} - continuation sans musique")
            else:
                if not self.music_enabled:
                    print("🎵 Musique désactivée dans la configuration")
                else:
                    print("🎵 MusicManager indisponible")
            
            # Créer les clips vidéo
            video_clips = self._create_ultra_clips(assets, video_duration, content_data)
            if not video_clips:
                print("❌ Aucun clip vidéo créé")
                return None
            
            # Assembler la vidéo finale
            final_video = self._assemble_ultra_video(video_clips, final_audio)
            
            # Générer le nom de fichier
            filename = f"brainrot_ultra_{clean_filename(content_data['title'])}.mp4"
            output_path = safe_path_join(self.output_dir, filename)
            
            print(f"💾 Export QUALITÉ MAX...")
            
            # 🔥 CORRECTION : Paramètres H.264 optimisés
            final_video.write_videofile(
                output_path,
                fps=self.target_fps,
                codec='libx264',
                audio_codec='aac',
                bitrate="8000k",
                audio_bitrate="192k",
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None,
                threads=4,
                preset='medium',
                ffmpeg_params=[
                    '-pix_fmt', 'yuv420p',
                    '-crf', '18',
                    '-movflags', '+faststart'
                ]
            )
            
            # Vérifier le résultat
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)
                print(f"✅ Vidéo créée: {output_path} ({file_size:.1f}MB)")
                return output_path
            else:
                print("❌ Fichier vidéo non créé")
                return None
                
        except Exception as e:
            print(f"❌ Composition ULTRA: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            # 🧹 NETTOYAGE ROBUSTE des ressources
            resources = [audio_clip, background_music, final_video]
            resources.extend(video_clips)
            
            for resource in resources:
                if resource:
                    try: 
                        resource.close()
                    except: 
                        pass

    def _create_ultra_clips(self, assets: Dict, total_duration: float, content_data: Dict) -> List:
        """Crée les clips vidéo à partir des assets"""
        if not HAS_MOVIEPY:
            return []
        
        asset_paths = assets.get('asset_paths', [])
        if not asset_paths:
            print("❌ Aucun asset path disponible")
            return []
        
        clips = []
        durations = self._calculate_ultra_durations(len(asset_paths), total_duration)
        
        for i, asset_path in enumerate(asset_paths):
            if i >= len(durations):
                break
                
            try:
                if asset_path.endswith('.gif'):
                    clip = VideoFileClip(asset_path)
                    clip = clip.set_duration(durations[i])
                else:
                    clip = ImageClip(asset_path, duration=durations[i])
                
                # 🔥 CORRECTION : Resize avec dimensions paires
                clip = clip.resize(height=self.resolution[1])
                
                # Ajouter des transitions
                if i > 0 and len(asset_paths) > 1:
                    clip = clip.fx(fadein, 0.5).fx(fadeout, 0.5)
                
                clip = clip.set_position(('center', 'center'))
                clips.append(clip)
                
            except Exception as e:
                print(f"❌ Clip ULTRA {i}: {e}")
                continue
        
        print(f"✅ {len(clips)} clips créés")
        return clips

    def _calculate_ultra_durations(self, num_assets: int, total_duration: float) -> List[float]:
        """Calcule les durées pour chaque asset"""
        if num_assets == 0:
            return []
        
        base_duration = total_duration / num_assets
        durations = [max(2.5, min(6.0, base_duration * random.uniform(0.7, 1.3))) for _ in range(num_assets)]
        
        total_current = sum(durations)
        if total_current > 0:
            adjustment = total_duration / total_current
            durations = [d * adjustment for d in durations]
        
        return durations

    def _assemble_ultra_video(self, video_clips: List, audio_clip: Any) -> Any:
        """Assemble la vidéo finale"""
        if not video_clips:
            raise ValueError("Aucun clip ULTRA")
        
        if len(video_clips) > 1:
            final_video = concatenate_videoclips(video_clips, method="compose", padding=0.2)
        else:
            final_video = video_clips[0]
        
        final_video = final_video.set_audio(audio_clip)
        final_video = final_video.set_duration(audio_clip.duration)
        
        return final_video

    def _cleanup_temp_files(self, files: List[str]):
        """Nettoie les fichiers temporaires"""
        cleaned = 0
        for file in files:
            try:
                if file and os.path.exists(file) and any(pattern in file for pattern in ['_ultra', 'fallback_audio']):
                    os.remove(file)
                    cleaned += 1
            except Exception:
                continue
        
        if cleaned > 0:
            print(f"🧹 {cleaned} fichiers ULTRA nettoyés")

class VideoCreator(BrainrotVideoCreator):
    def __init__(self):
        super().__init__()
        print("🔧 VideoCreator ULTRA initialisé")

def create_video(content_data: Dict[str, Any]) -> Optional[str]:
    """Fonction d'interface principale"""
    try:
        creator = VideoCreator()
        return creator.create_video(content_data)
    except Exception as e:
        print(f"❌ Création ULTRA: {e}")
        return None
