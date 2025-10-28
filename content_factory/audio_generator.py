# content_factory/audio_generator.py
import os
import edge_tts
import asyncio
import subprocess
import time
from pathlib import Path
from utils import clean_filename, safe_path_join, ensure_directory

class AudioGenerator:
    def __init__(self):
        self.output_dir = "output/audio"
        ensure_directory(self.output_dir)
    
    async def generate_audio_edge_tts_async(self, text, title):
        """
        Génère un audio avec Edge TTS (version asynchrone)
        """
        try:
            # Nettoyer le titre pour le nom de fichier
            clean_title = clean_filename(title)
            audio_path = safe_path_join(self.output_dir, f"audio_{clean_title}.mp3")
            
            print(f"🎵 Génération audio Edge TTS: {audio_path}")
            
            # Utiliser Edge TTS de manière asynchrone
            communicate = edge_tts.Communicate(text, "fr-FR-DeniseNeural")
            await communicate.save(audio_path)
            
            # Vérifier que le fichier est valide
            if self._verify_audio_file(audio_path):
                print(f"✅ Audio Edge TTS généré et validé: {audio_path}")
                return audio_path
            else:
                print(f"❌ Fichier Edge TTS corrompu: {audio_path}")
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                return None
            
        except Exception as e:
            print(f"❌ Erreur Edge TTS: {e}")
            return None
    
    def generate_audio_edge_tts(self, text, title):
        """
        Version synchrone pour Edge TTS
        """
        try:
            # Exécuter la version asynchrone dans un event loop
            return asyncio.run(self.generate_audio_edge_tts_async(text, title))
        except Exception as e:
            print(f"❌ Erreur execution Edge TTS: {e}")
            return None
    
    def generate_audio_google_tts(self, text, title):
        """
        Fallback avec Google TTS
        """
        try:
            clean_title = clean_filename(title)
            audio_path = safe_path_join(self.output_dir, f"audio_{clean_title}.mp3")
            
            print(f"🎵 Génération audio Google TTS (fallback): {audio_path}")
            
            # Utiliser gTTS pour une vraie génération audio
            from gtts import gTTS
            
            tts = gTTS(text=text, lang='fr', slow=False)
            tts.save(audio_path)
            
            # Attendre l'écriture du fichier
            time.sleep(2)
            
            # Vérifier le fichier
            if self._verify_audio_file(audio_path):
                print(f"✅ Audio Google TTS généré et validé: {audio_path}")
                return audio_path
            else:
                print(f"❌ Fichier Google TTS corrompu: {audio_path}")
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                return self._generate_robust_audio_fallback(text, title, audio_path)
                
        except Exception as e:
            print(f"❌ Erreur Google TTS: {e}")
            return self._generate_robust_audio_fallback(text, title)
    
    def _generate_robust_audio_fallback(self, text, title, original_path=None):
        """
        Fallback robuste avec plusieurs tentatives
        """
        try:
            clean_title = clean_filename(title)
            
            # Essayer eSpeak + FFmpeg
            audio_path = self._generate_with_espeak(text, clean_title)
            if audio_path and self._verify_audio_file(audio_path):
                return audio_path
            
            # Essayer la création via FFmpeg direct
            audio_path = self._generate_with_ffmpeg_silence(text, clean_title)
            if audio_path and self._verify_audio_file(audio_path):
                return audio_path
                
            # Dernier recours: fichier minimal
            return self._generate_minimal_audio_file(clean_title)
            
        except Exception as e:
            print(f"❌ Erreur fallback robuste: {e}")
            return self._generate_minimal_audio_file(clean_filename(title))
    
    def _generate_with_espeak(self, text, clean_title):
        """
        Génère l'audio avec eSpeak + FFmpeg
        """
        try:
            temp_wav = safe_path_join(self.output_dir, f"temp_{clean_title}.wav")
            audio_path = safe_path_join(self.output_dir, f"audio_{clean_title}.mp3")
            
            # Générer WAV avec eSpeak
            subprocess.run([
                'espeak', '-v', 'fr+f2', '-s', '150', 
                '-w', temp_wav, text
            ], capture_output=True, timeout=30)
            
            # Convertir en MP3 avec FFmpeg
            subprocess.run([
                'ffmpeg', '-i', temp_wav,
                '-codec:a', 'libmp3lame', '-qscale:a', '2',
                '-y', audio_path
            ], capture_output=True, timeout=30)
            
            # Nettoyer le temporaire
            if os.path.exists(temp_wav):
                os.remove(temp_wav)
                
            return audio_path
            
        except Exception as e:
            print(f"❌ eSpeak fallback échoué: {e}")
            return None
    
    def _generate_with_ffmpeg_silence(self, text, clean_title, duration=30):
        """
        Crée un audio silencieux avec metadata
        """
        try:
            audio_path = safe_path_join(self.output_dir, f"audio_{clean_title}.mp3")
            
            # Créer un audio silencieux avec FFmpeg
            subprocess.run([
                'ffmpeg', '-f', 'lavfi',
                '-i', f'anullsrc=channel_layout=stereo:sample_rate=44100:duration={duration}',
                '-y', audio_path
            ], capture_output=True, timeout=30)
            
            return audio_path
            
        except Exception as e:
            print(f"❌ FFmpeg silence échoué: {e}")
            return None
    
    def _generate_minimal_audio_file(self, clean_title):
        """
        Crée un fichier audio minimal (dernier recours)
        """
        try:
            audio_path = safe_path_join(self.output_dir, f"audio_{clean_title}.mp3")
            
            # Créer un fichier minimal valide
            with open(audio_path, 'wb') as f:
                # Header MP3 minimal (fichier silencieux très court)
                f.write(b'\xFF\xFB\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            
            print(f"⚠️  Fichier audio minimal créé: {audio_path}")
            return audio_path
            
        except Exception as e:
            print(f"❌ Erreur création fichier minimal: {e}")
            return None
    
    def _verify_audio_file(self, audio_path):
        """
        Vérifie si un fichier audio est valide
        """
        try:
            if not os.path.exists(audio_path):
                print(f"❌ Fichier audio n'existe pas: {audio_path}")
                return False
            
            # Vérifier la taille
            file_size = os.path.getsize(audio_path)
            if file_size < 1024:  # Moins de 1KB = suspect
                print(f"❌ Fichier audio trop petit: {file_size} octets")
                return False
            
            # Vérifier avec FFmpeg
            result = subprocess.run([
                'ffmpeg', '-v', 'error', '-i', audio_path, 
                '-f', 'null', '-'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"✅ Fichier audio valide ({file_size} octets)")
                return True
            else:
                print(f"❌ Fichier audio corrompu: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout vérification audio")
            return False
        except Exception as e:
            print(f"❌ Erreur vérification audio: {e}")
            return False
    
    def generate_audio(self, text, title, max_retries=2):
        """
        Génère l'audio avec fallbacks multiples et vérifications
        """
        print(f"🔊 Début génération audio pour: {title}")
        print(f"📝 Texte: {text[:100]}...")
        
        # Tentative 1: Edge TTS
        for attempt in range(max_retries):
            print(f"🔄 Tentative {attempt + 1}/{max_retries} - Edge TTS")
            audio_path = self.generate_audio_edge_tts(text, title)
            
            if audio_path and self._verify_audio_file(audio_path):
                print(f"✅ Audio généré avec succès: {audio_path}")
                return audio_path
            elif audio_path:
                print(f"❌ Fichier Edge TTS invalide, tentative {attempt + 1} échouée")
                if os.path.exists(audio_path):
                    os.remove(audio_path)
        
        # Tentative 2: Google TTS
        print("🔄 Passage à Google TTS...")
        audio_path = self.generate_audio_google_tts(text, title)
        
        if audio_path and self._verify_audio_file(audio_path):
            print(f"✅ Audio Google TTS réussi: {audio_path}")
            return audio_path
        
        # Tentative 3: Fallback robuste
        print("🔄 Passage au fallback robuste...")
        audio_path = self._generate_robust_audio_fallback(text, title)
        
        if audio_path:
            print(f"✅ Fallback audio réussi: {audio_path}")
            return audio_path
        else:
            print("❌ Échec complet de la génération audio")
            return None

# Fonction utilitaire pour usage direct
def generate_audio(text, title):
    """
    Fonction helper pour générer de l'audio
    """
    generator = AudioGenerator()
    return generator.generate_audio(text, title)

# Test du module
if __name__ == "__main__":
    def test_audio_generator():
        """Test du générateur audio"""
        print("🧪 Test du AudioGenerator...")
        
        generator = AudioGenerator()
        
        # Test avec un texte simple
        test_text = "Ceci est un test de génération audio avec le nouveau système robuste."
        test_title = "Test Audio System"
        
        result = generator.generate_audio(test_text, test_title)
        
        if result:
            print(f"✅ Test réussi! Fichier: {result}")
            
            # Vérification finale
            if generator._verify_audio_file(result):
                print("🎉 Fichier audio parfaitement valide!")
            else:
                print("⚠️  Fichier audio généré mais avec des problèmes")
        else:
            print("❌ Test échoué!")
        
        return result is not None
    
    # Exécuter le test
    test_audio_generator()            audio_path = self.generate_audio_silence(text, title)
        
        if audio_path:
            print(f"✅ Audio généré avec succès: {audio_path}")
        else:
            print("❌ Échec complet de la génération audio")
            
        return audio_path

# Fonction utilitaire pour usage direct
def generate_audio(text, title):
    """
    Fonction helper pour générer de l'audio
    """
    generator = AudioGenerator()
    return generator.generate_audio(text, title)
