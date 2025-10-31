# content_factory/audio_generator.py (VERSION ULTRA-RAPIDE)

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

# Voies françaises valides pour Edge TTS (testées)
VALID_FRENCH_VOICES = [
    "fr-FR-DeniseNeural",    # Femme - rapide et claire
    "fr-FR-HenriNeural",     # Homme - bon débit
    "fr-FR-AlainNeural",     # Homme - naturel
    "fr-FR-BrigitteNeural",  # Femme - énergique
    "fr-FR-JeromeNeural",    # Homme - dynamique
]

class AudioGenerator:
    """
    Génère des fichiers audio ULTRA-RAPIDES avec TTS optimisé.
    Version corrigée : vitesse maximale + meilleure gestion d'erreurs.
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
        
        # PARAMÈTRES VITESSE - OPTIMISÉS POUR SHORTS
        self.speaking_rate = self.audio_config.get('SPEAKING_RATE', 1.3)  # PLUS RAPIDE par défaut
        self.default_voice = self.audio_config.get('DEFAULT_VOICE', 'fr-FR-DeniseNeural')
        
        # Validation
        if self.default_voice not in VALID_FRENCH_VOICES:
            self.default_voice = 'fr-FR-DeniseNeural'
            
        print(f"🔊 AudioGenerator ULTRA-RAPIDE - Voix: {self.default_voice}, Vitesse: {self.speaking_rate}")

    def clean_text_for_tts(self, text: str) -> str:
        """
        Nettoie AGGRESSIVEMENT le texte pour TTS rapide.
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

    def generate_audio(self, text: str, title: str) -> Optional[str]:
        """
        Génère l'audio ULTRA-RAPIDE avec fallback agressif.
        """
        if not text or not text.strip():
            print("❌ Texte vide, utilisation du fallback")
            return self._create_quick_fallback(title)
        
        # NETTOYAGE AGGRESSIF
        clean_text = self.clean_text_for_tts(text)
        print(f"🔊 Génération RAPIDE pour: {title[:40]}...")
        print(f"📝 Texte optimisé: {clean_text[:80]}...")
        
        # Préparation chemin
        clean_title = clean_filename(title)
        audio_path = safe_path_join(self.output_dir, f"audio_{clean_title}.mp3")
        
        # ESSAI EN CHAÎNE RAPIDE (timeouts courts)
        methods = [
            (self._try_edge_tts_fast, HAS_EDGE_TTS),
            (self._try_google_tts_fast, HAS_G_TTS),
            (self._create_quick_audio, True),  # Fallback rapide
        ]
        
        for method, condition in methods:
            if not condition:
                continue
                
            try:
                print(f"⚡ Essai: {method.__name__}")
                result = method(clean_text, audio_path)
                
                if result and os.path.exists(result) and os.path.getsize(result) > MIN_FILE_SIZE_BYTES:
                    print(f"✅ SUCCÈS avec {method.__name__}")
                    return result
                    
            except Exception as e:
                print(f"❌ {method.__name__} échoué: {e}")
                continue
        
        # DERNIER RECOURS ULTRA-RAPIDE
        return self._create_quick_fallback(clean_title)

    def _try_edge_tts_fast(self, text: str, audio_path: str) -> Optional[str]:
        """
        Edge TTS ULTRA-RAPIDE avec timeout court.
        """
        if not HAS_EDGE_TTS:
            raise ImportError("edge_tts non disponible")
        
        async def generate_fast():
            # VOIX RAPIDE et paramètres optimisés
            voice = random.choice(VALID_FRENCH_VOICES)
            
            # CONTRÔLE DE VITESSE AGGRESSIF
            rate_percent = min(70, int((self.speaking_rate - 1.0) * 100))  # Max +70%
            rate_param = f"+{rate_percent}%"
            
            print(f"🔊 Edge TTS RAPIDE - Voix: {voice}, Vitesse: {rate_param}")
            
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
        fallback_voices = [v for v in VALID_FRENCH_VOICES if v != self.default_voice]
        
        for voice in fallback_voices[:2]:  # Seulement 2 essais
            try:
                async def retry():
                    communicate = edge_tts.Communicate(text, voice, rate="+50%")  # Vitesse fixe
                    await asyncio.wait_for(communicate.save(audio_path), timeout=20.0)
                    return audio_path
                
                print(f"🔄 Réessai avec voix: {voice}")
                return asyncio.run(retry())
            except Exception:
                continue
        
        raise Exception("Toutes les voix Edge TTS ont échoué")

    def _try_google_tts_fast(self, text: str, audio_path: str) -> Optional[str]:
        """
        Google TTS optimisé pour la vitesse.
        """
        if not HAS_G_TTS:
            raise ImportError("gTTS non disponible")
            
        try:
            print("🔊 Google TTS RAPIDE...")
            
            # Google TTS n'a pas de contrôle de vitesse fin
            # On utilise slow=False pour la vitesse maximale
            tts = gTTS(text=text, lang='fr', slow=False)
            tts.save(audio_path)
            
            return audio_path
            
        except Exception as e:
            raise Exception(f"Google TTS échoué: {e}")

    def _create_quick_audio(self, text: str, audio_path: str) -> Optional[str]:
        """
        Crée un audio de fallback RAPIDE avec espeak.
        """
        try:
            if not self._check_espeak_available():
                raise ImportError("espeak non disponible")
            
            print("🔊 Fallback espeak RAPIDE...")
            
            # Fichier WAV temporaire
            temp_wav = audio_path.replace('.mp3', '.wav')
            
            # PARAMÈTRES ESPEAK ULTRA-RAPIDES
            # -s 200: débit très rapide, -p 99: hauteur normale
            subprocess.run([
                'espeak', '-v', 'fr+f2', '-s', '200', '-p', '99', text,
                '-w', temp_wav
            ], check=True, capture_output=True, timeout=15)
            
            if os.path.exists(temp_wav):
                # Conversion MP3 rapide
                subprocess.run([
                    'ffmpeg', '-i', temp_wav, '-acodec', 'libmp3lame', 
                    '-q:a', '6', '-y', audio_path  # Qualité moyenne pour vitesse
                ], check=True, capture_output=True, timeout=10)
                os.remove(temp_wav)
                
            return audio_path
            
        except subprocess.TimeoutExpired:
            raise Exception("Timeout espeak")
        except Exception as e:
            raise Exception(f"espeak échoué: {e}")

    def _create_quick_fallback(self, clean_title: str) -> Optional[str]:
        """
        Fallback ULTRA-RAPIDE - audio silencieux court.
        """
        audio_path = safe_path_join(self.output_dir, f"audio_quick_{clean_title}.mp3")
        
        try:
            # Audio silencieux de 15 secondes (parfait pour Shorts)
            command = [
                'ffmpeg', '-f', 'lavfi',
                '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:duration=15',
                '-c:a', 'libmp3lame', '-q:a', '6', '-y', audio_path
            ]
            
            subprocess.run(command, check=True, capture_output=True, timeout=10)
            print(f"⚠️ Audio quick fallback: {os.path.basename(audio_path)}")
            return audio_path
            
        except Exception as e:
            print(f"❌ Échec fallback rapide: {e}")
            return None

    def _check_espeak_available(self) -> bool:
        """Vérifie rapidement espeak."""
        try:
            result = subprocess.run(['espeak', '--version'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

# --- FONCTION RAPIDE D'EXPORT ---
def generate_audio(text: str, title: str) -> Optional[str]:
    """
    Fonction d'export ULTRA-RAPIDE.
    """
    try:
        generator = AudioGenerator()
        return generator.generate_audio(text, title)
    except Exception as e:
        print(f"❌ Erreur audio ULTRA-RAPIDE: {e}")
        # Fallback immédiat
        try:
            generator = AudioGenerator()
            return generator._create_quick_fallback(clean_filename(title))
        except:
            return None

# --- TESTS DE VITESSE ---
def test_speed():
    """Teste la vitesse de génération."""
    print("\n🧪 TEST DE VITESSE AUDIO...")
    
    generator = AudioGenerator()
    
    test_text = """
    Top 5 des secrets incroyables de la science moderne. 
    Numéro 5 : La découverte révolutionnaire. 
    Numéro 4 : L'innovation surprenante.
    Numéro 3 : La révélation choquante.
    Numéro 2 : La technologie futuriste.
    Numéro 1 : Le secret ultime.
    """
    
    start_time = time.time()
    result = generator.generate_audio(test_text, "test_vitesse")
    end_time = time.time()
    
    if result:
        duration = end_time - start_time
        print(f"✅ Génération en {duration:.1f} secondes")
        
        # Vérifier la durée audio réelle
        try:
            if HAS_MOVIEPY:
                from moviepy.editor import AudioFileClip
                audio = AudioFileClip(result)
                print(f"📊 Durée audio: {audio.duration:.1f}s")
                audio.close()
        except:
            pass
            
        # Nettoyage
        try:
            os.remove(result)
        except:
            pass
    else:
        print("❌ Test de vitesse échoué")

if __name__ == "__main__":
    test_speed()
