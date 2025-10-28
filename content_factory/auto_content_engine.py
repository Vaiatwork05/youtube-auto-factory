# content_factory/auto_content_engine.py
import os
import sys
import time
from datetime import datetime
from content_generator import generate_daily_contents, ContentGenerator
from video_creator import VideoCreator
from youtube_uploader import YouTubeUploader
from utils import ensure_directory

def get_current_slot():
    """
    Détermine le créneau actuel basé sur l'heure
    8h = slot 0, 12h = slot 1, 16h = slot 2, 20h = slot 3
    """
    current_hour = datetime.now().hour
    
    if 7 <= current_hour < 11:   # 8h
        return 0
    elif 11 <= current_hour < 15: # 12h  
        return 1
    elif 15 <= current_hour < 19: # 16h
        return 2
    elif 19 <= current_hour <= 23: # 20h
        return 3
    else:
        # Si en dehors des heures programmées, utiliser le premier slot
        return 0

def create_video_for_slot(slot_number):
    """Crée une vidéo pour un créneau spécifique"""
    try:
        print(f"\n🎬 CRÉNEAU {slot_number + 1}/4")
        print("=" * 40)
        
        # Générer le contenu pour ce créneau
        daily_contents = generate_daily_contents()
        content_data = daily_contents[slot_number]
        
        print(f"📝 Titre: {content_data['title']}")
        print(f"📂 Catégorie: {content_data['category']}")
        print(f"🔢 Slot: {content_data['slot_number'] + 1}")
        print(f"🌱 Seed quotidienne: {content_data['daily_seed']}")
        print(f"📄 Script: {content_data['script'][:100]}...")
        
        # Créer la vidéo
        creator = VideoCreator()
        video_path = creator.create_professional_video(content_data)
        
        print(f"✅ Vidéo créée: {video_path}")
        return video_path, content_data
        
    except Exception as e:
        print(f"❌ Erreur créneau {slot_number + 1}: {e}")
        return None, None

def create_all_daily_videos():
    """Crée les 4 vidéos de la journée (pour tests)"""
    successful_videos = []
    
    print("🚀 LANCEMENT DE TOUS LES CRÉNEAUX QUOTIDIENS")
    print("=" * 50)
    
    for slot in range(4):
        video_path, content_data = create_video_for_slot(slot)
        
        if video_path:
            successful_videos.append({
                'path': video_path,
                'title': content_data['title'],
                'slot': slot + 1
            })
        
        # Pause entre les créneaux
        if slot < 3:
            print("\n⏳ Pause avant le prochain créneau...")
            time.sleep(2)
    
    return successful_videos

def main():
    try:
        print("=" * 60)
        print("🎯 YOUTUBE AUTO FACTORY - SYSTÈME QUOTIDIEN 4x")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Vérifications initiales
        print("\n📋 ÉTAPE 1: Vérification des configurations...")
        ensure_directory("output/audio")
        ensure_directory("output/videos")
        ensure_directory("downloaded_images")
        
        print("✅ Tous les dossiers sont prêts!")
        
        # Déterminer le mode d'exécution
        if len(sys.argv) > 1 and sys.argv[1] == "--all":
            # Mode test : créer les 4 vidéos
            successful_videos = create_all_daily_videos()
        else:
            # Mode production : créer seulement la vidéo du créneau actuel
            current_slot = get_current_slot()
            print(f"🕐 Créneau détecté: {current_slot + 1}/4")
            
            video_path, content_data = create_video_for_slot(current_slot)
            successful_videos = [{
                'path': video_path,
                'title': content_data['title'],
                'slot': current_slot + 1
            }] if video_path else []
        
        # Résumé final
        print("\n" + "=" * 50)
        print("📊 RAPPORT DE PRODUCTION")
        print("=" * 50)
        print(f"✅ Vidéos créées avec succès: {len(successful_videos)}")
        
        for video in successful_videos:
            print(f"   🎬 Créneau {video['slot']}: {video['title']}")
        
        if successful_videos:
            print("\n🎉 PROCESSUS TERMINÉ AVEC SUCCÈS!")
            
            # Optionnel : Upload YouTube
            try:
                uploader = YouTubeUploader()
                # uploader.upload_video(successful_videos[0]['path'], content_data)
                print("📤 Vidéo prête pour l'upload (upload désactivé)")
            except Exception as e:
                print(f"⚠️ Upload non effectué: {e}")
                
            return True
        else:
            print("\n❌ Aucune vidéo créée avec succès")
            return False
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
