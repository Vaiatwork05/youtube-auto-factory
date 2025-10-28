import edge_tts
import asyncio
import os
from gtts import gTTS

class AudioGenerator:
    def __init__(self):
        self.output_dir = "output/audio"
        os.makedirs(self.output_dir, exist_ok=True)
    
    async def generate_voice_edge(self, text, output_file, voice="fr-FR-DeniseNeural"):
        """Génère une voix off avec Edge TTS (qualité supérieure)"""
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)
            print(f"✅ Audio généré: {output_file}")
            return True
        except Exception as e:
            print(f"🚨 Erreur Edge TTS: {e}")
            return False
    
    def generate_voice_gtts(self, text, output_file, lang='fr'):
        """Génère une voix off avec Google TTS (fallback)"""
        try:
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(output_file)
            print(f"✅ Audio Google TTS généré: {output_file}")
            return True
        except Exception as e:
            print(f"🚨 Erreur Google TTS: {e}")
            return False
    
    def generate_audio(self, script_data, video_title):
        """Génère l'audio pour la vidéo"""
        output_file = os.path.join(self.output_dir, f"audio_{video_title.replace(' ', '_')}.mp3")
        
        # Texte complet pour la voix off
        full_text = f"{script_data['title']}. {script_data['script']}"
        
        # Essayer Edge TTS d'abord (meilleure qualité)
        try:
            # Pour l'async dans un contexte sync
            async def run_edge_tts():
                return await self.generate_voice_edge(full_text, output_file)
            
            # Exécuter l'async dans un contexte sync
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(run_edge_tts())
            loop.close()
            
            if success:
                return output_file
        except Exception as e:
            print(f"⚠️  Edge TTS échoué: {e}")
        
        # Fallback vers Google TTS
        if self.generate_voice_gtts(full_text, output_file):
            return output_file
        
        print("❌ Aucun TTS n'a fonctionné")
        return None

# Test
if __name__ == "__main__":
    generator = AudioGenerator()
    test_script = {
        "title": "Test Audio",
        "script": "Ceci est un test de génération de voix automatique."
    }
    generator.generate_audio(test_script, "test")
