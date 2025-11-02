# content_factory/video_creator.py

import os
import time
import random
from typing import Dict, List, Any, Optional
from PIL import Image, ImageDraw, ImageFont

# Gestion des imports MoviePy
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
    from moviepy.audio.AudioClip import AudioClip
    HAS_MOVIEPY = True
except ImportError as e:
    HAS_MOVIEPY = False
    print(f"⚠️ MoviePy non disponible: {e}")

from content_factory.utils import clean_filename, safe_path_join, ensure_directory
from content_factory.config_loader import ConfigLoader
from content_factory.image_manager import get_images

try:
    from content_factory.audio_generator import generate_audio
    HAS_AUDIO_GENERATOR = True
except ImportError as e:
    HAS_AUDIO_GENERATOR = False
    print(f"⚠️ AudioGenerator non disponible: {e}")

class BrainrotVideoCreator:
    """Créateur de vidéos optimisé pour style BRAINROT TOP 10"""
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.video_config = self.config.get('VIDEO_CREATOR', {})
        self.paths = self.config.get('PATHS', {})
        
        # Configuration BRAINROT
        self.resolution = (1080, 1920)  # Shorts
        self.target_fps = 30
        self.max_duration = 59  # Limite Shorts
        self.min_duration = 30
        
        # Chemins
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        video_dir = self.paths.get('VIDEO_DIR', 'videos')
        self.output_dir = safe_path_join(output_root, video_dir)
        ensure_directory(self.output_dir)
        
        print("🎬 BrainrotVideoCreator - Style BRAINROT activé")

    def create_video(self, content_data: Dict[str, Any], output_dir: str = None) -> Optional[str]:
        """Interface principale requise par auto_content_engine.py"""
        print(f"🎬 CREATE_VIDEO BRAINROT - {content_data['title']}")
        
        if output_dir:
            self.output_dir = output_dir
            ensure_directory(self.output_dir)
        
        return self.create_brainrot_video(content_data)

    def create_brainrot_video(self, content_data: Dict[str, Any]) -> Optional[str]:
        """Crée une vidéo BRAINROT ultra-optimisée"""
        
        print(f"\n🎬 DÉBUT CRÉATION BRAINROT: {content_data['title']}")
        print(f"📊 Catégorie: {content_data['category']} | Partie: {'1' if content_data['is_part1'] else '2'}")
        
        try:
            # 1. PRÉPARATION ASSETS BRAINROT
            print("🖼️ Étape 1: Préparation assets BRAINROT...")
            assets = self._prepare_brainrot_assets(content_data)
            if not assets:
                print("❌ Échec: Aucun asset BRAINROT")
                return None
            
            print(f"✅ Assets: {len(assets['asset_paths'])} éléments")

            # 2. GÉNÉRATION AUDIO BRAINROT
            print("🎵 Étape 2: Génération audio BRAINROT...")
            audio_path, audio_duration = self._generate_brainrot_audio(content_data)
            if not audio_path:
                print("❌ Échec: Aucun audio généré")
                return None
            
            print(f"✅ Audio: {audio_path} ({audio_duration:.1f}s)")

            # 3. CRÉATION VIDÉO BRAINROT
            print("🎬 Étape 3: Création vidéo BRAINROT...")
            final_video_path = self._create_brainrot_video_composition(
                content_data, assets, audio_path, audio_duration
            )
            
            if final_video_path and os.path.exists(final_video_path):
                file_size = os.path.getsize(final_video_path) / (1024 * 1024)
                print(f"🎉 VIDÉO BRAINROT CRÉÉE: {final_video_path} ({file_size:.1f}MB)")
                
                # Nettoyage
                self._cleanup_temp_files([audio_path] + assets.get('temp_files', []))
                
                return final_video_path
            else:
                print("❌ Échec création vidéo BRAINROT")
                return None
                
        except Exception as e:
            print(f"💥 ERREUR BRAINROT: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _prepare_brainrot_assets(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare les assets avec style BRAINROT"""
        
        # Récupère les images/GIFs via image_manager
        asset_paths = get_images(content_data, num_images=10)
        
        if not asset_paths:
            print("❌ Aucun asset généré")
            return {}
        
        # Traitement BRAINROT des assets
        processed_assets = []
        temp_files = []
        
        for asset_path in asset_paths:
            if asset_path.endswith('.gif'):
                # Pour les GIFs, conversion si nécessaire
                processed_path = self._process_brainrot_gif(asset_path)
                if processed_path and processed_path != asset_path:
                    temp_files.append(processed_path)
                processed_assets.append(processed_path or asset_path)
            else:
                # Pour les images, style BRAINROT
                processed_path = self._apply_brainrot_style(asset_path, content_data)
                if processed_path and processed_path != asset_path:
                    temp_files.append(processed_path)
                processed_assets.append(processed_path or asset_path)
        
        print(f"📊 Assets traités: {len(processed_assets)}")
        return {
            'asset_paths': processed_assets,
            'temp_files': temp_files,
            'content_data': content_data
        }

    def _apply_brainrot_style(self, image_path: str, content_data: Dict) -> Optional[str]:
        """Applique un style BRAINROT à une image"""
        try:
            with Image.open(image_path) as img:
                # Redimensionne pour Shorts
                img = self._resize_for_shorts(img)
                
                # Applique des effets BRAINROT
                if content_data.get('is_part1', True):
                    img = self._apply_mystery_effects(img, content_data)
                else:
                    img = self._apply_shock_effects(img, content_data)
                
                # Sauvegarde
                base, ext = os.path.splitext(image_path)
                output_path = f"{base}_brainrot{ext}"
                img.save(output_path, 'JPEG', quality=90, optimize=True)
                
                return output_path
                
        except Exception as e:
            print(f"⚠️ Erreur style BRAINROT: {e}")
            return None

    def _resize_for_shorts(self, img: Image.Image) -> Image.Image:
        """Redimensionne pour le format 9:16"""
        target_width, target_height = self.resolution
        
        # Calcul du redimensionnement
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        if img_ratio > target_ratio:
            new_height = target_height
            new_width = int(img.width * (target_height / img.height))
        else:
            new_width = target_width
            new_height = int(img.height * (target_width / img.width))
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Recadrage au centre
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        return img.crop((left, top, right, bottom))

    def _apply_mystery_effects(self, img: Image.Image, content_data: Dict) -> Image.Image:
        """Applique des effets mystère pour Partie 1"""
        # Ajoute un filtre bleu mystérieux
        from PIL import ImageEnhance
        
        # Augmente le contraste
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.2)
        
        # Teinte bleue
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(0.8)
        
        return img

    def _apply_shock_effects(self, img: Image.Image, content_data: Dict) -> Image.Image:
        """Applique des effets choc pour Partie 2"""
        from PIL import ImageEnhance, ImageFilter
        
        # Augmente saturation et contraste
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(1.3)
        
        enhancer = ImageEnhance.Color(img)
        img = enhancer.enhance(1.4)
        
        # Légère netteté
        img = img.filter(ImageFilter.SHARPEN)
        
        return img

    def _process_brainrot_gif(self, gif_path: str) -> Optional[str]:
        """Traite un GIF pour l'intégration BRAINROT"""
        # Pour l'instant, on garde les GIFs tels quels
        # Pourrait être amélioré avec extraction de frames
        return None

    def _generate_brainrot_audio(self, content_data: Dict) -> tuple[Optional[str], float]:
        """Génère l'audio avec style BRAINROT"""
        
        if not HAS_AUDIO_GENERATOR:
            return self._create_fallback_audio(content_data)
        
        try:
            script = content_data.get('script', '')
            title = content_data.get('title', '')
            
            # Génération audio avec données complètes pour style cohérent
            audio_path = generate_audio(script, title, content_data)
            
            if audio_path and os.path.exists(audio_path):
                duration = self._measure_audio_duration(audio_path)
                if duration > 0:
                    return audio_path, duration
            
            # Fallback
            return self._create_fallback_audio(content_data)
            
        except Exception as e:
            print(f"❌ Erreur audio BRAINROT: {e}")
            return self._create_fallback_audio(content_data)

    def _create_fallback_audio(self, content_data: Dict) -> tuple[Optional[str], float]:
        """Crée un audio de fallback"""
        if not HAS_MOVIEPY:
            return None, 45.0
        
        try:
            duration = random.uniform(45.0, 55.0)
            silent_clip = AudioClip(lambda t: 0, duration=duration)
            
            filename = f"brainrot_fallback_audio_{int(time.time())}.wav"
            audio_path = safe_path_join(self.output_dir, filename)
            
            silent_clip.write_audiofile(audio_path, fps=22050, verbose=False, logger=None)
            silent_clip.close()
            
            return audio_path, duration
            
        except Exception as e:
            print(f"❌ Erreur fallback audio: {e}")
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
        except Exception as e:
            print(f"⚠️ Erreur mesure durée: {e}")
            return 45.0

    def _create_brainrot_video_composition(self, content_data: Dict, assets: Dict, 
                                         audio_path: str, audio_duration: float) -> Optional[str]:
        """Crée la composition vidéo BRAINROT finale"""
        
        if not HAS_MOVIEPY:
            print("❌ MoviePy non disponible")
            return None
        
        try:
            # Charge l'audio
            audio_clip = AudioFileClip(audio_path)
            video_duration = min(audio_clip.duration, self.max_duration)
            audio_clip = audio_clip.subclip(0, video_duration)
            
            print(f"⏱️ Durée vidéo: {video_duration:.1f}s")
            
            # Crée les clips vidéo BRAINROT
            video_clips = self._create_brainrot_clips(assets, video_duration, content_data)
            if not video_clips:
                print("❌ Aucun clip créé")
                audio_clip.close()
                return None
            
            print(f"📹 Clips créés: {len(video_clips)}")
            
            # Assemble la vidéo
            final_video = self._assemble_brainrot_video(video_clips, audio_clip)
            
            # Export
            filename = f"brainrot_{clean_filename(content_data['title'])}.mp4"
            output_path = safe_path_join(self.output_dir, filename)
            
            print(f"💾 Export: {output_path}")
            
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
            
            # Cleanup
            final_video.close()
            audio_clip.close()
            for clip in video_clips:
                clip.close()
            
            if os.path.exists(output_path):
                return output_path
            else:
                return None
                
        except Exception as e:
            print(f"❌ Erreur composition BRAINROT: {e}")
            return None

    def _create_brainrot_clips(self, assets: Dict, total_duration: float, content_data: Dict) -> List:
        """Crée des clips vidéo avec style BRAINROT"""
        if not HAS_MOVIEPY:
            return []
        
        asset_paths = assets.get('asset_paths', [])
        if not asset_paths:
            return []
        
        clips = []
        durations = self._calculate_brainrot_durations(len(asset_paths), total_duration, content_data)
        
        print(f"🖼️ Durées BRAINROT: {[f'{d:.1f}s' for d in durations]}")
        
        for i, asset_path in enumerate(asset_paths):
            if i >= len(durations):
                break
                
            try:
                if asset_path.endswith('.gif'):
                    # Pour les GIFs, utiliser VideoFileClip
                    clip = VideoFileClip(asset_path)
                    clip = clip.set_duration(durations[i])
                else:
                    # Pour les images, utiliser ImageClip
                    clip = ImageClip(asset_path, duration=durations[i])
                
                clip = clip.resize(height=self.resolution[1])
                clip = clip.set_position(('center', 'center'))
                clips.append(clip)
                
            except Exception as e:
                print(f"❌ Erreur clip {i}: {e}")
                continue
        
        return clips

    def _calculate_brainrot_durations(self, num_assets: int, total_duration: float, content_data: Dict) -> List[float]:
        """Calcule des durées dynamiques style BRAINROT"""
        if num_assets == 0:
            return []
        
        # Style différent selon la partie
        if content_data.get('is_part1', True):
            # Partie 1: Durées plus longues pour le mystère
            base_duration = total_duration / num_assets * random.uniform(0.8, 1.2)
            durations = [max(3.0, min(7.0, base_duration)) for _ in range(num_assets)]
        else:
            # Partie 2: Durées plus courtes et dynamiques
            base_duration = total_duration / num_assets * random.uniform(0.6, 1.4)
            durations = [max(2.0, min(5.0, base_duration)) for _ in range(num_assets)]
        
        # Ajustement pour durée exacte
        total_current = sum(durations)
        if total_current > 0:
            adjustment = total_duration / total_current
            durations = [d * adjustment for d in durations]
        
        return durations

    def _assemble_brainrot_video(self, video_clips: List, audio_clip: Any) -> Any:
        """Assemble la vidéo BRAINROT finale"""
        if not video_clips:
            raise ValueError("Aucun clip à assembler")
        
        if len(video_clips) > 1:
            final_video = concatenate_videoclips(video_clips, method="compose")
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
                if file and os.path.exists(file) and any(pattern in file for pattern in ['_brainrot', 'fallback_audio']):
                    os.remove(file)
                    cleaned += 1
            except Exception as e:
                print(f"⚠️ Nettoyage {file}: {e}")
        
        if cleaned > 0:
            print(f"🧹 {cleaned} fichiers temporaires nettoyés")

# Fonction d'interface
def create_video(content_data: Dict[str, Any]) -> Optional[str]:
    """Fonction principale pour compatibilité"""
    try:
        creator = BrainrotVideoCreator()
        return creator.create_video(content_data)
    except Exception as e:
        print(f"❌ Erreur création vidéo BRAINROT: {e}")
        return None

# === COMPATIBILITÉ AVEC auto_content_engine.py ===

class VideoCreator(BrainrotVideoCreator):
    """
    Classe de compatibilité - auto_content_engine.py attend cette classe
    Hérite de BrainrotVideoCreator pour garder toutes les fonctionnalités BRAINROT
    """
    def __init__(self):
        super().__init__()
        print("🔧 VideoCreator (compatibilité) initialisé")

# Assurez-vous que la fonction create_video existe aussi
def create_video(content_data: Dict[str, Any]) -> Optional[str]:
    """Fonction de compatibilité pour les imports existants"""
    try:
        creator = VideoCreator()
        return creator.create_video(content_data)
    except Exception as e:
        print(f"❌ Erreur création vidéo (compatibilité): {e}")
        return None
