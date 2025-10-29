# content_factory/audio_generator.py (Intégration config.yaml)

import os
import time
import sys
import asyncio
import subprocess # Ajout de subprocess ici pour plus de clarté
from typing import Optional, List, Callable, Tuple
from content_factory.utils import clean_filename, safe_path_join, ensure_directory
from content_factory.config_loader import ConfigLoader # Import du chargeur

# --- GESTION DES IMPORTS DIFFÉRÉS (LATENCE) ---
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

# --- CONSTANTES DE SÉCURITÉ (non configurables) ---
MIN_FILE_SIZE_BYTES = 2048 # 2KB minimum pour l'audio réel

class AudioGenerator:
    """
    Génère des fichiers audio avec une chaîne de méthodes de repli robuste,
    en utilisant les paramètres du config.yaml.
    """
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.audio_config = self.config['AUDIO_GENERATOR']
        self.paths = self.config['PATHS']
        
        # Chemin de sortie basé sur la configuration centralisée
        self.output_dir = safe_path_join(self.paths['OUTPUT_ROOT'], self.paths['AUDIO_DIR'])
        ensure_directory(self.output_dir)
        
        # Paramètres configurables
        self.tts_voice = self.audio_config.get('DEFAULT_VOICE', 'fr-FR-DeniseNeural')
        self.speaking_rate = self.audio_config.get('SPEAKING_RATE', 1.0)
        self.fallback_duration_s = self.config['VIDEO_CREATOR'].get('FALLBACK_DURATION_S', 10) # Récupère la durée de secours de la config vidéo
    
    def generate_audio(self, text: str, title: str) -> Optional[str]:
        """
        Gère la chaîne de génération audio.
        """
        print(f"🔊 Tentative de génération audio pour: {title[:70]}...")
        
        # 1. Préparation des chemins
        clean_title = clean_filename(title)
        audio_path_base = safe_path_join(self.output_dir, f"audio_{clean_title}")
        
        # 2. Définition des méthodes de repli (du plus performant au plus sûr)
        # Note: self._try_system_tts est souvent problématique en CI/CD (binaires non trouvés)
        methods: List[Tuple[Callable, str, bool]] = [
            (self._try_edge_tts_async, '.mp3', HAS_EDGE_TTS),
            (self._try_google_tts, '.mp3', HAS_G_TTS),
            (self._create_silent_audio, '.mp3', True), # Toujours disponible
            (self._try_system_tts, '.mp3', True), # En dernier recours, car nécessite des binaires
        ]
        
        for method, ext, condition in methods:
            if not condition:
                continue

            current_audio_path = audio_path_base + ext
            
            try:
                # Exécution de la méthode
                result = method(text, current_audio_path)
                
                # Vérification
                if result and os.path.exists(result) and os.path.getsize(result) > MIN_FILE_SIZE_BYTES:
                    print(f"✅ Audio généré avec {method.__name__}: {result}")
                    return result
                    
                print(f"⚠️ {method.__name__} réussi mais le fichier est trop petit ou manquant.")
                
            except Exception as e:
                print(f"❌ {method.__name__} a échoué: {e.__class__.__name__}: {e}")
                continue
        
        # 3. Dernier recours (créer un fichier audio silencieux minimal si tout échoue)
        return self._create_minimal_audio(clean_title)
    
    # --- Méthodes de Génération ---
    
    def _try_edge_tts_async(self, text: str, audio_path: str) -> Optional[str]:
        """Exécute _try_edge_tts dans un contexte synchrone, en utilisant la voix configurée."""
        if not HAS_EDGE_TTS:
             raise ImportError("edge_tts n'est pas installé.")
        
        async def generate():
            communicate = edge_tts.Communicate(text, self.tts_voice, rate=f"+{int((self.speaking_rate - 1.0) * 100):+}%")
            await communicate.save(audio_path)
        
        try:
            asyncio.run(generate())
            return audio_path
        except Exception:
            raise

    def _try_google_tts(self, text: str, audio_path: str) -> Optional[str]:
        """Tente Google TTS (gTTS), en utilisant la langue configurée."""
        if not HAS_G_TTS:
            raise ImportError("gTTS n'est pas installé.")
            
        # gTTS n'a pas de paramètre 'voice' mais utilise la langue ('fr')
        lang = self.tts_voice[:2].lower() if self.tts_voice else 'fr'
        
        # La vitesse doit être soit 'True' (lent) soit 'False' (normal), on le simplifie ici
        slow = self.speaking_rate < 0.95 
            
        tts = gTTS(text=text, lang=lang, slow=slow)
        tts.save(audio_path)
        return audio_path

    def _try_system_tts(self, text: str, audio_path: str) -> Optional[str]:
        """Tente la synthèse système (espeak + ffmpeg). Nécessite que les binaires soient installés."""
        
        temp_wav = audio_path.replace('.mp3', f'_{int(time.time())}.wav')
        
        # Note: Les paramètres d'espeak sont souvent fixes
        # 1. Génération WAV (espeak)
        subprocess.run([
            'espeak', '-v', 'fr+f2', '-s', '150', '-a', '100', text,
            '-w', temp_wav
        ], check=True, capture_output=True, timeout=30)
        
        # 2. Conversion MP3 (ffmpeg)
        if os.path.exists(temp_wav):
            subprocess.run([
                'ffmpeg', '-i', temp_wav, '-acodec', 'libmp3lame', '-q:a', '4', '-y', audio_path
            ], check=True, capture_output=True, timeout=30)
            os.remove(temp_wav)
            
        return audio_path

    def _create_silent_audio(self, text: str, audio_path: str) -> Optional[str]:
        """Crée un audio silencieux basé sur la durée de secours configurée."""
        
        # Durée de l'audio silencieux basée sur la configuration vidéo
        duration = self.fallback_duration_s
        print(f"🔊 Fallback : Création d'un audio silencieux de {duration}s...")

        command = [
            'ffmpeg', '-f', 'lavfi',
            '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100:duration={duration}',
            '-c:a', 'libmp3lame', '-q:a', '4', '-y', audio_path
        ]
        
        subprocess.run(command, check=True, capture_output=True, timeout=45)
        return audio_path

    def _create_minimal_audio(self, clean_title: str) -> Optional[str]:
        """Crée un fichier audio minimal non vide (dernier recours)."""
        audio_path = safe_path_join(self.output_dir, f"audio_minimal_{clean_title}.mp3")
        try:
            with open(audio_path, 'wb') as f:
                f.write(b'\xFF\xFB\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00') 
            print(f"⚠️ AUCUNE méthode audio n'a fonctionné. Audio minimal créé: {audio_path}")
            return audio_path
        except Exception:
            print("❌ Échec de la création du fichier audio minimal.")
            return None

# --- Bloc d'Export et de Test ---

def generate_audio(text: str, title: str) -> Optional[str]:
    """Fonction d'export pour l'interface de la classe."""
    generator = AudioGenerator()
    return generator.generate_audio(text, title)

if __name__ == "__main__":
    print("🧪 Test AudioGenerator (vérifiez les dépendances TTS et les binaires FFmpeg)...")
    
    # ⚠️ Note : Pour que ce test fonctionne, PyYAML doit être installé, et config.yaml doit exister.
    
    try:
        # Configuration des dossiers de test
        test_output_root = "test_output_audio"
        ensure_directory(test_output_root)
        
        # L'instanciation appelle le ConfigLoader
        generator = AudioGenerator()
        
        result = generator.generate_audio(
            "Ceci est un test de la nouvelle chaîne de synthèse vocale configurée.",
            "Test_Configuration_TTS"
        )
        
        if result and os.path.exists(result):
            print(f"\n✅ Test réussi. Fichier généré: {result}")
        else:
            print("\n❌ Test échoué. Aucun fichier audio valide n'a pu être généré.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Erreur critique lors du test: {e}")
        sys.exit(1)

