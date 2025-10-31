# content_factory/audio_generator.py (VERSION MULTI-VOIX)

import os
import time
import asyncio
import subprocess
import random
import re
from typing import Optional, List
from content_factory.utils import clean_filename, safe_path_join, ensure_directory
from content_factory.config_loader import ConfigLoader

# Imports TTS
try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False
    
try:
    from gtts import gTTS
    HAS_G_TTS = True
except ImportError:
    HAS_G_TTS = False

class AudioGenerator:
    """Générateur audio avec support multi-voix depuis .env"""
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.paths = self.config.get('PATHS', {})
        
        # Chargement depuis .env
        self.available_voices = self._load_voices_from_env()
        self.default_voice = os.getenv('DEFAULT_TTS_VOICE', 'fr-FR-DeniseNeural')
        self.tts_speed = float(os.getenv('TTS_SPEED', '1.4'))
        self.retry_count = int(os.getenv('TTS_RETRY_COUNT', '3'))
        
        # Chemins
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        audio_dir = self.paths.get('AUDIO_DIR', 'audio')
        self.output_dir = safe_path_join(output_root, audio_dir)
        ensure_directory(self.output_dir)
        
        print(f"🔊 AudioGenerator - {len(self.available_voices)} voix disponibles")
        print(f"   Voix par défaut: {self.default_voice}")
        print(f"   Vitesse: {self.tts_speed}")

    def _load_voices_from_env(self) -> List[str]:
        """Charge la liste des voix depuis .env"""
        voices_env = os.getenv('TTS_VOICES', 'fr-FR-DeniseNeural,fr-FR-HenriNeural')
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
        """Nettoie le texte pour TTS."""
        if not text:
            return "Contenu intéressant à découvrir."
            
        # Nettoyage agressif
        text = re.sub(r'[^\w\s,.!?;:\-\n]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Raccourcir si trop long (pour Shorts)
        if len(text) > 500:
            sentences = text.split('.')
            text = '. '.join(sentences[:3]) + '.'
            
        return text

    def generate_audio(self, text: str, title: str) -> Optional[str]:
        """Génère l'audio avec fallback multi-voix."""
        if not text.strip():
            return self._create_quick_fallback(title)
        
        clean_text = self.clean_text_for_tts(text)
        clean_title = clean_filename(title)
        audio_path = safe_path_join(self.output_dir, f"audio_{clean_title}.mp3")
        
        print(f"🔊 Génération audio: {title[:40]}...")
        
        # Essai avec différentes méthodes
        methods = [
            (self._try_edge_tts_with_retry, HAS_EDGE_TTS),
            (self._try_google_tts_fast, HAS_G_TTS),
            (self._create_quick_audio, True),
        ]
        
        for method, condition in methods:
            if not condition:
                continue
                
            try:
                result = method(clean_text, audio_path)
                if result and os.path.exists(result) and os.path.getsize(result) > 2048:
                    return result
            except Exception as e:
                print(f"❌ {method.__name__}: {e}")
                continue
        
        return self._create_quick_fallback(clean_title)

    def _try_edge_tts_with_retry(self, text: str, audio_path: str) -> Optional[str]:
        """Essaie Edge TTS avec plusieurs voix en cas d'échec."""
        voices_to_try = [self.default_voice] + [
            v for v in self.available_voices if v != self.default_voice
        ]
        
        for attempt in range(self.retry_count):
            voice = voices_to_try[attempt % len(voices_to_try)]
            
            try:
                return asyncio.run(self._edge_tts_coroutine(text, audio_path, voice))
            except Exception as e:
                print(f"   ❌ Tentative {attempt+1} avec {voice}: {e}")
                continue
                
        raise Exception("Toutes les voix Edge TTS ont échoué")

    async def _edge_tts_coroutine(self, text: str, audio_path: str, voice: str) -> str:
        """Coroutine Edge TTS."""
        rate_percent = min(70, int((self.tts_speed - 1.0) * 100))
        rate_param = f"+{rate_percent}%"
        
        print(f"   🔊 Edge TTS - Voix: {voice}, Vitesse: {rate_param}")
        
        communicate = edge_tts.Communicate(text, voice, rate=rate_param)
        await asyncio.wait_for(communicate.save(audio_path), timeout=30.0)
        
        return audio_path

    def _try_google_tts_fast(self, text: str, audio_path: str) -> Optional[str]:
        """Google TTS rapide."""
        if not HAS_G_TTS:
            raise ImportError("gTTS non disponible")
            
        print("   🔊 Google TTS rapide...")
        tts = gTTS(text=text, lang='fr', slow=False)
        tts.save(audio_path)
        return audio_path

    def _create_quick_audio(self, text: str, audio_path: str) -> Optional[str]:
        """Fallback espeak rapide."""
        try:
            if not self._check_espeak():
                raise ImportError("espeak non disponible")
                
            temp_wav = audio_path.replace('.mp3', '.wav')
            
            subprocess.run([
                'espeak', '-v', 'fr+f2', '-s', '200', text, '-w', temp_wav
            ], check=True, capture_output=True, timeout=15)
            
            if os.path.exists(temp_wav):
                subprocess.run([
                    'ffmpeg', '-i', temp_wav, '-acodec', 'libmp3lame', 
                    '-q:a', '6', '-y', audio_path
                ], check=True, capture_output=True, timeout=10)
                os.remove(temp_wav)
                
            return audio_path
            
        except Exception as e:
            raise Exception(f"espeak échoué: {e}")

    def _create_quick_fallback(self, clean_title: str) -> Optional[str]:
        """Fallback ultime."""
        audio_path = safe_path_join(self.output_dir, f"audio_fallback_{clean_title}.mp3")
        
        try:
            subprocess.run([
                'ffmpeg', '-f', 'lavfi',
                '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:duration=15',
                '-c:a', 'libmp3lame', '-q:a', '6', '-y', audio_path
            ], check=True, capture_output=True, timeout=10)
            return audio_path
        except:
            return None

    def _check_espeak(self) -> bool:
        """Vérifie espeak."""
        try:
            subprocess.run(['espeak', '--version'], capture_output=True, timeout=5)
            return True
        except:
            return False

def generate_audio(text: str, title: str) -> Optional[str]:
    """Fonction d'export."""
    try:
        generator = AudioGenerator()
        return generator.generate_audio(text, title)
    except Exception as e:
        print(f"❌ Erreur audio: {e}")
        return None
