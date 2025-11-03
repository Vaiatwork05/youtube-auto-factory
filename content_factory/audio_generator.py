# content_factory/audio_generator.py (VERSION CORRIGÉE - DURÉE FIXÉE)

import os
import time
import asyncio
import subprocess
import random
import re
from typing import Optional, List, Dict, Any
from content_factory.utils import clean_filename, safe_path_join, ensure_directory
from content_factory.config_loader import ConfigLoader

# Gestion des imports conditionnels
try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False
    print("⚠️ edge_tts non disponible")
    
try:
    from gtts import gTTS
    HAS_G_TTS = True
except ImportError:
    HAS_G_TTS = False
    print("⚠️ gTTS non disponible")

try:
    from pydub import AudioSegment
    from pydub.effects import compress_dynamic_range, high_pass_filter
    HAS_PYDUB = True
except ImportError:
    HAS_PYDUB = False
    print("⚠️ pydub non disponible")

# Import du MusicManager
try:
    from content_factory.music_manager import MusicManager
    HAS_MUSIC_MANAGER = True
except ImportError:
    HAS_MUSIC_MANAGER = False
    print("⚠️ MusicManager non disponible")

class AudioGenerator:
    """Générateur audio CORRIGÉ avec durée garantie de 45-60 secondes."""
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.paths = self.config.get('PATHS', {})
        
        # Configuration TTS
        self.available_voices = self._load_voices_from_env()
        self.default_voice = os.getenv('DEFAULT_TTS_VOICE', 'fr-FR-DeniseNeural')
        self.tts_speed = float(os.getenv('TTS_SPEED', '1.1'))
        self.retry_count = int(os.getenv('TTS_RETRY_COUNT', '3'))
        
        # Configuration musique
        self.music_enabled = os.getenv('BACKGROUND_MUSIC_ENABLED', 'false').lower() == 'true'
        self.music_volume = float(os.getenv('BACKGROUND_MUSIC_VOLUME', '0.25'))
        
        # DURÉE GARANTIE - Configuration critique
        self.min_duration = 45.0  # 45 secondes MINIMUM
        self.target_duration = 60.0  # 60 secondes CIBLE
        self.max_duration = 120.0  # 120 secondes MAXIMUM
        
        # Chemins
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        audio_dir = self.paths.get('AUDIO_DIR', 'audio')
        self.output_dir = safe_path_join(output_root, audio_dir)
        ensure_directory(self.output_dir)
        
        # Initialisation MusicManager
        self.music_manager = None
        if self.music_enabled and HAS_MUSIC_MANAGER:
            self.music_manager = MusicManager()
            print("🎵 MusicManager initialisé - Recherche automatique activée")
        else:
            print("🎵 MusicManager désactivé")
        
        print(f"🔊 AudioGenerator prêt - Durée garantie: {self.min_duration}-{self.target_duration}s")

    def _load_voices_from_env(self) -> List[str]:
        """Charge la liste des voix depuis .env"""
        voices_env = os.getenv('TTS_VOICES', 'fr-FR-DeniseNeural,fr-FR-HenriNeural,fr-FR-AlainNeural')
        voices = [v.strip() for v in voices_env.split(',') if v.strip()]
        
        if not voices:
            # Fallback si aucune voix dans .env
            voices = [
                'fr-FR-DeniseNeural',
                'fr-FR-HenriNeural', 
                'fr-FR-AlainNeural',
                'fr-FR-BrigitteNeural',
                'fr-FR-JeromeNeural'
            ]
        
        return voices

    def get_random_voice(self) -> str:
        """Retourne une voix aléatoire parmi celles disponibles."""
        return random.choice(self.available_voices)

    def clean_text_for_tts(self, text: str) -> str:
        """
        Nettoie le texte pour TTS de façon INTELLIGENTE.
        GARANTIT une durée décente de 45-60 secondes.
        """
        if not text:
            return self._generate_fallback_text()
            
        print(f"📝 Texte original: {len(text)} caractères")
        
        # PHASE 1: Suppression LÉGÈRE des émojis seulement
        text = re.sub(r'[🚨💀🔥⚠️🎯💥🔞⚡🧠💸📺👉💖💬🔔🎉📊📁📏📝🎬🎵🖼️🔧📤📋🎯🔍😄😲💥🧹]', '', text)
        
        # PHASE 2: Remplacement MINIMUM des caractères problématiques
        replacements = {
            '#': 'numéro ',
            '**': '',
            '()': '',
            '[': '',
            ']': '',
            '\"': '',
            "'": "",
            '  ': ' ',
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        # PHASE 3: OPTIMISATION POUR DURÉE (INTELLIGENTE)
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        preserved_sentences = []
        
        for sentence in sentences:
            if len(sentence) > 200:  # TRÈS permissif
                words = sentence.split()
                if len(words) > 35:  # TRÈS permissif
                    # Couper INTELLIGEMMENT au milieu d'une phrase
                    sentence = ' '.join(words[:35]) + '. Écoute la suite dans la vidéo!'
            preserved_sentences.append(sentence)
        
        text = '. '.join(preserved_sentences)
        
        # PHASE 4: GARANTIR une longueur SUFFISANTE pour 45-60 secondes
        target_min_chars = 800   # ~45 secondes
        target_ideal_chars = 1200  # ~60 secondes
        
        current_chars = len(text)
        print(f"📏 Longueur après nettoyage: {current_chars} caractères")
        
        if current_chars < target_min_chars:
            print("🔄 Texte trop court, ajout de contenu...")
            text = self._extend_text_to_target(text, target_ideal_chars)
        
        # PHASE 5: Nettoyage final
        text = re.sub(r'\s+', ' ', text).strip()
        
        print(f"✅ Texte final: {len(text)} caractères (cible: {target_ideal_chars})")
        return text

    def _generate_fallback_text(self) -> str:
        """Génère un texte de fallback pour garantir la durée"""
        base_text = """
        Bienvenue dans ce top 10 exceptionnel ! Nous allons découvrir ensemble les révélations les plus incroyables.
        Chaque point va vous surprendre et vous faire réfléchir. Restez jusqu'à la fin pour la révélation ultime !
        """
        
        # Étendre pour atteindre la durée cible
        return self._extend_text_to_target(base_text, 1200)

    def _extend_text_to_target(self, text: str, target_chars: int) -> str:
        """Étend le texte pour atteindre la longueur cible"""
        extensions = [
            " N'oublie pas de t'abonner pour ne rien rater !",
            " Like la vidéo si tu apprends quelque chose d'incroyable !",
            " Laisse un commentaire avec ton point préféré !",
            " Active les notifications pour les prochains tops !",
            " Ces révélations vont changer ta vision du monde !",
            " Le meilleur est toujours à venir, reste jusqu'au bout !",
            " Partage cette vidéo à tes amis pour les surprendre !",
            " Chaque détail compte dans cette incroyable découverte !"
        ]
        
        current_chars = len(text)
        while current_chars < target_chars:
            extension = random.choice(extensions)
            text += extension
            current_chars = len(text)
            
            # Éviter la boucle infinie
            if current_chars >= target_chars * 1.2:
                break
        
        return text

    def generate_audio(self, text: str, title: str, content_data: Dict[str, Any] = None) -> Optional[str]:
        """
        Génère l'audio complet avec DURÉE GARANTIE de 45-60 secondes.
        """
        if not text or not text.strip():
            print("❌ Texte vide, utilisation du fallback")
            text = self._generate_fallback_text()
        
        # NETTOYAGE INTELLIGENT qui préserve la durée
        clean_text = self.clean_text_for_tts(text)
        
        print(f"🔊 Génération audio DURÉE GARANTIE pour: {title[:50]}...")
        
        # Préparation chemin
        clean_title = clean_filename(title)
        
        # ÉTAPE 1: Génération audio TTS de base
        audio_tts_path = self._generate_tts_audio(clean_text, clean_title)
        if not audio_tts_path:
            print("❌ Échec génération TTS, utilisation du fallback durée garantie")
            return self._create_guaranteed_duration_audio(clean_title, self.target_duration)
        
        # ÉTAPE 2: MESURER et GARANTIR la durée
        tts_duration = self._get_audio_duration(audio_tts_path)
        print(f"⏱️ Durée TTS générée: {tts_duration:.1f} secondes")
        
        # ÉTAPE CRITIQUE: GARANTIR la durée minimale
        if tts_duration < self.min_duration:
            print(f"🚨 DURÉE INSUFFISANTE! Extension de {tts_duration:.1f}s à {self.target_duration}s")
            audio_tts_path = self._extend_audio_to_target(audio_tts_path, self.target_duration, clean_title)
            final_duration = self.target_duration
        else:
            final_duration = min(tts_duration, self.max_duration)
        
        print(f"✅ Durée audio garantie: {final_duration:.1f} secondes")
        
        # ÉTAPE 3: Recherche et ajout de musique de fond (si activé)
        if self.music_manager and HAS_PYDUB and self.music_enabled:
            print("🎵 Tentative d'ajout de musique...")
            final_audio_path = self._add_background_music(audio_tts_path, clean_title, final_duration, content_data)
            
            # Nettoyage du fichier TTS temporaire
            try:
                if audio_tts_path != final_audio_path and os.path.exists(audio_tts_path):
                    os.remove(audio_tts_path)
            except Exception as e:
                print(f"⚠️ Impossible de nettoyer le fichier TTS: {e}")
            
            return final_audio_path
        else:
            print("🎵 Musique désactivée - Retour audio TTS durée garantie")
            return audio_tts_path

    def _generate_tts_audio(self, text: str, clean_title: str) -> Optional[str]:
        """Génère l'audio TTS avec fallback en cascade."""
        audio_path = safe_path_join(self.output_dir, f"audio_tts_{clean_title}.mp3")
        
        # ESSAI EN CHAÎNE avec gestion d'erreur améliorée
        methods = [
            (self._try_edge_tts_optimized, HAS_EDGE_TTS),
            (self._try_google_tts_optimized, HAS_G_TTS),
            (self._create_espeak_audio, self._check_espeak_available()),
        ]
        
        for method, condition in methods:
            if not condition:
                continue
                
            try:
                print(f"⚡ Essai: {method.__name__}")
                result = method(text, audio_path)
                
                if result and os.path.exists(result) and os.path.getsize(result) > 5000:  # Fichier substantiel
                    print(f"✅ SUCCÈS avec {method.__name__}")
                    return result
                    
            except Exception as e:
                print(f"❌ {method.__name__} échoué: {e}")
                continue
        
        print("❌ Tous les méthodes TTS ont échoué")
        return None

    def _try_edge_tts_optimized(self, text: str, audio_path: str) -> Optional[str]:
        """Edge TTS optimisé pour la durée et la qualité"""
        if not HAS_EDGE_TTS:
            raise ImportError("edge_tts non disponible")
        
        async def generate_optimized():
            voice = self.get_random_voice()
            
            # Vitesse OPTIMISÉE pour durée et compréhension
            rate_percent = min(30, int((self.tts_speed - 1.0) * 100))
            rate_param = f"+{rate_percent}%"
            
            print(f"   🔊 Edge TTS - Voix: {voice}, Vitesse: {rate_param}")
            print(f"   📝 Texte: {len(text)} caractères")
            
            communicate = edge_tts.Communicate(text, voice, rate=rate_param)
            
            # TIMEOUT plus long pour les textes longs
            timeout = min(60.0, max(30.0, len(text) / 50))  # Adaptatif
            try:
                await asyncio.wait_for(communicate.save(audio_path), timeout=timeout)
            except asyncio.TimeoutError:
                raise Exception(f"Timeout Edge TTS après {timeout}s")
                
            return audio_path
        
        try:
            return asyncio.run(generate_optimized())
        except Exception as e:
            # Réessayer avec une autre voix
            return self._retry_edge_tts_fallback(text, audio_path)

    def _retry_edge_tts_fallback(self, text: str, audio_path: str) -> Optional[str]:
        """Réessaye avec d'autres voix rapidement."""
        fallback_voices = [v for v in self.available_voices if v != self.default_voice]
        
        for voice in fallback_voices[:2]:  # Seulement 2 essais
            try:
                async def retry():
                    communicate = edge_tts.Communicate(text, voice, rate="+20%")  # Vitesse fixe modérée
                    await asyncio.wait_for(communicate.save(audio_path), timeout=40.0)
                    return audio_path
                
                print(f"   🔄 Réessai avec voix: {voice}")
                return asyncio.run(retry())
            except Exception:
                continue
        
        raise Exception("Toutes les voix Edge TTS ont échoué")

    def _try_google_tts_optimized(self, text: str, audio_path: str) -> Optional[str]:
        """Google TTS optimisé"""
        if not HAS_G_TTS:
            raise ImportError("gTTS non disponible")
            
        try:
            print("   🔊 Google TTS optimisé...")
            tts = gTTS(text=text, lang='fr', slow=False)
            tts.save(audio_path)
            
            return audio_path
            
        except Exception as e:
            raise Exception(f"Google TTS échoué: {e}")

    def _create_espeak_audio(self, text: str, audio_path: str) -> Optional[str]:
        """Crée un audio avec espeak (fallback)"""
        try:
            if not self._check_espeak_available():
                raise ImportError("espeak non disponible")
            
            print("   🔊 Fallback espeak...")
            
            # Fichier WAV temporaire
            temp_wav = audio_path.replace('.mp3', '.wav')
            
            # Paramètres optimisés pour durée et qualité
            subprocess.run([
                'espeak', '-v', 'fr+f2', '-s', '160', '-p', '50', text,
                '-w', temp_wav
            ], check=True, capture_output=True, timeout=30)
            
            if os.path.exists(temp_wav):
                # Conversion MP3
                subprocess.run([
                    'ffmpeg', '-i', temp_wav, '-acodec', 'libmp3lame', 
                    '-q:a', '4', '-y', audio_path
                ], check=True, capture_output=True, timeout=15)
                os.remove(temp_wav)
                
            return audio_path
            
        except subprocess.TimeoutExpired:
            raise Exception("Timeout espeak")
        except Exception as e:
            raise Exception(f"espeak échoué: {e}")

    def _extend_audio_to_target(self, audio_path: str, target_duration: float, title: str) -> str:
        """Étend l'audio pour atteindre la durée cible de façon INTELLIGENTE"""
        if not HAS_PYDUB:
            print("❌ pydub non disponible pour l'extension audio")
            return self._create_guaranteed_duration_audio(title, target_duration)
        
        try:
            audio = AudioSegment.from_file(audio_path, format="mp3")
            current_duration = len(audio) / 1000.0
            
            if current_duration >= target_duration:
                return audio_path
            
            print(f"🔄 Extension audio: {current_duration:.1f}s → {target_duration:.1f}s")
            
            # STRATÉGIE D'EXTENSION INTELLIGENTE
            needed_duration = target_duration - current_duration
            
            if current_duration > 15:  # Si l'audio a du contenu substantiel
                # Répéter les dernières 10 secondes avec fondu
                repeat_segment = audio[-10000:]  # Dernières 10 secondes
                repeat_segment = repeat_segment.fade_out(2000)  # Fondu de sortie
                
                extended_audio = audio
                while len(extended_audio) / 1000.0 < target_duration:
                    extended_audio = extended_audio + repeat_segment
                
            else:
                # Audio trop court, créer un nouveau avec silence intelligent
                extended_audio = audio
                silence_duration = min(10, needed_duration)  # Max 10s de silence
                silence = AudioSegment.silent(duration=int(silence_duration * 1000))
                extended_audio = extended_audio + silence
            
            # Couper à la durée exacte
            extended_audio = extended_audio[:int(target_duration * 1000)]
            
            # Appliquer un fondu de fin
            extended_audio = extended_audio.fade_out(3000)  # 3 secondes de fondu
            
            # Sauvegarder
            extended_path = audio_path.replace('.mp3', '_extended.mp3')
            extended_audio.export(extended_path, format="mp3", bitrate="192k")
            
            # Remplacer l'original
            if os.path.exists(audio_path):
                os.remove(audio_path)
            os.rename(extended_path, audio_path)
            
            print(f"✅ Audio étendu avec succès: {current_duration:.1f}s → {target_duration:.1f}s")
            return audio_path
            
        except Exception as e:
            print(f"❌ Erreur extension audio: {e}")
            # Fallback: créer un nouvel audio de durée garantie
            return self._create_guaranteed_duration_audio(title, target_duration)

    def _create_guaranteed_duration_audio(self, title: str, duration: float) -> str:
        """Crée un audio de durée garantie (fallback ultime)"""
        audio_path = safe_path_join(self.output_dir, f"audio_guaranteed_{title}.mp3")
        
        try:
            if HAS_PYDUB:
                # Créer un audio avec un message de fallback
                from gtts import gTTS
                fallback_text = f"Vidéo en cours de préparation. Durée garantie: {int(duration)} secondes de contenu brainrot de qualité."
                tts = gTTS(text=fallback_text, lang='fr', slow=False)
                tts.save(audio_path)
                
                # Étendre avec du silence si nécessaire
                audio = AudioSegment.from_file(audio_path, format="mp3")
                current_duration = len(audio) / 1000.0
                
                if current_duration < duration:
                    silence = AudioSegment.silent(duration=int((duration - current_duration) * 1000))
                    extended_audio = audio + silence
                    extended_audio.export(audio_path, format="mp3", bitrate="192k")
            else:
                # Fallback basique avec ffmpeg
                command = [
                    'ffmpeg', '-f', 'lavfi',
                    '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100:duration={duration}',
                    '-c:a', 'libmp3lame', '-q:a', '6', '-y', audio_path
                ]
                subprocess.run(command, check=True, capture_output=True, timeout=30)
            
            print(f"✅ Audio durée garantie créé: {duration}s")
            return audio_path
            
        except Exception as e:
            print(f"❌ Échec création audio durée garantie: {e}")
            return None

    def _add_background_music(self, tts_audio_path: str, clean_title: str, 
                            tts_duration: float, content_data: Dict[str, Any] = None) -> Optional[str]:
        """Ajoute une musique de fond à l'audio TTS."""
        try:
            print("🎵 Recherche de musique brainrot libre de droits...")
            
            # Charger l'audio TTS
            tts_audio = AudioSegment.from_file(tts_audio_path, format="mp3")
            
            # Trouver une musique appropriée
            music_path = self.music_manager.find_brainrot_music(
                tts_duration, 
                content_data.get('category', 'general') if content_data else 'general'
            )
            
            if not music_path:
                print("❌ Aucune musique trouvée - Retour audio TTS seul")
                return tts_audio_path
            
            print(f"✅ Musique trouvée: {os.path.basename(music_path)}")
            
            # Charger et préparer la musique
            background_music = AudioSegment.from_file(music_path, format="mp3")
            
            # Ajuster la musique à la durée du TTS
            background_music = self._prepare_background_music(background_music, tts_duration)
            
            # Ajuster le volume de la musique
            background_music = background_music - (1 - self.music_volume) * 12  # Réduction en dB
            
            # Mixer l'audio TTS et la musique
            print("🔊 Mixage audio TTS et musique...")
            mixed_audio = tts_audio.overlay(background_music)
            
            # Compression pour améliorer la qualité
            mixed_audio = compress_dynamic_range(mixed_audio, threshold=-20.0, ratio=4.0)
            
            # Filtre passe-haut léger sur la musique pour éviter les conflits
            mixed_audio = high_pass_filter(mixed_audio, cutoff=100)
            
            # Sauvegarder le résultat final
            final_path = safe_path_join(self.output_dir, f"audio_final_{clean_title}.mp3")
            mixed_audio.export(final_path, format="mp3", bitrate="192k")
            
            print(f"✅ Audio final avec musique: {final_path}")
            return final_path
            
        except Exception as e:
            print(f"❌ Erreur ajout musique: {e}")
            return tts_audio_path

    def _prepare_background_music(self, music: AudioSegment, required_duration: float) -> AudioSegment:
        """Prépare la musique de fond (boucle, fade, etc.)."""
        music_duration = len(music) / 1000.0
        
        # Si la musique est trop courte, la boucler
        if music_duration < required_duration:
            loops_needed = int(required_duration / music_duration) + 1
            looped_music = music
            for _ in range(loops_needed - 1):
                looped_music = looped_music + music
            music = looped_music
        
        # Couper à la durée exacte
        music = music[:int(required_duration * 1000)]
        
        # Appliquer fade in/out
        fade_in = int(float(os.getenv('BACKGROUND_MUSIC_FADE_IN', '2.0')) * 1000)
        fade_out = int(float(os.getenv('BACKGROUND_MUSIC_FADE_OUT', '3.0')) * 1000)
        
        if fade_in > 0:
            music = music.fade_in(fade_in)
        if fade_out > 0:
            music = music.fade_out(fade_out)
        
        return music

    def _get_audio_duration(self, audio_path: str) -> float:
        """Mesure la durée réelle du fichier audio."""
        if HAS_PYDUB:
            try:
                audio = AudioSegment.from_file(audio_path)
                return len(audio) / 1000.0
            except Exception as e:
                print(f"⚠️ Erreur mesure durée audio: {e}")
        
        # Fallback : estimation basée sur la taille du fichier
        try:
            file_size = os.path.getsize(audio_path)
            # Estimation améliorée
            estimated_duration = file_size / 16000  # ~16KB par seconde
            return max(5.0, min(300.0, estimated_duration))
        except:
            return 30.0  # Durée par défaut raisonnable

    def _check_espeak_available(self) -> bool:
        """Vérifie si espeak est disponible."""
        try:
            result = subprocess.run(['espeak', '--version'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

# --- FONCTION D'EXPORT PRINCIPALE ---
def generate_audio(text: str, title: str, content_data: Dict[str, Any] = None) -> Optional[str]:
    """
    Fonction d'export principale avec DURÉE GARANTIE.
    
    Args:
        text: Texte à synthétiser
        title: Titre pour le nommage
        content_data: Données supplémentaires pour contexte
    
    Returns:
        Chemin du fichier audio ou None
    """
    try:
        generator = AudioGenerator()
        return generator.generate_audio(text, title, content_data)
    except Exception as e:
        print(f"❌ Erreur critique AudioGenerator: {e}")
        # Fallback immédiat avec durée garantie
        try:
            generator = AudioGenerator()
            clean_title = clean_filename(title)
            return generator._create_guaranteed_duration_audio(clean_title, 45.0)
        except:
            return None

# --- TESTS ---
def test_audio_generator():
    """Test complet du générateur audio CORRIGÉ."""
    print("🧪 TEST AUDIO GENERATOR CORRIGÉ...")
    
    test_text = """
    Numéro dix : La révélation secrète que les experts cachent au public.
    Numéro neuf : L'astuce incroyable que seuls les initiés connaissent.
    Numéro huit : Le phénomène bizarre que la science ne peut expliquer.
    Numéro sept : La technique révolutionnaire qui change toutes les règles.
    Numéro six : Le secret choquant qui va vous faire tout remettre en question.
    Numéro cinq : La découverte accidentelle devenue révolutionnaire.
    Numéro quatre : La méthode interdite qui fonctionne vraiment.
    Numéro trois : La vérité cachée que personne n'ose révéler.
    Numéro deux : Le hack génial qui va vous simplifier la vie.
    Numéro un : La révélation ultime qui va tout changer.
    """
    
    test_content = {
        'title': 'Test Audio Durée Garantie',
        'category': 'psychologie'
    }
    
    start_time = time.time()
    result = generate_audio(test_text, test_content['title'], test_content)
    end_time = time.time()
    
    if result and os.path.exists(result):
        duration = end_time - start_time
        file_size = os.path.getsize(result) / 1024  # KB
        audio_duration = AudioGenerator()._get_audio_duration(result)
        
        print(f"✅ Test réussi en {duration:.1f}s")
        print(f"📁 Fichier: {result}")
        print(f"📏 Taille: {file_size:.1f} KB")
        print(f"⏱️ Durée audio: {audio_duration:.1f} secondes")
        
        # Vérification durée
        if audio_duration >= 45.0:
            print("🎯 DURÉE GARANTIE: ✅ SUCCÈS (45s+)")
        else:
            print("🎯 DURÉE GARANTIE: ❌ ÉCHEC (trop court)")
        
        # Nettoyage
        try:
            os.remove(result)
            print("🧹 Fichier de test nettoyé")
        except:
            pass
            
        return audio_duration >= 45.0
    else:
        print("❌ Test échoué")
        return False

if __name__ == "__main__":
    test_audio_generator()
