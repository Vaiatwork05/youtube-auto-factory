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

# Test - VERSION CORRIGÉE
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
        print("❌ Test échoué")        self._ensure_directory(image_dir)
        
        # CORRECTION : Séparer le for et le print
        for i in range(num_images):
            img_path = os.path.join(image_dir, f"placeholder_{i}.jpg")
            self._create_simple_image(img_path, f"Image {i+1}")
            images.append(img_path)
            print(f"🖼️ Image de secours créée: {img_path}")  # Déplacé ici
        
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

# Test
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
        
        self._ensure_directory(image_dir)
        
        for i in range(num_images):
            img_path = os.path.join(image_dir, f"placeholder_{i}.jpg")
            self._create_simple_image(img_path, f"Image {i+1}")
            images.append(img_path)
        
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

# Test
if __name__ == "__main__":
    print("🧪 Test VideoCreator...")
    
    test_data = {
        'title': 'Test Vidéo Opérationnelle',
        'script': 'Ceci est un test du système de création vidéo complètement opérationnel.',
        'keywords': ['test', 'video', 'systeme']
    }
    
    result = create_video(test_data)
    
    # CORRECTION : Séparer le print et le if correctement
    if result:
        print("✅ Test réussi")
    else:
        print("❌ Test échoué")        for i in range(num_images):
            img_path = os.path.join(image_dir, f"placeholder_{i}.jpg")
            self._create_simple_image(img_path, f"Image {i+1}")
            images.append(img_path)
        
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

# Test
if __name__ == "__main__":
    print("🧪 Test VideoCreator...")
    
    test_data = {
        'title': 'Test Vidéo Opérationnelle',
        'script': 'Ceci est un test du système de création vidéo complètement opérationnel.',
        'keywords': ['test', 'video', 'systeme']
    }
    
    result = create_video(test_data)
    
    # CORRECTION : Séparer le print et le if sur des lignes différentes
    if result:
        print("✅ Test réussi")
    else:
        print("❌ Test échoué")    
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

