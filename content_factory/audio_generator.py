# content_factory/audio_generator.py (VERSION CORRIGÉE TTS)

import os
import time
import sys
import asyncio
import subprocess
import random
import re
from typing import Optional, List, Callable, Tuple
from content_factory.utils import clean_filename, safe_path_join, ensure_directory
from content_factory.config_loader import ConfigLoader

# --- GESTION DES IMPORTS DIFFÉRÉS ---
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

# --- CONSTANTES ---
MIN_FILE_SIZE_BYTES = 2048  # 2KB minimum

# Voies françaises valides pour Edge TTS
VALID_FRENCH_VOICES = [
    "fr-FR-DeniseNeural",    # Femme - voix principale
    "fr-FR-HenriNeural",     # Homme
    "fr-FR-AlainNeural",     # Homme  
    "fr-FR-BrigitteNeural",  # Femme
    "fr-FR-CelesteNeural",   # Femme
    "fr-FR-ClaudeNeural",    # Homme
    "fr-FR-CoralieNeural",   # Femme
    "fr-FR-JacquelineNeural", # Femme
    "fr-FR-JeromeNeural",    # Homme
    "fr-FR-JosephineNeural", # Femme
    "fr-FR-MauriceNeural",   # Homme
    "fr-FR-YvesNeural",      # Homme
    "fr-FR-YvetteNeural"     # Femme
]

