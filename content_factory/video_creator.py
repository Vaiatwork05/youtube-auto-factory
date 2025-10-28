import os
import tempfile
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

class VideoCreator:
    def __init__(self):
        self.video_duration = 30  # 30 secondes
    
    def create_video(self, script_data, output_dir="output"):
        """Crée une vidéo simple avec le script"""
        
        # Créer le dossier de sortie
        os.makedirs(output_dir, exist_ok=True)
        
        # Créer un clip de fond (noir)
        background = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=self.video_duration)
        
        # Créer un clip texte
        txt_clip = TextClip(
            script_data["script"],
            fontsize=40,
            color='white',
            font='Arial-Bold',
            stroke_color='black',
            stroke_width=2
        )
        txt_clip = txt_clip.set_position('center').set_duration(self.video_duration)
        
        # Combiner les clips
        video = CompositeVideoClip([background, txt_clip])
        
        # Sauvegarder la vidéo
        output_path = os.path.join(output_dir, f"video_{script_data['title'].replace(' ', '_')}.mp4")
        video.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        print(f"✅ Vidéo créée: {output_path}")
        return output_path

# Test
if __name__ == "__main__":
    creator = VideoCreator()
    test_script = {
        "title": "Test Video",
        "script": "Ceci est un test de création vidéo automatique!"
    }
    creator.create_video(test_script)
