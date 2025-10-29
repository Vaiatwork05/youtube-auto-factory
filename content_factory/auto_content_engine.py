# content_factory/auto_content_engine.py
import os
import sys
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple, List, Optional

# Imports des modules du projet (Assurez-vous que les imports sont précis)
from content_generator import generate_daily_contents, ContentGenerator
from video_creator import VideoCreator
from youtube_uploader import YouTubeUploader
from utils import ensure_directory

# --- CONSTANTES ---
# Utilisation de la variable d'environnement DEBUG_MODE définie dans le workflow YAML
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
SLOT_HOURS = [8, 12, 16, 20] # Créneaux de déclenchement (heures)
SLOT_PAUSE_SECONDS = 5 # Pause réduite entre les créneaux en mode --all

def get_current_slot() -> int:
    """
    Détermine le créneau actuel basé sur l'heure.
    8h=0, 12h=1, 16h=2, 20h=3.
    """
    current_hour = datetime.now().hour
    
    # Trouver le créneau le plus proche et passé, ou le premier par défaut
    for i, hour in enumerate(SLOT_HOURS):
        if current_hour < hour:
            # Si l'heure actuelle est avant le prochain créneau, on reste sur le précédent
            # Mais si on est tôt le matin (avant 8h), on prend 8h (slot 0)
            return i - 1 if i > 0 else 0
        
    # Si l'heure est après le dernier créneau (20h), on utilise le dernier (slot 3)
    return len(SLOT_HOURS) - 1

def create_video_for_slot(slot_number: int, all_daily_contents: List[Dict[str, Any]]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Crée une vidéo pour un créneau spécifique à partir des données générées."""
    slot_display = slot_number + 1
    
    try:
        if slot_number >= len(all_daily_contents) or slot_number < 0:
            raise IndexError(f"Le créneau {slot_display} est hors limites des contenus générés.")
            
        content_data = all_daily_contents[slot_number]
        
        print(f"\n🎬 CRÉNEAU {slot_display}/{len(SLOT_HOURS)}")
        print("=" * 40)
        
        # Affichage des métadonnées
        print(f"📝 Titre: {content_data.get('title', 'N/A')}")
        print(f"📄 Script (début): {content_data.get('script', 'N/A')[:100]}...")
        
        # Créer la vidéo
        creator = VideoCreator()
        video_path = creator.create_professional_video(content_data)
        
        if video_path and os.path.exists(video_path):
            print(f"✅ Vidéo créée: {video_path}")
            return video_path, content_data
        else:
            raise RuntimeError(f"La fonction VideoCreator a échoué pour le créneau {slot_display}.")
        
    except Exception as e:
        print(f"❌ Erreur critique lors de la création pour le créneau {slot_display}: {e}")
        if DEBUG_MODE:
            traceback.print_exc(file=sys.stdout)
        return None, None

def create_and_process_videos(mode: str) -> List[Dict[str, Any]]:
    """Gère la création et le traitement des vidéos basés sur le mode (prod ou --all)."""
    successful_videos = []
    
    # 1. Génération de TOUT le contenu pour la journée (réalisée une seule fois)
    try:
        all_daily_contents = generate_daily_contents()
        if not all_daily_contents or len(all_daily_contents) != len(SLOT_HOURS):
            raise ValueError(f"Le générateur a retourné {len(all_daily_contents)} contenus au lieu de {len(SLOT_HOURS)}.")
        print(f"📋 Contenus journaliers générés ({len(all_daily_contents)} au total).")
    except Exception as e:
        print(f"❌ Échec de la génération des contenus journaliers : {e}")
        if DEBUG_MODE:
             traceback.print_exc(file=sys.stdout)
        return [] # Retourne une liste vide en cas d'échec
        
    slots_to_process = range(len(SLOT_HOURS)) if mode == "--all" else [get_current_slot()]
    
    print(f"➡️ Mode d'exécution: {'TOUS LES CRÉNEAUX' if mode == '--all' else f'CRÉNEAU {slots_to_process[0] + 1} (Production)'}")

    for slot in slots_to_process:
        video_path, content_data = create_video_for_slot(slot, all_daily_contents)
        
        if video_path and content_data:
            successful_videos.append({
                'path': video_path,
                'title': content_data['title'],
                'slot': slot + 1,
                'content_data': content_data # Ajouter les données complètes pour l'uploader
            })
        
        # Pause entre les créneaux uniquement en mode --all
        if mode == "--all" and slot < len(SLOT_HOURS) - 1:
            print(f"\n⏳ Pause de {SLOT_PAUSE_SECONDS}s avant le prochain créneau...")
            time.sleep(SLOT_PAUSE_SECONDS)
    
    return successful_videos

def handle_upload(successful_videos: List[Dict[str, Any]]) -> None:
    """Gère l'upload YouTube pour les vidéos réussies."""
    if not successful_videos:
        print("📤 Aucune vidéo à uploader.")
        return

    # En mode production, on uploade idéalement la dernière vidéo créée (celle du créneau actuel)
    video_to_upload = successful_videos[-1]
    
    print("\n📦 ÉTAPE FINALE: Tentative d'Upload YouTube...")
    try:
        uploader = YouTubeUploader()
        # On utilise les données complètes (content_data) pour le titre, description, tags, etc.
        uploader.upload_video(video_to_upload['path'], video_to_upload['content_data'])
        print("✅ Upload terminé avec succès.")
    except ImportError:
        # Géré par un fichier désactivateur ou une absence de dépendance
        print("⚠️ Upload désactivé ou dépendance YouTube non trouvée (YouTubeUploader).")
    except Exception as e:
        print(f"❌ Échec critique de l'Upload : {e}")
        if DEBUG_MODE:
            traceback.print_exc(file=sys.stdout)

def main() -> bool:
    """Fonction principale du moteur de contenu."""
    
    # Détecter le mode d'exécution: --all pour test/démo, sinon production
    mode = "--all" if len(sys.argv) > 1 and sys.argv[1] == "--all" else "production"

    try:
        print("=" * 60)
        print("🎯 YOUTUBE AUTO FACTORY - SYSTÈME QUOTIDIEN")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🐛 Mode DEBUG: {DEBUG_MODE}")
        
        # 1. Vérifications initiales (centralisées)
        print("\n📋 ÉTAPE 1: Vérification des configurations...")
        # Assurez-vous que 'utils' est bien défini pour gérer ces chemins
        ensure_directory("output/audio")
        ensure_directory("output/videos")
        ensure_directory("downloaded_images")
        print("✅ Tous les dossiers sont prêts.")

        # 2. Création et traitement des vidéos
        successful_videos = create_and_process_videos(mode)
        
        # 3. Résumé final
        print("\n" + "=" * 50)
        print("📊 RAPPORT FINAL DE PRODUCTION")
        print(f"✅ Vidéos créées avec succès: {len(successful_videos)}/{len(SLOT_HOURS) if mode == '--all' else 1}")
        
        for video in successful_videos:
            print(f"   🎬 Créneau {video['slot']}: {video['title']}")
            
        # 4. Upload
        handle_upload(successful_videos)
        
        print("\n🎉 PROCESSUS TERMINÉ.")
        return len(successful_videos) > 0 # Retourne True si au moins une vidéo a été créée

    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE DANS MAIN: {e}")
        if DEBUG_MODE:
            traceback.print_exc(file=sys.stdout)
        return False

if __name__ == "__main__":
    success = main()
    # Le code YAML s'appuie sur le code de retour 0 pour le succès
    sys.exit(0 if success else 1)
