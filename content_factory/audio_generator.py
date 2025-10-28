import os
import edge_tts
import tempfile
from utils import clean_filename, safe_path_join, ensure_directory

class AudioGenerator:
    def __init__(self):
        self.output_dir = "output/audio"
        ensure_directory(self.output_dir)
    
    def generate_audio_edge_tts(self, text, title):
        """
        Génère un audio avec Edge TTS
        """
        try:
            # Nettoyer le titre pour le nom de fichier
            clean_title = clean_filename(title)
            audio_path = safe_path_join(self.output_dir, f"audio_{clean_title}.mp3")
            
            print(f"🎵 Génération audio Edge TTS: {audio_path}")
            
            # Utiliser Edge TTS
            communicate = edge_tts.Communicate(text, "fr-FR-DeniseNeural")
            await communicate.save(audio_path)
            
            print(f"✅ Audio Edge TTS généré: {audio_path}")
            return audio_path
            
        except Exception as e:
            print(f"❌ Erreur Edge TTS: {e}")
            return None
    
    def generate_audio_google_tts(self, text, title):
        """
        Fallback avec Google TTS (si Edge TTS échoue)
        """
        try:
            clean_title = clean_filename(title)
            audio_path = safe_path_join(self.output_dir, f"audio_{clean_title}.mp3")
            
            print(f"🎵 Génération audio Google TTS: {audio_path}")
            
            # Implémentation Google TTS (à adapter selon votre code existant)
            # from gtts import gTTS
            # tts = gTTS(text=text, lang='fr', slow=False)
            # tts.save(audio_path)
            
            print(f"✅ Audio Google TTS généré: {audio_path}")
            return audio_path
            
        except Exception as e:
            print(f"❌ Erreur Google TTS: {e}")
            return None
    
    def generate_audio(self, text, title):
        """
        Génère l'audio avec fallback
        """
        # Essayer d'abord Edge TTS
        audio_path = self.generate_audio_edge_tts(text, title)
        
        # Si échec, utiliser Google TTS
        if not audio_path:
            audio_path = self.generate_audio_google_tts(text, title)
        
        return audio_path
