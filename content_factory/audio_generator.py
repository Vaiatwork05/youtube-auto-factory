# content_factory/audio_generator.py (VERSION COMPLÈTE AVEC MUSIQUE)

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
    """Générateur audio complet avec TTS et musique de fond automatique."""
    
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
        
        print(f"🔊 AudioGenerator prêt - TTS: {len(self.available_voices)} voix, Musique: {'✅' if self.music_manager else '❌'}")

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
        Nettoie AGGRESSIVEMENT le texte pour TTS.
        Supprime tout ce qui peut ralentir la synthèse.
        """
        if not text:
            return "Contenu intéressant à découvrir."
            
        # PHASE 1: Suppression totale des émojis et symboles
        text = re.sub(r'[^\w\s,.!?;:\-\n]', '', text)
        
        # PHASE 2: Remplacement des caractères problématiques
        replacements = {
            '#': 'numéro ',
            ' - ': ' : ',
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
        
        # PHASE 3: Optimisation pour la vitesse
        # Raccourcir les phrases longues
        sentences = text.split('.')
        short_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 100:  # Phrases trop longues
                words = sentence.split()
                if len(words) > 15:
                    # Couper les phrases trop longues
                    sentence = ' '.join(words[:15]) + '.'
            if sentence:
                short_sentences.append(sentence)
        
        text = '. '.join(short_sentences)
        
        # PHASE 4: Nettoyage final
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Assurer un texte minimal
        if len(text) < 20:
            text = "Découvrez ce contenu fascinant dans la vidéo."
            
        return text

    def generate_audio(self, text: str, title: str, content_data: Dict[str, Any] = None) -> Optional[str]:
        """
        Génère l'audio complet avec TTS et musique de fond automatique.
        
        Args:
            text: Le texte à synthétiser
            title: Le titre pour le nommage des fichiers
            content_data: Données supplémentaires pour la recherche de musique
        
        Returns:
            Chemin vers le fichier audio final ou None en cas d'erreur
        """
        if not text or not text.strip():
            print("❌ Texte vide fourni pour la génération audio")
            return self._create_quick_fallback(title)
        
        # NETTOYAGE AGGRESSIF du texte
        clean_text = self.clean_text_for_tts(text)
        
        if not clean_text or len(clean_text.strip()) < 10:
            print("⚠️ Texte trop court après nettoyage, utilisation du texte original")
            clean_text = re.sub(r'[^\w\s,.!?;:()\-]', ' ', text)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        print(f"🔊 Génération audio pour: {title[:50]}...")
        print(f"📝 Texte optimisé: {clean_text[:80]}...")
        
        # Préparation chemin
        clean_title = clean_filename(title)
        
        # ÉTAPE 1: Génération audio TTS de base
        audio_tts_path = self._generate_tts_audio(clean_text, clean_title)
        if not audio_tts_path:
            print("❌ Échec génération TTS, utilisation du fallback")
            return self._create_quick_fallback(clean_title)
        
        # ÉTAPE 2: Mesurer la durée réelle de l'audio TTS
        tts_duration = self._get_audio_duration(audio_tts_path)
        print(f"⏱️ Durée TTS: {tts_duration:.1f} secondes")
        
        # ÉTAPE 3: Recherche et ajout de musique de fond (si activé)
        if self.music_manager and HAS_PYDUB:
            final_audio_path = self._add_background_music(audio_tts_path, clean_title, tts_duration, content_data)
            
            # Nettoyage du fichier TTS temporaire
            try:
                if audio_tts_path != final_audio_path and os.path.exists(audio_tts_path):
                    os.remove(audio_tts_path)
            except Exception as e:
                print(f"⚠️ Impossible de nettoyer le fichier TTS: {e}")
            
            return final_audio_path
        else:
            print("🎵 Musique désactivée - Retour audio TTS seul")
            return audio_tts_path

    def _generate_tts_audio(self, text: str, clean_title: str) -> Optional[str]:
        """Génère l'audio TTS de base avec fallback en cascade."""
        audio_path = safe_path_join(self.output_dir, f"audio_tts_{clean_title}.mp3")
        
        # ESSAI EN CHAÎNE RAPIDE (timeouts courts)
        methods = [
            (self._try_edge_tts_fast, HAS_EDGE_TTS),
            (self._try_google_tts_fast, HAS_G_TTS),
            (self._create_quick_audio, True),
        ]
        
        for method, condition in methods:
            if not condition:
                continue
                
            try:
                print(f"⚡ Essai: {method.__name__}")
                result = method(text, audio_path)
                
                if result and os.path.exists(result) and os.path.getsize(result) > 2048:
                    print(f"✅ SUCCÈS avec {method.__name__}")
                    return result
                    
            except Exception as e:
                print(f"❌ {method.__name__} échoué: {e}")
                continue
        
        return None

    def _try_edge_tts_fast(self, text: str, audio_path: str) -> Optional[str]:
        """Edge TTS ULTRA-RAPIDE avec timeout court."""
        if not HAS_EDGE_TTS:
            raise ImportError("edge_tts non disponible")
        
        async def generate_fast():
            # VOIX RAPIDE et paramètres optimisés
            voice = self.get_random_voice()
            
            # CONTRÔLE DE VITESSE AGGRESSIF
            rate_percent = min(50, int((self.tts_speed - 1.0) * 100))
            rate_param = f"+{rate_percent}%"
            
            print(f"   🔊 Edge TTS - Voix: {voice}, Vitesse: {rate_param}")
            
            communicate = edge_tts.Communicate(text, voice, rate=rate_param)
            
            # TIMEOUT COURT pour éviter les blocages
            try:
                await asyncio.wait_for(communicate.save(audio_path), timeout=30.0)
            except asyncio.TimeoutError:
                raise Exception("Timeout Edge TTS")
                
            return audio_path
        
        try:
            return asyncio.run(generate_fast())
        except Exception as e:
            # Réessayer avec une autre voix en cas d'échec
            return self._retry_edge_tts_fallback(text, audio_path)

    def _retry_edge_tts_fallback(self, text: str, audio_path: str) -> Optional[str]:
        """Réessaye avec d'autres voix rapidement."""
        fallback_voices = [v for v in self.available_voices if v != self.default_voice]
        
        for voice in fallback_voices[:2]:  # Seulement 2 essais
            try:
                async def retry():
                    communicate = edge_tts.Communicate(text, voice, rate="+30%")  # Vitesse fixe
                    await asyncio.wait_for(communicate.save(audio_path), timeout=20.0)
                    return audio_path
                
                print(f"   🔄 Réessai avec voix: {voice}")
                return asyncio.run(retry())
            except Exception:
                continue
        
        raise Exception("Toutes les voix Edge TTS ont échoué")

    def _try_google_tts_fast(self, text: str, audio_path: str) -> Optional[str]:
        """Google TTS optimisé pour la vitesse."""
        if not HAS_G_TTS:
            raise ImportError("gTTS non disponible")
            
        try:
            print("   🔊 Google TTS rapide...")
            
            # Google TTS n'a pas de contrôle de vitesse fin
            # On utilise slow=False pour la vitesse maximale
            tts = gTTS(text=text, lang='fr', slow=False)
            tts.save(audio_path)
            
            return audio_path
            
        except Exception as e:
            raise Exception(f"Google TTS échoué: {e}")

    def _create_quick_audio(self, text: str, audio_path: str) -> Optional[str]:
        """Crée un audio de fallback RAPIDE avec espeak."""
        try:
            if not self._check_espeak_available():
                raise ImportError("espeak non disponible")
            
            print("   🔊 Fallback espeak rapide...")
            
            # Fichier WAV temporaire
            temp_wav = audio_path.replace('.mp3', '.wav')
            
            # PARAMÈTRES ESPEAK ULTRA-RAPIDES
            subprocess.run([
                'espeak', '-v', 'fr+f2', '-s', '200', '-p', '99', text,
                '-w', temp_wav
            ], check=True, capture_output=True, timeout=15)
            
            if os.path.exists(temp_wav):
                # Conversion MP3 rapide
                subprocess.run([
                    'ffmpeg', '-i', temp_wav, '-acodec', 'libmp3lame', 
                    '-q:a', '6', '-y', audio_path
                ], check=True, capture_output=True, timeout=10)
                os.remove(temp_wav)
                
            return audio_path
            
        except subprocess.TimeoutExpired:
            raise Exception("Timeout espeak")
        except Exception as e:
            raise Exception(f"espeak échoué: {e}")

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
            # Estimation grossière : ~1 seconde = 16KB
            return max(15.0, min(120.0, file_size / 16000))
        except:
            return 45.0  # Durée par défaut

    def _create_quick_fallback(self, clean_title: str) -> Optional[str]:
        """Crée un fichier audio de fallback minimal."""
        audio_path = safe_path_join(self.output_dir, f"audio_fallback_{clean_title}.mp3")
        
        try:
            # Court audio silencieux
            command = [
                'ffmpeg', '-f', 'lavfi',
                '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:duration=15',
                '-c:a', 'libmp3lame', '-q:a', '6', '-y', audio_path
            ]
            
            subprocess.run(command, check=True, capture_output=True, timeout=10)
            print(f"⚠️ Audio fallback créé: {os.path.basename(audio_path)}")
            return audio_path
            
        except Exception as e:
            print(f"❌ Échec fallback rapide: {e}")
            return None

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
    Fonction d'export principale pour le système.
    
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
        # Fallback immédiat
        try:
            generator = AudioGenerator()
            return generator._create_quick_fallback(clean_filename(title))
        except:
            return None

# --- TESTS ---
def test_audio_generator():
    """Test complet du générateur audio."""
    print("🧪 TEST AUDIO GENERATOR COMPLET...")
    
    test_text = """
    Numéro dix : La révélation secrète que les experts cachent au public.
    Numéro neuf : L'astuce incroyable que seuls les initiés connaissent.
    Numéro huit : Le phénomène bizarre que la science ne peut expliquer.
    """
    
    test_content = {
        'title': 'Test Audio Complet',
        'category': 'psychologie'
    }
    
    start_time = time.time()
    result = generate_audio(test_text, test_content['title'], test_content)
    end_time = time.time()
    
    if result and os.path.exists(result):
        duration = end_time - start_time
        file_size = os.path.getsize(result) / 1024  # KB
        
        print(f"✅ Test réussi en {duration:.1f}s")
        print(f"📁 Fichier: {result}")
        print(f"📏 Taille: {file_size:.1f} KB")
        
        # Nettoyage
        try:
            os.remove(result)
            print("🧹 Fichier de test nettoyé")
        except:
            pass
            
        return True
    else:
        print("❌ Test échoué")
        return False

if __name__ == "__main__":
    test_audio_generator()
