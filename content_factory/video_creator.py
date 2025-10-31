# content_factory/video_creator.py (VERSION SHORTS YOUTUBE)

import os
import time
import random
from typing import Dict, List, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np

# Gestion des imports MoviePy avec fallback
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, TextClip, concatenate_videoclips
    from moviepy.video.fx.all import resize, loop
    HAS_MOVIEPY = True
except ImportError:
    HAS_MOVIEPY = False
    print("⚠️ MoviePy non disponible")

from content_factory.utils import clean_filename, safe_path_join, ensure_directory
from content_factory.config_loader import ConfigLoader
from content_factory.image_manager import get_images
from content_factory.audio_generator import generate_audio

class VideoCreator:
    """
    Créateur de vidéos Shorts YouTube optimisé pour l'engagement.
    Version 9:16 verticale avec sous-titres automatiques.
    """
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.video_config = self.config.get('VIDEO_CREATOR', {})
        self.paths = self.config.get('PATHS', {})
        
        # CONFIGURATION SHORTS
        self.resolution = (1080, 1920)  # 9:16 vertical
        self.duration_range = (15, 45)  # Durée idéale Shorts
        self.target_fps = 30
        
        # Chemins
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        video_dir = self.paths.get('VIDEO_DIR', 'videos')
        self.output_dir = safe_path_join(output_root, video_dir)
        ensure_directory(self.output_dir)
        
        # Assets pour Shorts
        self.background_music = None  # À implémenter si souhaité
        self.sound_effects = []  # À implémenter
        
        print("🎬 VideoCreator Shorts initialisé - Format: 1080x1920 (9:16)")

    def create_professional_video(self, content_data: Dict[str, Any]) -> Optional[str]:
        """
        Crée une vidéo Shorts YouTube professionnelle.
        """
        print(f"\n🎬 CRÉATION SHORTS: {content_data['title']}")
        
        try:
            # 1. PRÉPARATION DES ASSETS
            assets = self._prepare_assets(content_data)
            if not assets:
                return None
            
            # 2. GÉNÉRATION AUDIO AVEC TEXTE NETTOYÉ
            script_for_tts = self._extract_clean_script(content_data)
            audio_path = generate_audio(script_for_tts, content_data['title'])
            if not audio_path or not os.path.exists(audio_path):
                print("❌ Échec génération audio")
                return None
            
            # 3. CRÉATION DE LA VIDÉO SHORTS
            final_video_path = self._create_shorts_video(content_data, assets, audio_path)
            
            # 4. NETTOYAGE DES FICHIERS TEMPORAIRES
            self._cleanup_temp_files([audio_path] + assets.get('image_paths', []))
            
            return final_video_path
            
        except Exception as e:
            print(f"❌ Erreur création Shorts: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _extract_clean_script(self, content_data: Dict[str, Any]) -> str:
        """
        Extrait et nettoie le script pour le TTS.
        Sépare les points du Top 10 pour un rythme dynamique.
        """
        script = content_data.get('script', '')
        
        # Si c'est un Top 10, on structure le script différemment
        if 'top10' in content_data.get('content_type', '').lower():
            return self._structure_top10_script(script)
        else:
            # Nettoyage basique pour autres contenus
            return self._clean_script_for_tts(script)
    
    def _structure_top10_script(self, script: str) -> str:
        """
        Structure le script Top 10 pour les Shorts.
        Un point par clip court.
        """
        lines = script.split('\n')
        clean_lines = []
        
        for line in lines:
            line = self._clean_script_for_tts(line)
            if line and len(line.strip()) > 10:  # Lignes significatives
                clean_lines.append(line)
        
        # Pour les Shorts, on prend les points principaux seulement
        return ". ".join(clean_lines[:5])  # Maximum 5 points pour Shorts

    def _clean_script_for_tts(self, text: str) -> str:
        """Nettoie le texte pour le TTS (version simplifiée)."""
        import re
        # Supprimer émojis et caractères spéciaux
        text = re.sub(r'[^\w\s,.!?;:()\-]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _prepare_assets(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare les images et assets pour la vidéo."""
        print("🖼️ Préparation des assets...")
        
        # Récupérer les images
        image_paths = get_images(content_data, num_images=5)  # Plus d'images pour variété
        
        if not image_paths:
            print("❌ Aucune image disponible")
            return {}
        
        # Redimensionner les images pour le format Shorts
        processed_images = []
        for img_path in image_paths:
            processed_path = self._resize_for_shorts(img_path)
            if processed_path:
                processed_images.append(processed_path)
        
        return {
            'image_paths': processed_images,
            'title': content_data['title'],
            'keywords': content_data.get('keywords', [])
        }

    def _resize_for_shorts(self, image_path: str) -> Optional[str]:
        """Redimensionne une image pour le format 9:16."""
        try:
            img = Image.open(image_path)
            
            # Calculer le redimensionnement pour remplir 9:16
            target_width, target_height = self.resolution
            
            # Redimensionner en gardant le ratio
            img_ratio = img.width / img.height
            target_ratio = target_width / target_height
            
            if img_ratio > target_ratio:
                # Image plus large, redimensionner par la hauteur
                new_height = target_height
                new_width = int(img.width * (target_height / img.height))
            else:
                # Image plus haute, redimensionner par la largeur
                new_width = target_width
                new_height = int(img.height * (target_width / img.width))
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Recadrer au centre pour exactement 1080x1920
            left = (new_width - target_width) / 2
            top = (new_height - target_height) / 2
            right = (new_width + target_width) / 2
            bottom = (new_height + target_height) / 2
            
            img = img.crop((left, top, right, bottom))
            
            # Sauvegarder l'image redimensionnée
            output_path = image_path.replace('.jpg', '_shorts.jpg')
            img.save(output_path, 'JPEG', quality=85)
            
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur redimensionnement Shorts: {e}")
            return None

    def _create_shorts_video(self, content_data: Dict[str, Any], assets: Dict[str, Any], audio_path: str) -> Optional[str]:
        """Crée la vidéo Shorts finale."""
        print("🎬 Assemblage du Shorts...")
        
        if not HAS_MOVIEPY:
            print("❌ MoviePy non disponible")
            return None
        
        try:
            # Charger l'audio
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            
            # Limiter la durée pour les Shorts
            max_duration = min(audio_duration, self.duration_range[1])
            audio_clip = audio_clip.subclip(0, max_duration)
            
            # Créer les clips vidéo
            video_clips = self._create_video_clips(assets, max_duration)
            
            if not video_clips:
                print("❌ Aucun clip vidéo créé")
                return None
            
            # Assembler la vidéo finale
            final_video = self._assemble_shorts(video_clips, audio_clip, content_data)
            
            # Exporter
            output_filename = f"shorts_{clean_filename(content_data['title'])}.mp4"
            output_path = safe_path_join(self.output_dir, output_filename)
            
            print("📤 Exportation du Shorts...")
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
            
            print(f"✅ Shorts créé: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur création Shorts: {e}")
            return None

    def _create_video_clips(self, assets: Dict[str, Any], duration: float) -> List[Any]:
        """Crée les clips vidéo à partir des images."""
        if not HAS_MOVIEPY:
            return []
        
        image_paths = assets.get('image_paths', [])
        if not image_paths:
            return []
        
        clips = []
        
        # Durée par image (variée pour dynamisme)
        clip_durations = self._calculate_clip_durations(len(image_paths), duration)
        
        for i, img_path in enumerate(image_paths):
            try:
                # Créer un clip image
                clip = ImageClip(img_path, duration=clip_durations[i])
                
                # Redimensionner pour s'assurer du format 9:16
                clip = clip.resize(height=self.resolution[1])
                
                # Centrer horizontalement
                clip = clip.set_position(('center', 'center'))
                
                clips.append(clip)
                
            except Exception as e:
                print(f"❌ Erreur création clip {i}: {e}")
                continue
        
        return clips

    def _calculate_clip_durations(self, num_clips: int, total_duration: float) -> List[float]:
        """Calcule des durées variées pour les clips."""
        base_duration = total_duration / num_clips
        
        # Varier les durées pour plus de dynamisme
        durations = []
        for i in range(num_clips):
            variation = random.uniform(0.8, 1.2)  # ±20%
            durations.append(base_duration * variation)
        
        # Ajuster pour total exact
        total = sum(durations)
        factor = total_duration / total
        return [d * factor for d in durations]

    def _assemble_shorts(self, video_clips: List[Any], audio_clip: Any, content_data: Dict[str, Any]) -> Any:
        """Assemble tous les éléments du Shorts."""
        
        # Concatenér les clips vidéo
        if len(video_clips) > 1:
            final_video = concatenate_videoclips(video_clips, method="compose")
        else:
            final_video = video_clips[0]
        
        # Ajouter l'audio
        final_video = final_video.set_audio(audio_clip)
        
        # Ajouter les sous-titres (optionnel - complexe à implémenter)
        # final_video = self._add_subtitles(final_video, content_data)
        
        # S'assurer de la durée exacte
        final_video = final_video.set_duration(audio_clip.duration)
        
        return final_video

    def _add_subtitles(self, video_clip: Any, content_data: Dict[str, Any]) -> Any:
        """
        Ajoute des sous-titres animés (version basique).
        À améliorer avec une vraie reconnaissance vocale.
        """
        # IMPLÉMENTATION BASIQUE - À COMPLÉTER
        # Idéalement: utiliser speech-to-text pour synchroniser
        
        try:
            # Sous-titre simple avec le titre
            title = content_data['title']
            txt_clip = TextClip(
                title, 
                fontsize=40, 
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2
            )
            
            # Position en bas (standard Shorts)
            txt_clip = txt_clip.set_position(('center', 1600)).set_duration(3)
            
            # Composite avec le texte
            return CompositeVideoClip([video_clip, txt_clip])
            
        except Exception as e:
            print(f"⚠️ Sous-titres non ajoutés: {e}")
            return video_clip

    def _cleanup_temp_files(self, file_paths: List[str]):
        """Nettoie les fichiers temporaires."""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path) and 'shorts' not in file_path and 'audio_' not in file_path:
                    os.remove(file_path)
            except Exception as e:
                print(f"⚠️ Impossible de supprimer {file_path}: {e}")

    def create_emergency_video(self, content_data: Dict[str, Any]) -> Optional[str]:
        """Crée une vidéo de secours si la génération principale échoue."""
        print("🆘 Création vidéo de secours...")
        
        try:
            # Vidéo simple avec une image et audio
            title = content_data['title']
            output_filename = f"shorts_emergency_{clean_filename(title)}.mp4"
            output_path = safe_path_join(self.output_dir, output_filename)
            
            # Générer un audio minimal
            script = self._extract_clean_script(content_data)
            audio_path = generate_audio(script, title)
            
            if audio_path and os.path.exists(audio_path):
                # Créer une image de fond simple
                bg_path = self._create_emergency_background(title)
                
                if HAS_MOVIEPY and bg_path:
                    audio_clip = AudioFileClip(audio_path)
                    video_clip = ImageClip(bg_path, duration=audio_clip.duration)
                    video_clip = video_clip.set_audio(audio_clip)
                    
                    video_clip.write_videofile(
                        output_path,
                        fps=24,
                        verbose=False,
                        logger=None
                    )
                    
                    video_clip.close()
                    audio_clip.close()
                    os.remove(bg_path)
                    os.remove(audio_path)
                    
                    print(f"✅ Vidéo de secours créée: {output_path}")
                    return output_path
            
            return None
            
        except Exception as e:
            print(f"❌ Échec vidéo de secours: {e}")
            return None

    def _create_emergency_background(self, title: str) -> Optional[str]:
        """Crée un fond d'urgence pour les vidéos de secours."""
        try:
            width, height = self.resolution
            img = Image.new('RGB', (width, height), color=(30, 30, 60))  # Fond bleu nuit
            draw = ImageDraw.Draw(img)
            
            # Ajouter le titre
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                font = ImageFont.load_default()
            
            # Diviser le titre en lignes
            words = title.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                text_width = bbox[2] - bbox[0]
                
                if text_width < width - 100:  # Marge
                    current_line.append(word)
                else:
                    lines.append(' '.join(current_line))
                    current_line = [word]
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Dessiner les lignes
            total_height = len(lines) * 70
            start_y = (height - total_height) // 2
            
            for i, line in enumerate(lines):
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                y = start_y + (i * 70)
                
                draw.text((x, y), line, font=font, fill=(255, 255, 255))
            
            output_path = safe_path_join(self.output_dir, "emergency_bg.jpg")
            img.save(output_path, 'JPEG', quality=90)
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur fond d'urgence: {e}")
            return None

# --- FONCTION D'EXPORT ---
def create_video(content_data: Dict[str, Any]) -> Optional[str]:
    """Fonction d'export principale pour les Shorts."""
    try:
        creator = VideoCreator()
        return creator.create_professional_video(content_data)
    except Exception as e:
        print(f"❌ Erreur création vidéo: {e}")
        return None

# --- TEST ---
if __name__ == "__main__":
    print("🧪 Test VideoCreator Shorts...")
    
    if not HAS_MOVIEPY:
        print("❌ MoviePy requis pour les tests")
        sys.exit(1)
    
    try:
        # Données de test
        test_content = {
            'title': '🚨 TOP 5 SECRETS CHOCS DE LA SCIENCE (PARTIE 1) 💀',
            'script': 'Numéro 5 : La révélation secrète. Numéro 4 : La découverte incroyable. Numéro 3 : La vérité cachée.',
            'keywords': ['science', 'top5', 'secrets', 'choc'],
            'content_type': 'top10_shorts'
        }
        
        creator = VideoCreator()
        result = creator.create_professional_video(test_content)
        
        if result and os.path.exists(result):
            print(f"✅ Test réussi! Shorts créé: {result}")
        else:
            print("❌ Test échoué")
            
    except Exception as e:
        print(f"❌ Erreur test: {e}")
        import traceback
        traceback.print_exc()
