# content_factory/video_creator.py (VERSION COMPLÈTEMENT RÉÉCRITE)

import os
import time
import random
import re
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

# Import du nouveau GifManager
try:
    from content_factory.gif_manager import get_gifs
    HAS_GIF_MANAGER = True
    print("✅ GifManager chargé")
except ImportError as e:
    HAS_GIF_MANAGER = False
    print(f"⚠️ GifManager non disponible: {e}")

try:
    from content_factory.audio_generator import generate_audio
    HAS_AUDIO_GENERATOR = True
except ImportError as e:
    HAS_AUDIO_GENERATOR = False
    print(f"⚠️ AudioGenerator non disponible: {e}")

class VideoCreator:
    """Créateur de vidéos robuste avec support GIFs et gestion d'erreurs complète."""
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.video_config = self.config.get('VIDEO_CREATOR', {})
        self.paths = self.config.get('PATHS', {})
        
        # Configuration optimisée pour YouTube Shorts
        self.resolution = (1080, 1920)  # Format 9:16
        self.target_fps = 30
        self.max_duration = 60  # 60 secondes max pour Shorts
        self.min_duration = 20  # 20 secondes min pour être engageant
        
        # Chemins
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        video_dir = self.paths.get('VIDEO_DIR', 'videos')
        self.output_dir = safe_path_join(output_root, video_dir)
        ensure_directory(self.output_dir)
        
        # Compteur pour noms de fichiers uniques
        self.file_counter = 0
        
        print("🎬 VideoCreator initialisé - Mode GIFs activé")

    def create_video(self, content_data: Dict[str, Any], output_dir: str = None) -> Optional[str]:
        """
        MÉTHODE PRINCIPALE - Interface requise par auto_content_engine.py
        """
        print(f"🎬 CREATE_VIDEO appelé")
        print(f"📝 Titre: {content_data.get('title', 'Sans titre')}")
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
        
        # Validation des champs requis avec valeurs par défaut
        content_data.setdefault('title', 'Contenu intéressant')
        content_data.setdefault('script', 'Découvrez ce contenu fascinant.')
        content_data.setdefault('keywords', ['éducation', 'apprentissage'])
        
        return self.create_professional_video(content_data)

    def create_professional_video(self, content_data: Dict[str, Any]) -> Optional[str]:
        """Crée une vidéo avec support GIFs et gestion d'erreurs complète."""
        print(f"\n🎬 DÉBUT CRÉATION VIDÉO: {content_data['title'][:50]}...")
        start_time = time.time()
        
        try:
            # 1. PRÉPARATION DES MÉDIAS (GIFs prioritaires)
            print("🖼️ Étape 1: Préparation des médias...")
            media_assets = self._prepare_media_assets(content_data)
            if not media_assets or not media_assets.get('media_paths'):
                print("❌ Échec critique: Aucun média disponible")
                return None
            
            print(f"✅ Médias préparés: {len(media_assets['media_paths'])} éléments")

            # 2. GÉNÉRATION AUDIO AVEC DURÉE OPTIMISÉE
            print("🎵 Étape 2: Génération audio...")
            audio_path, audio_duration = self._generate_optimized_audio(content_data)
            if not audio_path:
                print("❌ Échec critique: Aucun audio généré")
                return None
            
            print(f"✅ Audio généré: {audio_path} ({audio_duration:.1f}s)")

            # 3. CRÉATION VIDÉO AVEC NOM DE FICHIER SÉCURISÉ
            print("🎬 Étape 3: Création vidéo...")
            final_video_path = self._create_adaptive_video(content_data, media_assets, audio_path, audio_duration)
            
            if final_video_path and os.path.exists(final_video_path):
                total_time = time.time() - start_time
                file_size = os.path.getsize(final_video_path) / (1024 * 1024)
                
                print(f"🎉 VIDÉO CRÉÉE AVEC SUCCÈS!")
                print(f"📁 Chemin: {final_video_path}")
                print(f"📏 Taille: {file_size:.1f} MB")
                print(f"⏱️ Durée: {audio_duration:.1f}s")
                print(f"🚀 Temps total: {total_time:.1f}s")
                
                # Nettoyage des fichiers temporaires
                self._cleanup_temp_files([audio_path] + media_assets.get('temp_files', []))
                
                return final_video_path
            else:
                print("❌ Échec création vidéo finale")
                return None
                
        except Exception as e:
            print(f"💥 ERREUR CRITIQUE dans create_professional_video: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _prepare_media_assets(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prépare les médias (GIFs prioritaires) avec fallback complet."""
        print("  🖼️ Préparation des médias...")
        
        temp_files = []
        media_paths = []
        
        try:
            # ESSAI 1: Récupération de GIFs via GifManager
            if HAS_GIF_MANAGER:
                print("  🎬 Recherche de GIFs...")
                gif_paths = get_gifs(content_data, num_gifs=6)
                media_paths.extend(gif_paths)
                print(f"  ✅ {len(gif_paths)} GIFs trouvés")
            
            # ESSAI 2: Fallback - images de secours
            if len(media_paths) < 4:
                needed = 6 - len(media_paths)
                print(f"  🔧 Complétion avec {needed} images fallback...")
                fallback_paths = self._create_thematic_fallback_images(content_data, needed)
                media_paths.extend(fallback_paths)
                temp_files.extend(fallback_paths)
            
            # ESSAI 3: Fallback d'urgence
            if not media_paths:
                print("  🚨 Création médias d'urgence...")
                emergency_paths = self._create_emergency_media(3)
                media_paths.extend(emergency_paths)
                temp_files.extend(emergency_paths)
            
            # Redimensionnement pour format Shorts
            processed_media = []
            for media_path in media_paths:
                if os.path.exists(media_path):
                    if media_path.endswith('.gif'):
                        # Pour les GIFs, on les utilise directement
                        processed_media.append(media_path)
                    else:
                        # Pour les images, redimensionnement
                        processed_path = self._resize_for_shorts(media_path)
                        if processed_path and processed_path != media_path:
                            temp_files.append(processed_path)
                        processed_media.append(processed_path or media_path)
            
            print(f"  ✅ {len(processed_media)} médias prêts")
            
            return {
                'media_paths': processed_media,
                'temp_files': temp_files,
                'content_data': content_data
            }
            
        except Exception as e:
            print(f"  ❌ Erreur préparation médias: {e}")
            # Fallback ultime
            emergency_paths = self._create_emergency_media(3)
            return {
                'media_paths': emergency_paths,
                'temp_files': emergency_paths,
                'content_data': content_data
            }

    def _create_thematic_fallback_images(self, content_data: Dict[str, Any], count: int) -> List[str]:
        """Crée des images de secours thématiques."""
        try:
            title = content_data.get('title', 'Contenu intéressant')
            keywords = content_data.get('keywords', ['éducation', 'apprentissage'])
            
            images = []
            colors = [
                (41, 128, 185, 255),   # Bleu
                (39, 174, 96, 255),    # Vert
                (142, 68, 173, 255),   # Violet
                (230, 126, 34, 255),   # Orange
                (231, 76, 60, 255)     # Rouge
            ]
            
            for i in range(min(count, 5)):
                color = colors[i % len(colors)]
                img = Image.new('RGBA', self.resolution, color=color)
                draw = ImageDraw.Draw(img)
                
                # Titre stylisé
                try:
                    # Texte principal
                    title_lines = self._split_text(title, 25)
                    for j, line in enumerate(title_lines[:2]):
                        text_width = len(line) * 20  # Estimation
                        x = (self.resolution[0] - text_width) // 2
                        y = self.resolution[1]//2 - 30 + (j * 40)
                        draw.text((x, y), line, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 128))
                    
                    # Mot-clé
                    if keywords:
                        keyword = keywords[i % len(keywords)]
                        kw_width = len(keyword) * 20
                        kw_x = (self.resolution[0] - kw_width) // 2
                        draw.text((kw_x, self.resolution[1]//2 + 40), keyword, 
                                 fill=(255, 255, 255, 200))
                        
                except Exception as font_error:
                    print(f"    ⚠️ Erreur police: {font_error}")
                    # Fallback texte basique
                    draw.text((100, 500), title[:40], fill=(255, 255, 255, 255))
                
                path = safe_path_join(self.output_dir, f"thematic_fallback_{i}_{int(time.time())}.png")
                img.convert('RGB').save(path, 'JPEG', quality=90)
                images.append(path)
            
            return images
            
        except Exception as e:
            print(f"    ❌ Erreur images thématiques: {e}")
            return []

    def _create_emergency_media(self, count: int) -> List[str]:
        """Crée des médias d'urgence."""
        try:
            media_paths = []
            gradients = [
                [(30, 60, 90), (70, 130, 180)],   # Bleu dégradé
                [(50, 120, 80), (140, 200, 150)], # Vert dégradé
                [(120, 60, 120), (200, 140, 200)] # Violet dégradé
            ]
            
            for i in range(min(count, 3)):
                color1, color2 = gradients[i]
                img = Image.new('RGB', self.resolution)
                draw = ImageDraw.Draw(img)
                
                # Créer un dégradé simple
                for y in range(self.resolution[1]):
                    ratio = y / self.resolution[1]
                    r = int(color1[0] + (color2[0] - color1[0]) * ratio)
                    g = int(color1[1] + (color2[1] - color1[1]) * ratio)
                    b = int(color1[2] + (color2[2] - color1[2]) * ratio)
                    draw.line([(0, y), (self.resolution[0], y)], fill=(r, g, b))
                
                path = safe_path_join(self.output_dir, f"emergency_media_{i}_{int(time.time())}.jpg")
                img.save(path, 'JPEG', quality=85)
                media_paths.append(path)
            
            return media_paths
            
        except Exception as e:
            print(f"    ❌ Erreur médias d'urgence: {e}")
            return []

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

    def _generate_optimized_audio(self, content_data: Dict[str, Any]) -> tuple[Optional[str], float]:
        """Génère l'audio avec durée optimisée pour YouTube Shorts."""
        target_duration = 30.0  # Cible 30 secondes idéal pour Shorts
        
        try:
            script = self._optimize_script_duration(content_data, target_duration)
            title = content_data.get('title', 'Sujet intéressant')
            
            print(f"    📝 Script optimisé ({len(script)} caractères)")
            
            # Génération audio
            if HAS_AUDIO_GENERATOR:
                audio_path = generate_audio(script, title, content_data)
                
                if audio_path and os.path.exists(audio_path):
                    duration = self._measure_audio_duration(audio_path)
                    
                    # Validation durée
                    if duration < self.min_duration:
                        print(f"    ⚠️ Audio trop court ({duration:.1f}s), utilisation durée cible")
                        # Recréer avec script plus long
                        extended_script = self._extend_script(script, self.min_duration)
                        audio_path = generate_audio(extended_script, title, content_data)
                        duration = self._measure_audio_duration(audio_path) if audio_path else target_duration
                    
                    duration = min(duration, self.max_duration)
                    return audio_path, duration
            
            # Fallback audio silencieux
            print("    🔧 Fallback: audio silencieux...")
            silent_path = self._create_silent_audio(target_duration)
            return silent_path, target_duration
            
        except Exception as e:
            print(f"    ❌ Erreur génération audio: {e}")
            silent_path = self._create_silent_audio(target_duration)
            return silent_path, target_duration

    def _optimize_script_duration(self, content_data: Dict[str, Any], target_duration: float) -> str:
        """Optimise le script pour atteindre la durée cible."""
        script = content_data.get('script', '')
        title = content_data.get('title', '')
        
        # Estimation: ~30 caractères = 1 seconde de parole
        target_chars = int(target_duration * 30)
        
        if len(script) < target_chars:
            # Ajouter du contenu pour atteindre la durée
            additional_content = [
                "Cette information est cruciale pour votre développement personnel.",
                "Prenez des notes, c'est important.",
                "Partagez cette vidéo à quelqu'un qui en a besoin.",
                "Abonnez-vous pour plus de contenu comme celui-ci.",
                "Laissez un like si vous avez appris quelque chose.",
                "Restez jusqu'à la fin pour la révélation la plus importante."
            ]
            
            # Ajouter progressivement du contenu
            while len(script) < target_chars and additional_content:
                extra = additional_content.pop(0)
                script += "\n\n" + extra
        
        elif len(script) > target_chars * 1.5:
            # Réduire si trop long
            script = script[:int(target_chars * 1.2)]
        
        return script

    def _extend_script(self, script: str, min_duration: float) -> str:
        """Étend un script pour atteindre une durée minimale."""
        extensions = [
            "C'est une information essentielle que peu de gens connaissent.",
            "Appliquez ces conseils dans votre vie quotidienne.",
            "Les résultats peuvent être spectaculaires.",
            "Prenez le temps de bien comprendre ces concepts.",
            "Votre vie pourrait changer grâce à ces révélations."
        ]
        
        extended = script
        for extension in extensions:
            extended += "\n\n" + extension
        
        return extended

    def _measure_audio_duration(self, audio_path: str) -> float:
        """Mesure la durée réelle du fichier audio."""
        if not HAS_MOVIEPY or not os.path.exists(audio_path):
            return 30.0
        
        try:
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            audio_clip.close()
            return duration
        except Exception as e:
            print(f"    ⚠️ Erreur mesure durée audio: {e}")
            return 30.0

    def _create_silent_audio(self, duration: float) -> Optional[str]:
        """Crée un fichier audio silencieux en fallback."""
        if not HAS_MOVIEPY:
            return None
        
        try:
            silent_clip = AudioClip(lambda t: 0, duration=duration)
            silent_path = safe_path_join(self.output_dir, f"silent_audio_{int(duration)}s.wav")
            silent_clip.write_audiofile(silent_path, fps=22050, verbose=False, logger=None)
            silent_clip.close()
            
            return silent_path
            
        except Exception as e:
            print(f"    ❌ Erreur création audio silencieux: {e}")
            return None

    def _create_adaptive_video(self, content_data: Dict[str, Any], assets: Dict[str, Any], 
                             audio_path: str, audio_duration: float) -> Optional[str]:
        """Crée une vidéo adaptative avec nom de fichier sécurisé."""
        if not HAS_MOVIEPY:
            print("❌ MoviePy non disponible")
            return None
        
        try:
            print(f"    🎬 Création vidéo adaptative ({audio_duration:.1f}s)...")
            
            # Charger et ajuster l'audio
            audio_clip = AudioFileClip(audio_path)
            video_duration = min(audio_clip.duration, self.max_duration)
            audio_clip = audio_clip.subclip(0, video_duration)
            
            print(f"    ⏱️ Durée vidéo finale: {video_duration:.1f}s")
            
            # Créer les clips média
            video_clips = self._create_media_clips(assets, video_duration)
            if not video_clips:
                print("    ❌ Aucun clip créé")
                audio_clip.close()
                return None
            
            print(f"    📹 {len(video_clips)} clips créés")
            
            # Assembler la vidéo
            final_video = self._assemble_video(video_clips, audio_clip)
            
            # NOM DE FICHIER SÉCURISÉ - CORRECTION DU BUG PRINCIPAL
            safe_filename = self._generate_safe_filename(content_data['title'])
            output_path = safe_path_join(self.output_dir, safe_filename)
            
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
                file_size = os.path.getsize(output_path) / (1024 * 1024)
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

    def _generate_safe_filename(self, title: str) -> str:
        """Génère un nom de fichier sécurisé sans caractères spéciaux."""
        # Nettoyage radical du nom de fichier
        safe_title = re.sub(r'[^\w\s-]', '', title)  # Supprime tous les caractères spéciaux
        safe_title = re.sub(r'[\s]+', '_', safe_title)  # Remplace espaces par underscores
        safe_title = safe_title.strip('_')  # Supprime les underscores en début/fin
        
        # Si le titre est vide après nettoyage, utiliser un timestamp
        if not safe_title:
            safe_title = f"video_{int(time.time())}"
        else:
            # Limiter la longueur
            safe_title = safe_title[:50]
        
        filename = f"shorts_{safe_title}.mp4"
        print(f"    🔧 Nom de fichier sécurisé: {filename}")
        return filename

    def _create_media_clips(self, assets: Dict[str, Any], total_duration: float) -> List[Any]:
        """Crée des clips vidéo à partir des médias."""
        if not HAS_MOVIEPY:
            return []
        
        media_paths = assets.get('media_paths', [])
        if not media_paths:
            return []
        
        clips = []
        
        try:
            # Calculer les durées adaptatives
            durations = self._calculate_optimized_durations(len(media_paths), total_duration)
            print(f"    🎬 Durées médias: {[f'{d:.1f}s' for d in durations]}")
            
            for i, media_path in enumerate(media_paths):
                if i >= len(durations):
                    break
                    
                if os.path.exists(media_path):
                    try:
                        if media_path.endswith('.gif'):
                            # Utiliser directement le GIF comme clip vidéo
                            clip = VideoFileClip(media_path)
                            # Ajuster la durée
                            if clip.duration > durations[i]:
                                clip = clip.subclip(0, durations[i])
                            else:
                                # Si le GIF est plus court, le boucler
                                clip = clip.loop(duration=durations[i])
                        else:
                            # Image standard
                            clip = ImageClip(media_path, duration=durations[i])
                        
                        # Redimensionner et positionner
                        clip = clip.resize(height=self.resolution[1])
                        clip = clip.set_position(('center', 'center'))
                        clips.append(clip)
                        
                    except Exception as e:
                        print(f"    ⚠️ Erreur création clip {i}: {e}")
                        continue
            
            return clips
            
        except Exception as e:
            print(f"    ❌ Erreur création clips: {e}")
            return []

    def _calculate_optimized_durations(self, num_media: int, total_duration: float) -> List[float]:
        """Calcule des durées optimisées pour un bon rythme."""
        if num_media == 0 or total_duration < 15:
            return [max(3.0, total_duration)] if num_media > 0 else []
        
        # Rythme varié et engageant
        min_duration = 3.0
        max_duration = 7.0
        
        # Répartition intelligente
        base_duration = total_duration / num_media
        durations = []
        
        for i in range(num_media):
            if i == 0:
                # Première image plus longue
                duration = min(max_duration, base_duration * 1.4)
            elif i == num_media - 1:
                # Dernière image plus longue
                duration = min(max_duration, base_duration * 1.3)
            else:
                # Images intermédiaires variées
                variation = random.uniform(0.8, 1.2)
                duration = base_duration * variation
            
            duration = max(min_duration, min(max_duration, duration))
            durations.append(duration)
        
        # Ajustement final précis
        total = sum(durations)
        if total > 0 and abs(total - total_duration) > 0.1:
            factor = total_duration / total
            durations = [d * factor for d in durations]
        
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
                    any(pattern in file for pattern in [
                        '_shorts.', 'fallback_', 'silent_audio', 
                        'thematic_', 'emergency_', 'temp_'
                    ])):
                    os.remove(file)
                    cleaned += 1
            except Exception as e:
                print(f"⚠️ Impossible de supprimer {file}: {e}")
        
        if cleaned > 0:
            print(f"🧹 {cleaned} fichiers temporaires nettoyés")

# Fonction d'export principale pour compatibilité
def create_video(content_data: Dict[str, Any]) -> Optional[str]:
    """Fonction d'export principale pour compatibilité."""
    try:
        creator = VideoCreator()
        return creator.create_video(content_data)
    except Exception as e:
        print(f"❌ Erreur création vidéo (fonction globale): {e}")
        return None
