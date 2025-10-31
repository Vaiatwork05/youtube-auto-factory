# content_factory/video_creator.py (VERSION COMPLÈTE CORRIGÉE)

import os
import time
import random
import tempfile
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

try:
    from content_factory.image_manager import get_images
    HAS_IMAGE_MANAGER = True
except ImportError as e:
    HAS_IMAGE_MANAGER = False
    print(f"⚠️ ImageManager non disponible: {e}")

try:
    from content_factory.audio_generator import generate_audio
    HAS_AUDIO_GENERATOR = True
except ImportError as e:
    HAS_AUDIO_GENERATOR = False
    print(f"⚠️ AudioGenerator non disponible: {e}")

class VideoCreator:
    """Créateur de vidéos robuste avec fallbacks complets."""
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.video_config = self.config.get('VIDEO_CREATOR', {})
        self.paths = self.config.get('PATHS', {})
        
        # Configuration
        self.resolution = (1080, 1920)  # Format Shorts 9:16
        self.target_fps = 30
        self.max_duration = int(os.getenv('MAX_AUDIO_DURATION', 120))
        self.min_duration = int(os.getenv('MIN_AUDIO_DURATION', 15))
        
        # Chemins
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        video_dir = self.paths.get('VIDEO_DIR', 'videos')
        self.output_dir = safe_path_join(output_root, video_dir)
        ensure_directory(self.output_dir)
        
        print("🎬 VideoCreator initialisé - Mode robuste activé")

    def create_video(self, content_data: Dict[str, Any], output_dir: str = None) -> Optional[str]:
        """
        MÉTHODE PRINCIPALE - Interface requise par auto_content_engine.py
        """
        print(f"🎬 CREATE_VIDEO appelé - Titre: {content_data.get('title', 'Sans titre')}")
        print(f"📁 Output dir reçu: {output_dir}")
        
        # Utiliser le output_dir fourni ou garder celui par défaut
        if output_dir:
            self.output_dir = output_dir
            ensure_directory(self.output_dir)
        
        print(f"📁 Output dir final: {self.output_dir}")
        
        # Vérification basique des données
        if not content_data or not isinstance(content_data, dict):
            print("❌ Données de contenu invalides")
            return None
        
        required_fields = ['title', 'script']
        missing_fields = [field for field in required_fields if field not in content_data]
        if missing_fields:
            print(f"❌ Champs manquants: {missing_fields}")
            # Créer des valeurs par défaut
            content_data.setdefault('title', 'Contenu intéressant')
            content_data.setdefault('script', 'Découvrez ce contenu fascinant.')
        
        return self.create_professional_video(content_data)

    def create_professional_video(self, content_data: Dict[str, Any]) -> Optional[str]:
        """Crée une vidéo avec fallbacks complets."""
        print(f"\n🎬 DÉBUT CRÉATION VIDÉO: {content_data['title']}")
        
        try:
            # 1. PRÉPARATION DES ASSETS (avec fallback)
            print("🖼️ Étape 1: Préparation des assets...")
            assets = self._prepare_assets_with_fallback(content_data)
            if not assets or not assets.get('image_paths'):
                print("❌ Échec critique: Aucun asset disponible")
                return None
            
            print(f"✅ Assets préparés: {len(assets['image_paths'])} images")

            # 2. GÉNÉRATION AUDIO (avec fallback)
            print("🎵 Étape 2: Génération audio...")
            audio_path, audio_duration = self._generate_audio_with_fallback(content_data)
            if not audio_path:
                print("❌ Échec critique: Aucun audio généré")
                return None
            
            print(f"✅ Audio généré: {audio_path} ({audio_duration:.1f}s)")

            # 3. CRÉATION VIDÉO
            print("🎬 Étape 3: Création vidéo...")
            final_video_path = self._create_adaptive_video(content_data, assets, audio_path, audio_duration)
            
            if final_video_path and os.path.exists(final_video_path):
                print(f"🎉 VIDÉO CRÉÉE AVEC SUCCÈS: {final_video_path}")
                
                # Nettoyage des fichiers temporaires
                self._cleanup_temp_files([audio_path] + assets.get('temp_files', []))
                
                return final_video_path
            else:
                print("❌ Échec création vidéo finale")
                return None
                
        except Exception as e:
            print(f"💥 ERREUR CRITIQUE dans create_professional_video: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _prepare_assets_with_fallback(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare les assets avec système de fallback robuste."""
        print("  🖼️ Préparation assets avec fallback...")
        
        temp_files = []
        image_paths = []
        
        try:
            # Essai 1: Récupération d'images via ImageManager
            if HAS_IMAGE_MANAGER:
                print("  🔧 Essai ImageManager...")
                image_paths = get_images(content_data, num_images=8)
            
            # Essai 2: Fallback - images de secours thématiques
            if not image_paths:
                print("  🔧 Fallback: images thématiques...")
                image_paths = self._create_thematic_fallback_images(content_data)
                temp_files.extend(image_paths)
            
            # Essai 3: Fallback d'urgence - images basiques
            if not image_paths:
                print("  🔧 Fallback d'urgence: images basiques...")
                image_paths = self._create_basic_fallback_images()
                temp_files.extend(image_paths)
            
            # Redimensionnement pour format Shorts
            processed_images = []
            for img_path in image_paths:
                if os.path.exists(img_path):
                    processed_path = self._resize_for_shorts(img_path)
                    if processed_path and processed_path != img_path:
                        temp_files.append(processed_path)
                    processed_images.append(processed_path or img_path)
            
            # Dernier recours: une seule image d'urgence
            if not processed_images:
                print("  🚨 Création image d'urgence...")
                emergency_path = self._create_emergency_image(content_data)
                if emergency_path:
                    processed_images = [emergency_path]
                    temp_files.append(emergency_path)
            
            print(f"  ✅ {len(processed_images)} images prêtes")
            
            return {
                'image_paths': processed_images,
                'temp_files': temp_files,
                'content_data': content_data
            }
            
        except Exception as e:
            print(f"  ❌ Erreur préparation assets: {e}")
            # Fallback ultime
            emergency_path = self._create_emergency_image(content_data)
            return {
                'image_paths': [emergency_path] if emergency_path else [],
                'temp_files': [emergency_path] if emergency_path else [],
                'content_data': content_data
            }

    def _create_thematic_fallback_images(self, content_data: Dict[str, Any]) -> List[str]:
        """Crée des images de secours thématiques."""
        try:
            title = content_data.get('title', 'Contenu intéressant')
            keywords = content_data.get('keywords', ['apprentissage', 'découverte'])
            
            images = []
            colors = [
                (41, 128, 185),   # Bleu
                (39, 174, 96),    # Vert
                (142, 68, 173),   # Violet
                (230, 126, 34),   # Orange
                (231, 76, 60)     # Rouge
            ]
            
            for i in range(5):
                color = colors[i % len(colors)]
                img = Image.new('RGB', self.resolution, color=color)
                draw = ImageDraw.Draw(img)
                
                # Ajouter un titre stylisé
                try:
                    # Essayer une police plus grande
                    font_large = ImageFont.load_default()
                    title_lines = self._split_text(title, 30)
                    
                    # Dessiner un fond semi-transparent pour le texte
                    text_bg = Image.new('RGBA', (self.resolution[0], 200), (0, 0, 0, 128))
                    img.paste(text_bg, (0, self.resolution[1]//2 - 100), text_bg)
                    
                    # Titre
                    for j, line in enumerate(title_lines[:2]):
                        text_width = draw.textlength(line, font=font_large)
                        x = (self.resolution[0] - text_width) // 2
                        y = self.resolution[1]//2 - 40 + (j * 40)
                        draw.text((x, y), line, fill=(255, 255, 255), font=font_large)
                    
                    # Mot-clé
                    if keywords:
                        keyword = keywords[i % len(keywords)]
                        kw_width = draw.textlength(keyword, font=font_large)
                        kw_x = (self.resolution[0] - kw_width) // 2
                        draw.text((kw_x, self.resolution[1]//2 + 40), keyword, 
                                 fill=(255, 255, 255, 180), font=font_large)
                        
                except Exception as font_error:
                    print(f"    ⚠️ Erreur police: {font_error}")
                    # Fallback texte basique
                    draw.text((100, 500), title[:40], fill=(255, 255, 255))
                
                path = safe_path_join(self.output_dir, f"thematic_fallback_{i}.jpg")
                img.save(path, 'JPEG', quality=90)
                images.append(path)
            
            return images
            
        except Exception as e:
            print(f"    ❌ Erreur images thématiques: {e}")
            return []

    def _create_basic_fallback_images(self) -> List[str]:
        """Crée des images de fallback basiques."""
        try:
            images = []
            gradients = [
                [(30, 60, 90), (70, 130, 180)],   # Bleu dégradé
                [(50, 120, 80), (140, 200, 150)], # Vert dégradé
                [(120, 60, 120), (200, 140, 200)] # Violet dégradé
            ]
            
            for i, (color1, color2) in enumerate(gradients):
                img = Image.new('RGB', self.resolution)
                draw = ImageDraw.Draw(img)
                
                # Créer un dégradé simple
                for y in range(self.resolution[1]):
                    ratio = y / self.resolution[1]
                    r = int(color1[0] + (color2[0] - color1[0]) * ratio)
                    g = int(color1[1] + (color2[1] - color1[1]) * ratio)
                    b = int(color1[2] + (color2[2] - color1[2]) * ratio)
                    draw.line([(0, y), (self.resolution[0], y)], fill=(r, g, b))
                
                path = safe_path_join(self.output_dir, f"basic_fallback_{i}.jpg")
                img.save(path, 'JPEG', quality=85)
                images.append(path)
            
            return images
            
        except Exception as e:
            print(f"    ❌ Erreur images basiques: {e}")
            return []

    def _create_emergency_image(self, content_data: Dict[str, Any]) -> Optional[str]:
        """Crée une image d'urgence absolue."""
        try:
            img = Image.new('RGB', self.resolution, color=(45, 45, 45))
            draw = ImageDraw.Draw(img)
            
            # Texte très simple
            title = content_data.get('title', 'Contenu spécial')[:50]
            draw.rectangle([100, 500, self.resolution[0]-100, 600], fill=(70, 70, 70))
            draw.text((150, 520), title, fill=(255, 255, 255))
            
            path = safe_path_join(self.output_dir, "emergency_fallback.jpg")
            img.save(path, 'JPEG')
            return path
            
        except Exception as e:
            print(f"    💥 Erreur image d'urgence: {e}")
            return None

    def _split_text(self, text: str, max_length: int) -> List[str]:
        """Divise un texte en lignes de longueur maximale."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if len(' '.join(current_line + [word])) <= max_length:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def _resize_for_shorts(self, image_path: str) -> Optional[str]:
        """Redimensionne une image pour le format 9:16."""
        try:
            with Image.open(image_path) as img:
                target_width, target_height = self.resolution
                
                # Redimensionner en gardant le ratio
                img_ratio = img.width / img.height
                target_ratio = target_width / target_height
                
                if img_ratio > target_ratio:
                    # Image trop large
                    new_height = target_height
                    new_width = int(img.width * (target_height / img.height))
                else:
                    # Image trop haute
                    new_width = target_width
                    new_height = int(img.height * (target_width / img.width))
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Recadrer au centre
                left = (new_width - target_width) // 2
                top = (new_height - target_height) // 2
                right = left + target_width
                bottom = top + target_height
                
                img = img.crop((left, top, right, bottom))
                
                # Sauvegarder avec un nom différent
                base, ext = os.path.splitext(image_path)
                output_path = f"{base}_shorts{ext}"
                img.save(output_path, 'JPEG', quality=85, optimize=True)
                
                return output_path
                
        except Exception as e:
            print(f"    ⚠️ Erreur redimensionnement {image_path}: {e}")
            return None

    def _generate_audio_with_fallback(self, content_data: Dict[str, Any]) -> tuple[Optional[str], float]:
        """Génère l'audio avec système de fallback complet."""
        default_duration = 45.0
        
        try:
            script = self._extract_clean_script(content_data)
            title = content_data.get('title', 'Sujet intéressant')
            
            print(f"    📝 Script à synthétiser ({len(script)} caractères)")
            
            # Essai 1: Génération audio normale
            if HAS_AUDIO_GENERATOR:
                print("    🔧 Essai AudioGenerator...")
                audio_path = generate_audio(script, title, content_data)
                
                if audio_path and os.path.exists(audio_path):
                    duration = self._measure_audio_duration(audio_path)
                    if duration > 0:
                        return audio_path, duration
            
            # Essai 2: Génération sans données supplémentaires
            if HAS_AUDIO_GENERATOR:
                print("    🔧 Fallback: génération sans metadata...")
                try:
                    audio_path = generate_audio(script, title, {})
                    if audio_path and os.path.exists(audio_path):
                        duration = self._measure_audio_duration(audio_path)
                        if duration > 0:
                            return audio_path, duration
                except Exception as e:
                    print(f"    ⚠️ Échec génération simple: {e}")
            
            # Essai 3: Audio silencieux
            print("    🔧 Fallback: audio silencieux...")
            silent_path = self._create_silent_audio(default_duration)
            if silent_path:
                return silent_path, default_duration
            
            # Échec total
            print("    ❌ Tous les fallbacks audio ont échoué")
            return None, 0.0
            
        except Exception as e:
            print(f"    ❌ Erreur génération audio: {e}")
            silent_path = self._create_silent_audio(default_duration)
            return silent_path, default_duration if silent_path else (None, 0.0)

    def _extract_clean_script(self, content_data: Dict[str, Any]) -> str:
        """Extrait et nettoie le script pour le TTS."""
        script = content_data.get('script', '')
        
        if not script:
            # Générer un script basique à partir du titre
            title = content_data.get('title', 'Ce contenu fascinant')
            keywords = content_data.get('keywords', ['découverte', 'apprentissage'])
            script = f"Découvrez {title}. Un sujet fascinant sur {', '.join(keywords[:3])}. À ne pas manquer !"
        
        # Optimisation pour Shorts
        if len(script) > 1500:
            print("    📝 Script long détecté, optimisation...")
            lines = script.split('\n')
            important_lines = [l for l in lines if l.strip() and len(l.strip()) > 10]
            script = '\n'.join(important_lines[:10])[:1000]
        
        return script

    def _measure_audio_duration(self, audio_path: str) -> float:
        """Mesure la durée réelle du fichier audio."""
        if not HAS_MOVIEPY or not os.path.exists(audio_path):
            return 45.0
        
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            audio_clip.close()
            return duration
        except Exception as e:
            print(f"    ⚠️ Erreur mesure durée audio: {e}")
            return 45.0

    def _create_silent_audio(self, duration: float) -> Optional[str]:
        """Crée un fichier audio silencieux en fallback."""
        if not HAS_MOVIEPY:
            return None
        
        try:
            # Créer un clip audio silencieux
            silent_clip = AudioClip(lambda t: 0, duration=duration)
            silent_path = safe_path_join(self.output_dir, f"silent_audio_{int(duration)}s.wav")
            silent_clip.write_audiofile(silent_path, fps=22050, verbose=False, logger=None)
            silent_clip.close()
            
            print(f"    ✅ Audio silencieux créé: {silent_path}")
            return silent_path
            
        except Exception as e:
            print(f"    ❌ Erreur création audio silencieux: {e}")
            return None

    def _create_adaptive_video(self, content_data: Dict[str, Any], assets: Dict[str, Any], 
                             audio_path: str, audio_duration: float) -> Optional[str]:
        """Crée une vidéo qui s'adapte parfaitement à l'audio."""
        if not HAS_MOVIEPY:
            print("❌ MoviePy non disponible")
            return None
        
        try:
            print(f"    🎬 Création vidéo adaptative ({audio_duration:.1f}s)...")
            
            # Charger l'audio
            audio_clip = AudioFileClip(audio_path)
            video_duration = min(audio_clip.duration, self.max_duration)
            audio_clip = audio_clip.subclip(0, video_duration)
            
            print(f"    ⏱️ Durée vidéo finale: {video_duration:.1f}s")
            
            # Créer les clips vidéo
            video_clips = self._create_adaptive_clips(assets, video_duration)
            if not video_clips:
                print("    ❌ Aucun clip vidéo créé")
                audio_clip.close()
                return None
            
            print(f"    📹 {len(video_clips)} clips créés")
            
            # Assembler la vidéo
            final_video = self._assemble_video(video_clips, audio_clip)
            
            # Générer le nom de fichier final
            filename = f"shorts_{clean_filename(content_data['title'])}.mp4"
            output_path = safe_path_join(self.output_dir, filename)
            
            print(f"    💾 Exportation vers: {output_path}")
            
            # Exporter avec paramètres optimisés
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
            
            # Nettoyer la mémoire
            final_video.close()
            audio_clip.close()
            for clip in video_clips:
                clip.close()
            
            # Vérification finale
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
                print(f"    ✅ Export réussi: {file_size:.1f}MB")
                return output_path
            else:
                print("    ❌ Fichier de sortie non trouvé")
                return None
                
        except Exception as e:
            print(f"    ❌ Erreur création vidéo adaptative: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_adaptive_clips(self, assets: Dict[str, Any], total_duration: float) -> List[Any]:
        """Crée des clips vidéo adaptés à la durée totale."""
        if not HAS_MOVIEPY:
            return []
        
        image_paths = assets.get('image_paths', [])
        if not image_paths:
            return []
        
        clips = []
        
        try:
            # Calculer les durées adaptatives
            durations = self._calculate_adaptive_durations(len(image_paths), total_duration)
            print(f"    🖼️ Durées images: {[f'{d:.1f}s' for d in durations]}")
            
            for i, img_path in enumerate(image_paths):
                if i >= len(durations):
                    break
                    
                if os.path.exists(img_path):
                    clip = ImageClip(img_path, duration=durations[i])
                    clip = clip.resize(height=self.resolution[1])
                    clip = clip.set_position(('center', 'center'))
                    clips.append(clip)
            
            return clips
            
        except Exception as e:
            print(f"    ❌ Erreur création clips: {e}")
            return []

    def _calculate_adaptive_durations(self, num_images: int, total_duration: float) -> List[float]:
        """Calcule des durées qui remplissent exactement la durée audio."""
        if num_images == 0:
            return []
        
        # Durées variées pour un bon rythme
        min_duration = 2.5
        max_duration = 6.0
        
        # Générer des durées aléatoires mais cohérentes
        durations = []
        remaining_time = total_duration
        
        for i in range(num_images):
            if i == num_images - 1:  # Dernière image
                durations.append(max(min_duration, remaining_time))
            else:
                # Durée proportionnelle avec variation
                base_duration = remaining_time / (num_images - i)
                varied_duration = base_duration * random.uniform(0.7, 1.3)
                final_duration = max(min_duration, min(max_duration, varied_duration))
                
                durations.append(final_duration)
                remaining_time -= final_duration
            
            if remaining_time <= 0:
                break
        
        # Ajustement final pour correspondre exactement
        total_current = sum(durations)
        if total_current > 0 and abs(total_current - total_duration) > 0.1:
            adjustment = total_duration / total_current
            durations = [d * adjustment for d in durations]
        
        return durations

    def _assemble_video(self, video_clips: List[Any], audio_clip: Any) -> Any:
        """Assemble la vidéo finale."""
        if not video_clips:
            raise ValueError("Aucun clip à assembler")
        
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
        cleaned = 0
        for file in files:
            try:
                if (file and os.path.exists(file) and 
                    any(pattern in file for pattern in ['_shorts.', 'fallback_', 'silent_audio', 'thematic_', 'basic_'])):
                    os.remove(file)
                    cleaned += 1
            except Exception as e:
                print(f"⚠️ Impossible de supprimer {file}: {e}")
        
        if cleaned > 0:
            print(f"🧹 {cleaned} fichiers temporaires nettoyés")

def create_video(content_data: Dict[str, Any]) -> Optional[str]:
    """Fonction d'export principale pour compatibilité."""
    try:
        creator = VideoCreator()
        return creator.create_video(content_data)
    except Exception as e:
        print(f"❌ Erreur création vidéo (fonction globale): {e}")
        return None
