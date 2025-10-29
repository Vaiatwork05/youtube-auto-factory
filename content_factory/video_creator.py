# content_factory/video_creator.py
import os
import sys
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips
from PIL import Image
import time

class VideoCreator:
    def __init__(self):
        self.output_dir = "output/videos"
        self._ensure_directory(self.output_dir)
    
    def _ensure_directory(self, path):
        """Crée le dossier s'il n'existe pas"""
        os.makedirs(path, exist_ok=True)
    
    def create_video(self, content_data):
        """
        Crée une vidéo simple et robuste
        """
        try:
            print("🎬 Début création vidéo...")
            
            # Extraire les données
            title = content_data.get('title', 'Ma Vidéo')
            script = content_data.get('script', 'Contenu vidéo généré automatiquement.')
            
            # Nettoyer le titre pour le fichier
            clean_title = self._clean_filename(title)
            video_path = os.path.join(self.output_dir, f"video_{clean_title}.mp4")
            
            print(f"📝 Titre: {title}")
            print(f"💾 Fichier: {video_path}")
            
            # Générer l'audio
            print("🔊 Génération audio...")
            audio_path = self._generate_audio(script, title)
            
            # Obtenir les images
            print("🖼️ Récupération images...")
            image_paths = self._get_images(content_data, num_images=6)
            
            # Vérifier si on a des images
            if not image_paths:
                print("❌ Aucune image disponible, création d'images de secours...")
                image_paths = self._create_fallback_images(6)
            
            # Créer la vidéo
            print("🎥 Assemblage vidéo...")
            result_path = self._create_video_from_assets(image_paths, audio_path, video_path)
            
            if result_path and os.path.exists(result_path):
                file_size = os.path.getsize(result_path)
                print(f"✅ Vidéo créée avec succès: {result_path} ({file_size} octets)")
                return result_path
            else:
                print("❌ Échec création vidéo")
                return None
                
        except Exception as e:
            print(f"❌ Erreur création vidéo: {e}")
            return self._create_fallback_video(content_data)
    
    def _generate_audio(self, text, title):
        """Génère un fichier audio simple"""
        try:
            from content_factory.audio_generator import AudioGenerator
            generator = AudioGenerator()
            return generator.generate_audio(text, title)
        except Exception as e:
            print(f"⚠️ Erreur génération audio: {e}")
            # Fallback: créer un fichier audio minimal
            audio_dir = "output/audio"
            self._ensure_directory(audio_dir)
            audio_path = os.path.join(audio_dir, f"audio_{self._clean_filename(title)}.mp3")
            
            # Créer un fichier audio silencieux avec ffmpeg
            try:
                import subprocess
                subprocess.run([
                    'ffmpeg', '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
                    '-t', '30', '-y', audio_path
                ], capture_output=True, timeout=30)
            except Exception as e:
                print(f"⚠️ Erreur ffmpeg: {e}")
                # Dernier recours: fichier vide
                open(audio_path, 'wb').close()
            
            return audio_path
    
    def _get_images(self, content_data, num_images=6):
        """Récupère des images"""
        try:
            from content_factory.image_manager import ImageManager
            manager = ImageManager()
            return manager.get_images_for_content(content_data, num_images)
        except Exception as e:
            print(f"⚠️ Erreur récupération images: {e}")
            # Fallback: créer des placeholders
            return self._create_fallback_images(num_images)
    
    def _create_fallback_images(self, num_images):
        """Crée des images de secours"""
        images = []
        image_dir = "output/images"
        self._ensure_directory(image_dir)
        
        for i in range(num_images):
            img_path = os.path.join(image_dir, f"placeholder_{i}.jpg")
            self._create_simple_image(img_path, f"Image {i+1}")
            images.append(img_path)
            print(f"🖼️ Image de secours créée: {img_path}")
        
        return images
    
    def _create_simple_image(self, path, text):
        """Crée une image simple avec texte"""
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Créer image 1280x720
            img = Image.new('RGB', (1280, 720), color=(53, 94, 159))
            draw = ImageDraw.Draw(img)
            
            # Essayer différentes polices
            try:
                font = ImageFont.truetype("arial.ttf", 60)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 60)
                except:
                    font = ImageFont.load_default()
            
            # Centrer le texte
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            x = (1280 - text_width) // 2
            y = (720 - 60) // 2
            
            draw.text((x, y), text, fill=(255, 255, 255), font=font)
            img.save(path, quality=85)
            
        except Exception as e:
            print(f"⚠️ Erreur création image: {e}")
            # Créer une image vide
            Image.new('RGB', (1280, 720), color=(100, 100, 100)).save(path)
    
    def _create_video_from_assets(self, image_paths, audio_path, output_path):
        """Crée la vidéo finale"""
        try:
            # Vérifier les fichiers
            if not os.path.exists(audio_path):
                raise Exception("Fichier audio manquant")
            
            if not image_paths:
                raise Exception("Aucune image disponible")
            
            # Durée de l'audio
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            if audio_duration <= 0:
                audio_duration = 30
            
            # Calculer durée par image
            duration_per_image = audio_duration / len(image_paths)
            
            print(f"⏱️ Durée audio: {audio_duration:.1f}s")
            print(f"🖼️ Images: {len(image_paths)}")
            print(f"⏰ Durée/image: {duration_per_image:.1f}s")
            
            # Créer les clips images
            video_clips = []
            for i, img_path in enumerate(image_paths):
                if os.path.exists(img_path):
                    clip = ImageClip(img_path, duration=duration_per_image)
                    clip = clip.resize(height=720)  # Format 16:9
                    video_clips.append(clip)
                    print(f"📹 Clip {i+1}/{len(image_paths)} créé")
            
            if not video_clips:
                raise Exception("Aucun clip valide créé")
            
            # Concaténer et ajouter l'audio
            final_video = concatenate_videoclips(video_clips, method="compose")
            final_video = final_video.set_audio(audio_clip)
            final_video = final_video.set_duration(audio_duration)
            
            # Exporter
            final_video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                verbose=False,
                logger=None,
                threads=4
            )
            
            # Nettoyer la mémoire
            for clip in video_clips:
                clip.close()
            audio_clip.close()
            final_video.close()
            
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur création vidéo assets: {e}")
            return None
    
    def _create_fallback_video(self, content_data):
        """Crée une vidéo de secours ultra simple"""
        try:
            title = content_data.get('title', 'Vidéo Secours')
            video_path = os.path.join(self.output_dir, f"fallback_{self._clean_filename(title)}.mp4")
            
            # Créer une image simple
            img_path = os.path.join("output/images", "fallback.jpg")
            self._create_simple_image(img_path, title)
            
            # Créer une vidéo de 10 secondes
            clip = ImageClip(img_path, duration=10)
            clip = clip.resize(height=720)
            clip.write_videofile(
                video_path,
                fps=24,
                verbose=False,
                logger=None
            )
            clip.close()
            
            print(f"✅ Vidéo de secours créée: {video_path}")
            return video_path
            
        except Exception as e:
            print(f"❌ Échec vidéo secours: {e}")
            return None
    
    def _clean_filename(self, text):
        """Nettoie le texte pour un nom de fichier valide"""
        import re
        clean = re.sub(r'[^\w\s-]', '', text)
        clean = re.sub(r'[-\s]+', '_', clean)
        return clean[:50]

# Fonction principale d'export
def create_video(content_data):
    """Fonction principale pour créer une vidéo"""
    creator = VideoCreator()
    return creator.create_video(content_data)

# Test SIMPLE et PROPRE
if __name__ == "__main__":
    print("🧪 Test VideoCreator...")
    
    test_data = {
        'title': 'Test Vidéo Opérationnelle',
        'script': 'Ceci est un test du système de création vidéo complètement opérationnel.',
        'keywords': ['test', 'video', 'systeme']
    }
    
    result = create_video(test_data)
    
    if result:
        print("✅ Test réussi")
    else:
        print("❌ Test échoué")
