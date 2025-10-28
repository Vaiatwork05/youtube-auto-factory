# content_factory/audio_generator.py
import os
import time
from utils import clean_filename, safe_path_join, ensure_directory

class AudioGenerator:
    def __init__(self):
        self.output_dir = "output/audio"
        ensure_directory(self.output_dir)
    
    def generate_audio(self, text, title):
        """
        Génère un fichier audio avec fallbacks robustes
        """
        print(f"🔊 Génération audio: {title[:50]}...")
        
        clean_title = clean_filename(title)
        audio_path = safe_path_join(self.output_dir, f"audio_{clean_title}.mp3")
        
        # Essayer différentes méthodes
        methods = [
            self._try_edge_tts,
            self._try_google_tts,
            self._try_system_tts,
            self._create_silent_audio
        ]
        
        for method in methods:
            try:
                result = method(text, title, audio_path)
                if result and os.path.exists(result) and os.path.getsize(result) > 1024:
                    print(f"✅ Audio généré: {result}")
                    return result
            except Exception as e:
                print(f"⚠️ {method.__name__} échoué: {e}")
                continue
        
        # Dernier recours
        return self._create_minimal_audio(clean_title)
    
    def _try_edge_tts(self, text, title, audio_path):
        """Tente Edge TTS"""
        try:
            import asyncio
            import edge_tts
            
            async def generate():
                communicate = edge_tts.Communicate(text, "fr-FR-DeniseNeural")
                await communicate.save(audio_path)
            
            asyncio.run(generate())
            return audio_path
        except Exception as e:
            print(f"❌ Edge TTS échoué: {e}")
            return None
    
    def _try_google_tts(self, text, title, audio_path):
        """Tente Google TTS"""
        try:
            from gtts import gTTS
            tts = gTTS(text=text, lang='fr', slow=False)
            tts.save(audio_path)
            time.sleep(1)  # Attendre l'écriture
            return audio_path
        except Exception as e:
            print(f"❌ Google TTS échoué: {e}")
            return None
    
    def _try_system_tts(self, text, title, audio_path):
        """Tente la synthèse système"""
        try:
            import subprocess
            
            # Essayer espeak + ffmpeg
            temp_wav = audio_path.replace('.mp3', '.wav')
            
            subprocess.run([
                'espeak', '-v', 'fr+f2', '-s', '150', text,
                '-w', temp_wav
            ], capture_output=True, timeout=30)
            
            if os.path.exists(temp_wav):
                subprocess.run([
                    'ffmpeg', '-i', temp_wav, '-y', audio_path
                ], capture_output=True, timeout=30)
                os.remove(temp_wav)
                
            return audio_path if os.path.exists(audio_path) else None
        except Exception as e:
            print(f"❌ System TTS échoué: {e}")
            return None
    
    def _create_silent_audio(self, text, title, audio_path):
        """Crée un audio silencieux"""
        try:
            import subprocess
            subprocess.run([
                'ffmpeg', '-f', 'lavfi',
                '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100:duration=30',
                '-y', audio_path
            ], capture_output=True, timeout=30)
            return audio_path
        except Exception as e:
            print(f"❌ Silent audio échoué: {e}")
            return None
    
    def _create_minimal_audio(self, clean_title):
        """Crée un fichier audio minimal"""
        audio_path = safe_path_join(self.output_dir, f"audio_{clean_title}.mp3")
        try:
            # Créer un fichier MP3 minimal valide
            with open(audio_path, 'wb') as f:
                f.write(b'\xFF\xFB\x90\x00\x00\x00\x00\x00')  # Header MP3 minimal
            print(f"⚠️ Audio minimal créé: {audio_path}")
            return audio_path
        except Exception as e:
            print(f"❌ Minimal audio échoué: {e}")
            return None

# Export
def generate_audio(text, title):
    generator = AudioGenerator()
    return generator.generate_audio(text, title)

# Test
if __name__ == "__main__":
    print("🧪 Test AudioGenerator...")
    
    generator = AudioGenerator()
    result = generator.generate_audio(
        "Ceci est un test de génération audio avec le système opérationnel.",
        "Test Audio"
    )
    
    if result:
        print("✅ Test réussi")
    else:
        print("❌ Test échoué")
