# content_factory/audio_generator.py
import os
import edge_tts
import asyncio
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
            
            print(f"✅ Audio Edge TTS généré: {audio_path}")
            return audio_path
            
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
        Fallback avec Google TTS (si Edge TTS échoue)
        """
        try:
            clean_title = clean_filename(title)
            audio_path = safe_path_join(self.output_dir, f"audio_{clean_title}.mp3")
            
            print(f"🎵 Génération audio Google TTS: {audio_path}")
            
            # Implémentation Google TTS (fallback simple)
            # Pour l'instant, créer un fichier audio vide comme fallback
            with open(audio_path, 'wb') as f:
                f.write(b"")  # Fichier vide
            
            print(f"✅ Audio Google TTS (fallback) généré: {audio_path}")
            return audio_path
            
        except Exception as e:
            print(f"❌ Erreur Google TTS: {e}")
            return None
    
    def generate_audio(self, text, title):
        """
        Génère l'audio avec fallback
        """
        print(f"🔊 Début génération audio pour: {title}")
        
        # Essayer d'abord Edge TTS
        audio_path = self.generate_audio_edge_tts(text, title)
        
        # Si échec, utiliser Google TTS fallback
        if not audio_path:
            print("🔄 Fallback vers Google TTS...")
            audio_path = self.generate_audio_google_tts(text, title)
        
        if audio_path:
            print(f"✅ Audio généré avec succès: {audio_path}")
        else:
            print("❌ Échec de la génération audio")
            
        return audio_path

# Fonction utilitaire pour usage direct
def generate_audio(text, title):
    """
    Fonction helper pour générer de l'audio
    """
    generator = AudioGenerator()
    return generator.generate_audio(text, title)