# Test - CORRIGÉ (chaîne correctement terminée)
if __name__ == "__main__":
    print("🧪 Test VideoCreator...")
    
    test_data = {
        'title': 'Test Vidéo Opérationnelle',
        'script': 'Ceci est un test du système de création vidéo complètement opérationnel.',
        'keywords': ['test', 'video', 'systeme']
    }
    
    result = create_video(test_data)
    if result:
        print(f"🎉 Test réussi: {result}")
    else:
    if not image_paths:
        print("❌ Test échoué")
                print("❌ Aucune image disponible, création d'images par défaut")
                image_paths = [image_manager.create_placeholder_image("default", i) for i in range(8)]
            
            print(f"✅ {len(image_paths)} images obtenues")
            
            # Créer la vidéo avec les images et l'audio
            print("🎥 Assemblage de la vidéo...")
            final_video_path = self.create_video_from_images_and_audio(image_paths, audio_path, video_path)
            
            print(f"✅ Vidéo créée avec succès: {final_video_path}")
            return final_video_path
            
        except Exception as e:
            print(f"❌ Erreur création vidéo: {e}")
            import traceback
            traceback.print_exc()
            
            # Tentative de fallback
            try:
                print("🔄 Tentative de vidéo de secours...")
                return self.create_fallback_video(content_data)
            except Exception as fallback_error:
                print(f"❌ Échec vidéo de secours: {fallback_error}")
                return None
    
    def create_simple_video(self, content_data):
        """
        Version simplifiée pour la compatibilité
        """
        return self.create_professional_video(content_data)
    
    def create_video_from_images_and_audio(self, image_paths, audio_path, output_path):
        """
        Crée une vidéo à partir d'images et d'audio
        """
        video_clips = []
        audio_clip = None
        final_video = None
        
        try:
            # Vérifier que l'audio existe
            if not os.path.exists(audio_path):
                raise Exception(f"Fichier audio introuvable: {audio_path}")
            
            # Charger l'audio avec gestion d'erreur
            print("🔊 Chargement de l'audio...")
            try:
                audio_clip = AudioFileClip(audio_path)
                audio_duration = audio_clip.duration
                
                if audio_duration <= 0:
                    print("⚠️ Durée audio nulle, utilisation durée par défaut")
                    audio_duration = 30.0  # Durée par défaut
            except Exception as audio_error:
                print(f"⚠️ Erreur chargement audio: {audio_error}")
                audio_duration = 30.0  # Durée par défaut
                audio_clip = None
            
            # Calculer la durée par image
            num_images = len(image_paths)
            duration_per_image = audio_duration / num_images if num_images > 0 else 5.0
            
            print(f"⏱️ Durée vidéo: {audio_duration:.2f}s")
            print(f"🖼️ Nombre d'images: {num_images}")
            print(f"⏰ Durée par image: {duration_per_image:.2f}s")
            
            # Créer les clips vidéo
            for i, image_path in enumerate(image_paths):
                try:
                    # Vérifier que l'image existe
                    if not os.path.exists(image_path):
                        print(f"⚠️ Image manquante: {image_path}")
                        continue
                    
                    # Vérifier que l'image est valide
                    try:
                        with Image.open(image_path) as img:
                            img.verify()
                    except Exception as img_error:
                        print(f"⚠️ Image corrompue {image_path}: {img_error}")
                        continue
                    
                    print(f"📹 Création clip {i+1}/{num_images}: {os.path.basename(image_path)}")
                    
                    # Créer un clip image avec la durée calculée
                    image_clip = ImageClip(image_path, duration=duration_per_image)
                    
                    # Redimensionner pour format 16:9 (1920x1080)
                    try:
                        image_clip = image_clip.resize(height=1080)
                        
                        # Centrer l'image si nécessaire
                        if image_clip.w < 1920:
                            image_clip = image_clip.resize(width=1920)
                        elif image_clip.w > 1920:
                            # Recadrer au centre
                            image_clip = image_clip.crop(
                                x_center=image_clip.w/2, 
                                y_center=image_clip.h/2, 
                                width=1920, 
                                height=1080
                            )
                    except Exception as resize_error:
                        print(f"⚠️ Erreur redimensionnement image: {resize_error}")
                        # Continuer avec l'image originale
                    
                    video_clips.append(image_clip)
                    
                except Exception as e:
                    print(f"⚠️ Erreur création clip {i+1}: {e}")
                    continue
            
            if not video_clips:
                raise Exception("Aucun clip vidéo créé - toutes les images ont échoué")
            
            print(f"✅ {len(video_clips)} clips créés avec succès")
            
            # Concaténer tous les clips
            print("🎞️ Concaténation des clips...")
            final_video = concatenate_videoclips(video_clips, method="compose")
            
            # Ajouter l'audio si disponible
            if audio_clip:
                print("🔊 Ajout de l'audio...")
                final_video = final_video.set_audio(audio_clip)
                final_video = final_video.set_duration(audio_duration)
            else:
                print("⚠️ Aucun audio disponible, vidéo silencieuse")
                final_video = final_video.set_duration(audio_duration)
            
            # Exporter la vidéo
            print("📤 Export de la vidéo...")
            final_video.write_videofile(
                output_path,
                fps=24,
                codec='libx264',
                audio_codec='aac' if audio_clip else None,
                verbose=False,
                logger=None,
                threads=4,
                preset='medium',
                bitrate='2000k'
            )
            
            print(f"✅ Vidéo exportée: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Erreur création vidéo from images: {e}")
            import traceback
            traceback.print_exc()
            
            # Nettoyer avant de relancer l'erreur
            self._cleanup_clips(video_clips, audio_clip, final_video)
            raise
        
        finally:
            # Nettoyer la mémoire dans tous les cas
            self._cleanup_clips(video_clips, audio_clip, final_video)
    
    def _cleanup_clips(self, video_clips, audio_clip, final_video):
        """
        Nettoie tous les clips de la mémoire
        """
        print("🧹 Nettoyage mémoire...")
        try:
            for clip in video_clips:
                try:
                    if hasattr(clip, 'close'):
                        clip.close()
                except Exception as e:
                    print(f"⚠️ Erreur fermeture clip: {e}")
            
            if audio_clip and hasattr(audio_clip, 'close'):
                try:
                    audio_clip.close()
                except Exception as e:
                    print(f"⚠️ Erreur fermeture audio: {e}")
            
            if final_video and hasattr(final_video, 'close'):
                try:
                    final_video.close()
                except Exception as e:
                    print(f"⚠️ Erreur fermeture vidéo: {e}")
                    
        except Exception as e:
            print(f"⚠️ Erreur lors du nettoyage: {e}")
    
    def create_fallback_video(self, content_data, output_dir="output"):
        """
        Crée une vidéo de secours en cas d'erreur
        """
        try:
            print("🔄 Création vidéo de secours...")
            
            title = content_data.get('title', 'Video de secours')
            clean_title = clean_filename(title)
            video_path = safe_path_join(self.output_dir, f"fallback_{clean_title}.mp4")
            
            # Créer une image simple
            image_manager = self._get_image_manager()
            image_path = image_manager.create_placeholder_image("secours", 0)
            
            # Créer un clip image simple
            image_clip = ImageClip(image_path, duration=10)
            
            # Exporter la vidéo sans audio
            image_clip.write_videofile(
                video_path,
                fps=24,
                verbose=False,
                logger=None
            )
            
            # Nettoyer
            self._cleanup_clips([image_clip], None, None)
            
            print(f"✅ Vidéo de secours créée: {video_path}")
            return video_path
            
        except Exception as e:
            print(f"❌ Erreur vidéo de secours: {e}")
            return None

# Fonction utilitaire pour usage direct
def create_video(content_data):
    """
    Fonction helper pour créer une vidéo
    """
    creator = VideoCreator()
    return creator.create_professional_video(content_data)

def create_simple_video(content_data):
    """
    Fonction helper pour créer une vidéo simple
    """
    creator = VideoCreator()
    return creator.create_simple_video(content_data)

# Test du module
if __name__ == "__main__":
    print("🧪 Test de VideoCreator...")
    
    test_content = {
        'title': 'Test Vidéo Creator Corrigé',
        'script': 'Ceci est un test de création vidéo avec le système complètement corrigé.',
        'category': 'test',
        'keywords': ['test', 'vidéo
