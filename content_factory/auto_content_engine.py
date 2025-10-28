import os
import sys
from content_generator import ContentGenerator
from video_creator import VideoCreator
from youtube_uploader import YouTubeUploader
from utils import ensure_directory

def main():
    try:
        print("=" * 50)
        print("🚀 DÉMARRAGE YOUTUBE AUTO FACTORY")
        print("=" * 50)
        
        # Étape 1: Vérifications initiales
        print("\n📋 ÉTAPE 1: Vérification des configurations...")
        ensure_directory("output/audio")
        ensure_directory("output/videos")
        ensure_directory("downloaded_images")
        
        # Vérifier les secrets (à adapter selon votre configuration)
        required_secrets = ['OPENAI_API_KEY']  # Ajoutez vos secrets ici
        print("✅ Tous les dossiers sont prêts!")
        
        # Étape 2: Génération du contenu
        print("\n📝 ÉTAPE 2: Génération du script...")
        content_generator = ContentGenerator()
        script_data = content_generator.generate_content()
        
        print(f"🎯 Titre: {script_data.get('title', 'N/A')}")
        print(f"📄 Script: {script_data.get('script', 'N/A')[:100]}...")
        
        # Étape 3: Création de la vidéo
        print("\n🎬 ÉTAPE 3: Création de la vidéo...")
        creator = VideoCreator()
        
        # Utiliser la nouvelle méthode
        video_path = creator.create_professional_video(script_data)
        
        print(f"✅ Vidéo créée: {video_path}")
        
        # Étape 4: Upload YouTube (optionnel)
        print("\n📤 ÉTAPE 4: Upload YouTube...")
        try:
            uploader = YouTubeUploader()
            # uploader.upload_video(video_path, script_data)  # Décommentez pour uploader
            print("✅ Vidéo prête pour l'upload (upload désactivé)")
        except Exception as e:
            print(f"⚠️ Upload non effectué: {e}")
        
        print("\n🎉 PROCESSUS TERMINÉ AVEC SUCCÈS!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
