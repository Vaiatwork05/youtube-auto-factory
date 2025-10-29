# content_factory/auto_content_engine.py (Orchestrateur Final)

import os
import sys
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional

# Imports relatifs des modules du projet
from .content_generator import generate_daily_contents
from .video_creator import VideoCreator
from .youtube_uploader import YouTubeUploader
from .utils import ensure_directory
from .config_loader import ConfigLoader # NOUVEL IMPORT

# Déclaration d'une variable globale pour la configuration (initialisée dans main)
CONFIG: Optional[Dict[str, Any]] = None

def get_current_slot(slot_hours: List[int]) -> int:
    """
    Détermine le créneau actuel basé sur l'heure.
    8h=0, 12h=1, 16h=2, 20h=3.
    """
    current_hour = datetime.now().hour
    
    # Si l'heure est après le dernier créneau, on utilise le dernier (ex: 20:30 -> slot 3)
    if current_hour >= slot_hours[-1]:
        return len(slot_hours) - 1
        
    # Trouver le créneau le plus proche et passé
    for i, hour in enumerate(slot_hours):
        if current_hour < hour:
            # Si on est avant le premier créneau (8h), on prend le premier (slot 0)
            return i - 1 if i > 0 else 0
            
    # Devrait être couvert par la première condition, mais assure la sécurité
    return 0 

