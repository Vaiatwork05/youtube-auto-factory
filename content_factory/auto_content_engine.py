import traceback
import sys
import os
from content_generator import ContentGenerator
from video_creator import VideoCreator
from youtube_uploader import YouTubeUploader

print("🔧 ÉTAPE 1: Démarrage YouTube Auto Factory...")

try:
    # ÉTAPE 2: Vérification des configurations
    print("🔧 ÉTAPE 2: Vérification des configurations...")
    
    # Vérification des secrets
    required_secrets = ['YOUTUBE_CLIENT_SECRET_1', 'YOUTUBE_REFRESH_TOKEN_1', 'YOUTUBE_CHANNEL_ID_1']
    for secret in required_secrets:
        if secret not in os.environ:
            raise Exception(f"Secret manquant: {secret}")
    
    print("✅ Tous les secrets sont configurés !")
    
    # ÉTAPE 3: Génération du script
    print("🔧 ÉTAPE 3: Génération du script...")
    generator = ContentGenerator()
    script_data = generator.generate_script()
    print(f"📝 Titre: {script_data['title']}")
    print(f"📝 Script: {script_data['script'][:100]}...")
    
    # ÉTAPE 4: Création de la vidéo
    print("🔧 ÉTAPE 4: Création de la vidéo...")
    creator = VideoCreator()
    video_path = creator.create_video(script_data)
    print(f"🎥 Vidéo créée: {video_path}")
    
    # ÉTAPE 5: Upload YouTube
    print("🔧 ÉTAPE 5: Upload vers YouTube...")
    uploader = YouTubeUploader(
        client_secret=os.environ['YOUTUBE_CLIENT_SECRET_1'],
        refresh_token=os.environ['YOUTUBE_REFRESH_TOKEN_1'], 
        channel_id=os.environ['YOUTUBE_CHANNEL_ID_1']
    )
    
    video_id = uploader.upload_video(
        video_path=video_path,
        title=script_data["title"],
        description=script_data["description"],
        tags=script_data["tags"]
    )
    
    print(f"✅ SUCCÈS: Vidéo uploadée! ID: {video_id}")
    
except Exception as e:
    print(f"🚨 ERREUR: {str(e)}")
    print(f"📋 STACKTRACE: {traceback.format_exc()}")
    sys.exit(1)