class AudioGenerator:
    """
    Génère des fichiers audio avec gestion robuste du TTS.
    Version corrigée : nettoie le texte avant synthèse vocale.
    """
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.audio_config = self.config.get('AUDIO_GENERATOR', {})
        self.paths = self.config.get('PATHS', {})
        
        # Chemins
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        audio_dir = self.paths.get('AUDIO_DIR', 'audio')
        self.output_dir = safe_path_join(output_root, audio_dir)
        ensure_directory(self.output_dir)
        
        # Paramètres
        self.default_voice = self.audio_config.get('DEFAULT_VOICE', 'fr-FR-DeniseNeural')
        self.speaking_rate = self.audio_config.get('SPEAKING_RATE', 1.0)
        self.fallback_duration_s = self.config.get('VIDEO_CREATOR', {}).get('FALLBACK_DURATION_S', 10)
        
        # Validation de la voix
        self._validate_and_set_voice()
        
        print(f"🔊 AudioGenerator initialisé - Voix: {self.default_voice}")

    def _validate_and_set_voice(self):
        """Valide et corrige la voix par défaut."""
        if self.default_voice not in VALID_FRENCH_VOICES:
            print(f"⚠️ Voix '{self.default_voice}' invalide. Utilisation d'une voix valide.")
            self.default_voice = random.choice(VALID_FRENCH_VOICES)
            print(f"🔊 Nouvelle voix sélectionnée: {self.default_voice}")

    def get_valid_voice(self) -> str:
        """Retourne une voix française valide."""
        return random.choice(VALID_FRENCH_VOICES)

    def clean_text_for_tts(self, text: str) -> str:
        """
        Nettoie le texte pour que le TTS ne lise pas la ponctuation.
        Résout le problème des 'astérisque', 'dièse', etc.
        """
        if not text:
            return ""
            
        # Supprimer tous les émojis et caractères spéciaux
        text = re.sub(r'[^\w\s,.!?;:()\-@#\n]', '', text)
        
        # Remplacer les caractères probléciaux
        replacements = {
            '#': 'numéro ',
            ' - ': ' : ',
            ' * ': ' ',
            '**': '',
            '()': '',
            '[': '',
            ']': '',
            '\"': '',
            "'": "",
            '👉': '',
            '🎯': '',
            '🚨': '',
            '💀': '',
            '🔥': '',
            '⚠️': '',
            '💥': '',
            '🔞': '',
            '⚡': '',
            '🧠': '',
            '💸': '',
            '💡': '',
            '💖': '',
            '💬': '',
            '🔔': '',
            '📺': '',
            '📹': '',
            '🎉': '',
            '⬇️': '',
            '✅': '',
            '❌': ''
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        # Nettoyer les formats de liste
        text = re.sub(r'(\d+)\s*-\s*', r'numéro \1 : ', text)  # "10 - Titre" → "numéro 10 : Titre"
        
        # Supprimer les espaces multiples
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Capitaliser la première lettre
        if text:
            text = text[0].upper() + text[1:]
            
        print(f"🔧 Texte nettoyé pour TTS: {text[:100]}...")
        return text

    def generate_audio(self, text: str, title: str) -> Optional[str]:
        """
        Gère la génération audio avec texte nettoyé pour TTS.
        """
        if not text or not text.strip():
            print("❌ Texte vide fourni pour la génération audio")
            return self._create_fallback_audio(title)
        
        # NETTOYAGE CRITIQUE du texte pour TTS
        clean_text = self.clean_text_for_tts(text)
        
        if not clean_text or len(clean_text.strip()) < 10:
            print("⚠️ Texte trop court après nettoyage, utilisation du texte original")
            clean_text = re.sub(r'[^\w\s,.!?;:()\-]', ' ', text)  # Nettoyage basique
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        print(f"🔊 Génération audio pour: {title[:50]}...")
        print(f"📝 Texte à synthétiser: {clean_text[:100]}...")
        
        # Préparation des chemins
        clean_title = clean_filename(title)
        audio_path_base = safe_path_join(self.output_dir, f"audio_{clean_title}")
        
        # Chaîne de fallback
        methods = self._get_fallback_methods()
        
        for method, ext, condition in methods:
            if not condition:
                continue

            current_audio_path = audio_path_base + ext
            
            try:
                # Utiliser le texte NETTOYÉ pour le TTS
                result = method(clean_text, current_audio_path)
                
                if self._validate_audio_file(result):
                    print(f"✅ Audio généré avec {method.__name__}: {os.path.basename(result)}")
                    return result
                    
                print(f"⚠️ {method.__name__} réussi mais fichier invalide")
                
            except Exception as e:
                print(f"❌ {method.__name__} échoué: {e.__class__.__name__}: {str(e)[:100]}")

        # Dernier recours
        return self._create_fallback_audio(clean_title)

    def _get_fallback_methods(self) -> List[Tuple[Callable, str, bool]]:
        """Retourne les méthodes de génération par ordre de préférence."""
        return [
            (self._try_edge_tts_async, '.mp3', HAS_EDGE_TTS),
            (self._try_google_tts, '.mp3', HAS_G_TTS),
            (self._create_silent_audio, '.mp3', True),
            (self._try_system_tts, '.mp3', self._check_system_tts_available()),
        ]

    def _validate_audio_file(self, file_path: Optional[str]) -> bool:
        """Valide qu'un fichier audio existe et a une taille suffisante."""
        if not file_path or not os.path.exists(file_path):
            return False
        
        try:
            file_size = os.path.getsize(file_path)
            return file_size > MIN_FILE_SIZE_BYTES
        except OSError:
            return False

    # --- MÉTHODES DE GÉNÉRATION AUDIO ---

    def _try_edge_tts_async(self, text: str, audio_path: str) -> Optional[str]:
        """Tente la génération avec Edge TTS."""
        try:
            return asyncio.run(self._try_edge_tts_async_coro(text, audio_path))
        except Exception as e:
            raise Exception(f"Edge TTS échoué: {e}")

    async def _try_edge_tts_async_coro(self, text: str, audio_path: str) -> Optional[str]:
        """Coroutine pour Edge TTS."""
        if not HAS_EDGE_TTS:
            raise ImportError("edge_tts non disponible")

        try:
            voice = self.get_valid_voice()
            rate_adjustment = f"+{int((self.speaking_rate - 1.0) * 100):+}%"
            
            print(f"🔊 Edge TTS avec voix: {voice}")
            communicate = edge_tts.Communicate(text, voice, rate=rate_adjustment)
            await communicate.save(audio_path)
            
            return audio_path
            
        except Exception as e:
            # Fallback sur d'autres voix en cas d'erreur
            if "voice" in str(e).lower():
                return await self._retry_edge_tts_with_fallback(text, audio_path)
            raise

    async def _retry_edge_tts_with_fallback(self, text: str, audio_path: str) -> Optional[str]:
        """Réessaye Edge TTS avec des voix alternatives."""
        fallback_voices = [v for v in VALID_FRENCH_VOICES if v != self.default_voice]
        
        for voice in fallback_voices[:3]:  # Essayer jusqu'à 3 voix
            try:
                print(f"🔊 Essai voix alternative: {voice}")
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(audio_path)
                return audio_path
            except Exception:
                continue
        
        raise Exception("Toutes les voix Edge TTS ont échoué")

    def _try_google_tts(self, text: str, audio_path: str) -> Optional[str]:
        """Tente Google TTS."""
        if not HAS_G_TTS:
            raise ImportError("gTTS non disponible")
            
        try:
            lang = 'fr'  # Français
            slow = self.speaking_rate < 0.8
            
            print("🔊 Google TTS en cours...")
            tts = gTTS(text=text, lang=lang, slow=slow)
            tts.save(audio_path)
            return audio_path
            
        except Exception as e:
            raise Exception(f"Google TTS échoué: {e}")

    def _try_system_tts(self, text: str, audio_path: str) -> Optional[str]:
        """Tente la synthèse système (espeak)."""
        if not self._check_system_tts_available():
            raise ImportError("espeak ou ffmpeg non disponible")
            
        try:
            temp_wav = audio_path.replace('.mp3', f'_{int(time.time())}.wav')
            
            print("🔊 Synthèse système (espeak) en cours...")
            subprocess.run([
                'espeak', '-v', 'fr+f2', '-s', '150', text,
                '-w', temp_wav
            ], check=True, capture_output=True, timeout=30)
            
            if os.path.exists(temp_wav):
                subprocess.run([
                    'ffmpeg', '-i', temp_wav, '-acodec', 'libmp3lame', 
                    '-q:a', '4', '-y', audio_path
                ], check=True, capture_output=True, timeout=30)
                os.remove(temp_wav)
                
            return audio_path
            
        except subprocess.TimeoutExpired:
            raise Exception("Timeout de la synthèse système")
        except subprocess.CalledProcessError as e:
            raise Exception(f"Erreur synthèse système: {e}")
        except Exception as e:
            raise Exception(f"Erreur inattendue: {e}")

    def _check_system_tts_available(self) -> bool:
        """Vérifie si espeak et ffmpeg sont disponibles."""
        try:
            subprocess.run(['espeak', '--version'], capture_output=True, check=True)
            subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _create_silent_audio(self, text: str, audio_path: str) -> Optional[str]:
        """Crée un audio silencieux."""
        try:
            duration = self.fallback_duration_s
            print(f"🔊 Création audio silencieux ({duration}s)...")
            
            command = [
                'ffmpeg', '-f', 'lavfi',
                '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100:duration={duration}',
                '-c:a', 'libmp3lame', '-q:a', '4', '-y', audio_path
            ]
            
            subprocess.run(command, check=True, capture_output=True, timeout=45)
            return audio_path
            
        except Exception as e:
            raise Exception(f"Audio silencieux échoué: {e}")

    def _create_fallback_audio(self, clean_title: str) -> Optional[str]:
        """Crée un fichier audio de fallback minimal."""
        audio_path = safe_path_join(self.output_dir, f"audio_fallback_{clean_title}.mp3")
        
        try:
            # Court audio silencieux
            command = [
                'ffmpeg', '-f', 'lavfi',
                '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:duration=1',
                '-c:a', 'libmp3lame', '-q:a', '4', '-y', audio_path
            ]
            
            subprocess.run(command, check=True, capture_output=True, timeout=30)
            print(f"⚠️ Audio fallback créé: {os.path.basename(audio_path)}")
            return audio_path
            
        except Exception:
            print("❌ Échec de la création de l'audio fallback")
            return None

# --- INTERFACE D'EXPORT ---

def generate_audio(text: str, title: str) -> Optional[str]:
    """Fonction d'export principale."""
    try:
        generator = AudioGenerator()
        return generator.generate_audio(text, title)
    except Exception as e:
        print(f"❌ Erreur critique AudioGenerator: {e}")
        return None

# --- TESTS ---

def test_tts_cleaning():
    """Teste le nettoyage du texte pour TTS."""
    print("\n🧪 Test nettoyage TTS...")
    
    generator = AudioGenerator()
    
    test_cases = [
        "🚨 TOP 10 #1 - Le *secret* choquant 🔥",
        "👉 Cliquez ici ! 🎯 #5 - Astuce **incroyable**",
        "💀 Ce point #3 va vous détruire ! ⚡",
        "📹 Numéro #2 : La révélation [interdite]",
        "🎉 Likez si vous aimez ! 💖 Commentaire ⬇️"
    ]
    
    for i, test_text in enumerate(test_cases):
        cleaned = generator.clean_text_for_tts(test_text)
        print(f"Test {i+1}:")
        print(f"  Avant: {test_text}")
        print(f"  Après: {cleaned}")
        print()

def main_test():
    """Test principal."""
    print("🧪 Test AudioGenerator (version corrigée)...")
    
    try:
        generator = AudioGenerator()
        
        # Test avec texte contenant des caractères problématiques
        test_text = "🚨 TOP 10 SECRETS CHOCS #1 - Le *premier* point 🔥 #2 - La suite 🎯 #3 - La fin 💀"
        test_title = "Test_TTS_Cleaning"
        
        result = generator.generate_audio(test_text, test_title)
        
        if result and os.path.exists(result):
            file_size = os.path.getsize(result) / 1024
            print(f"\n✅ Test réussi!")
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
            print("\n❌ Test échoué")
            return False
            
    except Exception as e:
        print(f"\n❌ Erreur critique: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test du nettoyage TTS
    test_tts_cleaning()
    
    # Test principal
    success = main_test()
    
    sys.exit(0 if success else 1)
