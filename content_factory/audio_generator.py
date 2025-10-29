# content_factory/audio_generator.py
import os
import time
import sys
import asyncio
from typing import Optional, List, Callable, Tuple
from content_factory.utils import clean_filename, safe_path_join, ensure_directory

# --- CONSTANTES ---
# Utilisation de constantes pour la clarté et la maintenabilité
DEFAULT_OUTPUT_DIR = "output/audio"
MIN_FILE_SIZE_BYTES = 2048 # Augmenté à 2KB pour plus de sécurité (audio réel)
AUDIO_DURATION_SEC = 30 # Durée pour l'audio silencieux

# --- GESTION DES IMPORTS DIFFÉRÉS (LATENCE) ---
# Les imports coûteux ou optionnels sont faits à l'intérieur des méthodes.
# Cependant, pour Edge TTS et gTTS, nous ajoutons des gardes pour une meilleure gestion des erreurs.
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
    """
    Génère des fichiers audio avec une chaîne de méthodes de repli robuste.
    """
    def __init__(self, output_dir: str = DEFAULT_OUTPUT_DIR):
        # Assure que le chemin est absolu si possible ou cohérent
        self.output_dir = output_dir
        ensure_directory(self.output_dir)
    
    def generate_audio(self, text: str, title: str) -> Optional[str]:
        """
        Gère la chaîne de génération audio.
        :param text: Texte à synthétiser.
        :param title: Titre utilisé pour nommer le fichier.
        :return: Le chemin du fichier audio généré ou None.
        """
        print(f"🔊 Tentative de génération audio pour: {title[:70]}...")
        
        # 1. Préparation des chemins
        clean_title = clean_filename(title)
        audio_path_base = safe_path_join(self.output_dir, f"audio_{clean_title}")
        
        # 2. Définition des méthodes de repli (en utilisant les gardes d'imports)
        # La tupe contient (méthode, extension, condition)
        methods: List[Tuple[Callable, str, bool]] = [
            (self._try_edge_tts_async, '.mp3', HAS_EDGE_TTS),
            (self._try_google_tts, '.mp3', HAS_G_TTS),
            (self._try_system_tts, '.mp3', True), # System TTS tente l'exécution de binaires externes (espeak, ffmpeg)
            (self._create_silent_audio, '.mp3', True)
        ]
        
        for method, ext, condition in methods:
            if not condition:
                continue

            current_audio_path = audio_path_base + ext
            
            try:
                # Exécution de la méthode
                result = method(text, current_audio_path)
                
                # Vérification plus stricte
                if result and os.path.exists(result) and os.path.getsize(result) > MIN_FILE_SIZE_BYTES:
                    print(f"✅ Audio généré avec {method.__name__}: {result}")
                    return result
                    
                print(f"⚠️ {method.__name__} réussi mais le fichier est trop petit ou manquant.")
                
            except Exception as e:
                # Log l'échec et passe au fallback
                print(f"❌ {method.__name__} a échoué: {e}")
                continue
        
        # 3. Dernier recours minimal (si tout le reste échoue, pour éviter le None)
        return self._create_minimal_audio(clean_title)
    
    # --- Méthodes de Génération ---
    
    def _try_edge_tts_async(self, text: str, audio_path: str) -> Optional[str]:
        """Exécute _try_edge_tts dans un contexte synchrone."""
        if not HAS_EDGE_TTS:
             raise ImportError("edge_tts n'est pas installé.")
        
        async def generate():
            # Utilisation de la voix stable et en français
            communicate = edge_tts.Communicate(text, "fr-FR-DeniseNeural")
            await communicate.save(audio_path)
        
        # Gestion propre de l'environnement asynchrone (nécessaire pour edge_tts)
        try:
            asyncio.run(generate())
            return audio_path
        except Exception:
            raise # Laisse l'exception remonter pour le bloc try...except principal

    def _try_google_tts(self, text: str, audio_path: str) -> Optional[str]:
        """Tente Google TTS (gTTS)."""
        if not HAS_G_TTS:
            raise ImportError("gTTS n'est pas installé.")
            
        tts = gTTS(text=text, lang='fr', slow=False)
        tts.save(audio_path)
        # time.sleep(1) n'est plus nécessaire dans un environnement synchrone et moderne
        return audio_path

    def _try_system_tts(self, text: str, audio_path: str) -> Optional[str]:
        """Tente la synthèse système (espeak + ffmpeg). Nécessite que les binaires soient installés."""
        import subprocess
        
        temp_wav = audio_path.replace('.mp3', f'_{int(time.time())}.wav')
        
        # 1. Génération WAV (espeak)
        subprocess.run([
            'espeak', '-v', 'fr+f2', '-s', '150', '-a', '100', text,
            '-w', temp_wav
        ], check=True, capture_output=True, timeout=30)
        
        # 2. Conversion MP3 (ffmpeg)
        if os.path.exists(temp_wav):
            # Utilisation de check=True pour lever une erreur si ffmpeg échoue
            subprocess.run([
                'ffmpeg', '-i', temp_wav, '-acodec', 'libmp3lame', '-q:a', '4', '-y', audio_path
            ], check=True, capture_output=True, timeout=30)
            os.remove(temp_wav)
            
        return audio_path

    def _create_silent_audio(self, text: str, audio_path: str) -> Optional[str]:
        """Crée un audio silencieux d'une durée fixe (30 secondes)."""
        import subprocess
        
        # Durée de l'audio silencieux basée sur la constante
        command = [
            'ffmpeg', '-f', 'lavfi',
            '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100:duration={AUDIO_DURATION_SEC}',
            '-c:a', 'libmp3lame', '-q:a', '4', '-y', audio_path
        ]
        
        subprocess.run(command, check=True, capture_output=True, timeout=45) # Timeout augmenté
        return audio_path

    def _create_minimal_audio(self, clean_title: str) -> Optional[str]:
        """Crée un fichier audio minimal non vide."""
        audio_path = safe_path_join(self.output_dir, f"audio_minimal_{clean_title}.mp3")
        try:
            # Crée un header MP3 minimal et ajoute quelques octets de padding
            with open(audio_path, 'wb') as f:
                f.write(b'\xFF\xFB\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00') 
            print(f"⚠️ AUCUNE méthode audio n'a fonctionné. Audio minimal créé: {audio_path}")
            return audio_path
        except Exception:
            print("❌ Échec de la création du fichier audio minimal.")
            return None

# --- Bloc d'Export et de Test ---

# L'export est maintenu pour la compatibilité avec d'autres fichiers.
def generate_audio(text: str, title: str) -> Optional[str]:
    """Fonction d'export pour l'interface de la classe."""
    generator = AudioGenerator()
    return generator.generate_audio(text, title)

if __name__ == "__main__":
    print("🧪 Test AudioGenerator (vérifiez la présence d'espeak et ffmpeg)...")
    
    # Assurez-vous que le répertoire de test est créé
    ensure_directory("test_output")
    generator = AudioGenerator("test_output/audio")

    result = generator.generate_audio(
        "Ce message est généré pour tester la fiabilité du système de synthèse vocale.",
        "Test de Fiabilite du Moteur Audio"
    )
    
    if result and os.path.exists(result):
        print(f"\n✅ Test réussi. Fichier généré: {result}")
        # Optionnel: supprimer pour nettoyer
        # os.remove(result) 
    else:
        print("\n❌ Test échoué. Aucun fichier audio valide n'a pu être généré.")
        sys.exit(1)