def create_video_for_slot(slot_number: int, all_daily_contents: List[Dict[str, Any]], slot_hours: List[int]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Crée une vidéo pour un créneau spécifique à partir des données générées."""
    global CONFIG
    # Utiliser le mode DEBUG depuis la config (qui est un simple os.getenv, ici on simule)
    debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    
    slot_display = slot_number + 1
    
    try:
        if slot_number >= len(all_daily_contents) or slot_number < 0:
            raise IndexError(f"Le créneau {slot_display} est hors limites des contenus générés.")
            
        content_data = all_daily_contents[slot_number]
        
        print(f"\n🎬 CRÉNEAU {slot_display}/{len(slot_hours)} - Heure cible: {slot_hours[slot_number]}h00")
        print("=" * 45)
        
        # Affichage des métadonnées
        print(f"📝 Titre: {content_data.get('title', 'N/A')}")
        
        # Créer la vidéo
        creator = VideoCreator() # Initialisation utilise la config
        video_path = creator.create_professional_video(content_data)
        
        if video_path and os.path.exists(video_path):
            print(f"✅ Vidéo créée: {video_path}")
            return video_path, content_data
        else:
            raise RuntimeError(f"La fonction VideoCreator a échoué pour le créneau {slot_display}.")
        
    except Exception as e:
        print(f"❌ Erreur critique lors de la création pour le créneau {slot_display}: {e}")
        if debug_mode:
            traceback.print_exc(file=sys.stdout)
        return None, None

def create_and_process_videos(mode: str, slot_hours: List[int], slot_pause_s: int) -> List[Dict[str, Any]]:
    """Gère la création et le traitement des vidéos basés sur le mode (prod ou --all)."""
    successful_videos = []
    
    # 1. Génération de TOUT le contenu pour la journée
    try:
        all_daily_contents = generate_daily_contents() # Utilise le nombre de slots du config.yaml
        
        # Vérification basée sur le nombre de créneaux défini dans le moteur (SLOT_HOURS)
        if not all_daily_contents or len(all_daily_contents) != len(slot_hours):
            print(f"⚠️ AVERTISSEMENT: Le générateur a produit {len(all_daily_contents)} contenus, mais le moteur attend {len(slot_hours)} créneaux.")
        
        print(f"📋 Contenus journaliers générés ({len(all_daily_contents)} au total).")
    except Exception as e:
        print(f"❌ Échec de la génération des contenus journaliers : {e}")
        return []
        
    slots_to_process = range(len(slot_hours)) if mode == "--all" else [get_current_slot(slot_hours)]
    
    print(f"➡️ Mode d'exécution: {'TOUS LES CRÉNEAUX' if mode == '--all' else f'CRÉNEAU {slots_to_process[0] + 1} (Production)'}")

    for slot in slots_to_process:
        video_path, content_data = create_video_for_slot(slot, all_daily_contents, slot_hours)
        
        if video_path and content_data:
            successful_videos.append({
                'path': video_path,
                'title': content_data['title'],
                'slot': slot + 1,
                'content_data': content_data
            })
        
        # Pause entre les créneaux uniquement en mode --all
        if mode == "--all" and slot < len(slot_hours) - 1:
            print(f"\n⏳ Pause de {slot_pause_s}s avant le prochain créneau...")
            time.sleep(slot_pause_s)
    
    return successful_videos

def handle_upload(successful_videos: List[Dict[str, Any]], mode: str) -> None:
    """Gère l'upload YouTube pour les vidéos réussies."""
    if not successful_videos:
        print("📤 Aucune vidéo à uploader.")
        return

    # En mode --all (test/démo), on uploade idéalement la première vidéo créée.
    # En mode production, on uploade la vidéo qui vient d'être créée (la dernière de la liste).
    video_to_upload = successful_videos[0] if mode == "--all" else successful_videos[-1]
    
    print("\n📦 ÉTAPE FINALE: Tentative d'Upload YouTube...")
    try:
        uploader = YouTubeUploader() # Initialisation utilise la config pour les secrets
        # On utilise les données complètes (content_data) pour le titre, description, tags, etc.
        uploader.upload_video(video_to_upload['path'], video_to_upload['content_data'])
        print("✅ Upload terminé avec succès.")
    except ImportError:
        print("⚠️ Upload désactivé ou dépendance YouTube non trouvée.")
    except Exception as e:
        print(f"❌ Échec critique de l'Upload : {e}")
        # Le mode DEBUG est géré par la classe Uploader elle-même, mais on le rappelle ici pour la clarté.


def main() -> bool:
    """Fonction principale du moteur de contenu."""
    global CONFIG
    
    try:
        # --- 1. CHARGEMENT DE LA CONFIGURATION ET DES CONSTANTES ---
        CONFIG = ConfigLoader().get_config()
        
        # Assurez-vous que les constantes proviennent de la configuration
        slot_hours = CONFIG.get('WORKFLOW', {}).get('SLOT_HOURS', [8, 12, 16, 20])
        slot_pause_s = CONFIG.get('WORKFLOW', {}).get('SLOT_PAUSE_SECONDS', 5)
        
        # Le mode DEBUG est laissé en variable d'environnement pour le workflow YAML, mais on peut le lire ici
        debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

        # Détecter le mode d'exécution
        mode = "--all" if len(sys.argv) > 1 and sys.argv[1] == "--all" else "production"

        print("=" * 60)
        print("🎯 YOUTUBE AUTO FACTORY - SYSTÈME QUOTIDIEN")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🐛 Mode DEBUG: {debug_mode}")
        print(f"⏱️ Créneaux définis: {slot_hours}")
        
        # 2. Vérifications initiales (centralisées)
        print("\n📋 ÉTAPE 2: Vérification des dossiers de sortie...")
        
        output_root = CONFIG['PATHS']['OUTPUT_ROOT']
        audio_dir = CONFIG['PATHS']['AUDIO_DIR']
        video_dir = CONFIG['PATHS']['VIDEO_DIR']
        image_dir = CONFIG['PATHS']['IMAGE_DIR']

        ensure_directory(output_root)
        ensure_directory(os.path.join(output_root, audio_dir))
        ensure_directory(os.path.join(output_root, video_dir))
        ensure_directory(os.path.join(output_root, image_dir))
        print("✅ Tous les dossiers sont prêts.")

        # 3. Création et traitement des vidéos
        successful_videos = create_and_process_videos(mode, slot_hours, slot_pause_s)
        
        # 4. Résumé final
        print("\n" + "=" * 50)
        print("📊 RAPPORT FINAL DE PRODUCTION")
        print(f"✅ Vidéos créées avec succès: {len(successful_videos)}/{len(slot_hours) if mode == '--all' else 1}")
        
        for video in successful_videos:
            print(f"   🎬 Créneau {video['slot']}: {video['title']}")
            
        # 5. Upload
        handle_upload(successful_videos, mode)
        
        print("\n🎉 PROCESSUS TERMINÉ.")
        return len(successful_videos) > 0

    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE DANS MAIN: {e}")
        if debug_mode:
            traceback.print_exc(file=sys.stdout)
        return False

if __name__ == "__main__":
    # Correction: Mettez les SLOT_HOURS dans config.yaml ou laissez-les en dur pour l'exécution initiale
    # Pour l'exécution en Python pur, il faut s'assurer que les imports relatifs fonctionnent (lancement depuis le dossier parent)
    
    # Pour le test, on ajoute une vérification simple des imports relatifs dans le bloc d'exécution :
    try:
        from content_factory.config_loader import ConfigLoader
    except ImportError:
        print("❌ ERREUR D'IMPORTATION: Veuillez lancer le script depuis le dossier racine du projet (pas depuis content_factory).")
        print(f"Ex: python3 content_factory/auto_content_engine.py")
        sys.exit(1)
        
    success = main()
    # Le code de retour 0 pour le succès est la norme pour les workflows CI/CD
    sys.exit(0 if success else 1)
