# content_factory/auto_content_engine.py (Orchestrateur Final)

import os
import sys
import time
import traceback
import argparse # (MODIFIÉ) Nouvel import
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional

# Imports relatifs des modules du projet
from .content_generator import generate_daily_contents
from .video_creator import VideoCreator
from .youtube_uploader import YouTubeUploader
from .utils import ensure_directory
from .config_loader import ConfigLoader

# (MODIFIÉ) La variable globale CONFIG est supprimée.

def get_current_slot(slot_hours: List[int]) -> int:
    """
    Détermine le créneau actuel basé sur l'heure.
    """
    current_hour = datetime.now().hour
    
    if current_hour >= slot_hours[-1]:
        return len(slot_hours) - 1
        
    for i, hour in enumerate(slot_hours):
        if current_hour < hour:
            return i - 1 if i > 0 else 0
            
    return 0 

def create_video_for_slot(
    slot_number: int, 
    all_daily_contents: List[Dict[str, Any]], 
    slot_hours: List[int],
    config: Dict[str, Any], # (MODIFIÉ) Injection de la config
    debug_mode: bool        # (MODIFIÉ) Injection du mode debug
) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """Crée une vidéo pour un créneau spécifique à partir des données générées."""
    # (MODIFIÉ) global CONFIG est supprimé
    
    slot_display = slot_number + 1
    
    try:
        if slot_number >= len(all_daily_contents) or slot_number < 0:
            raise IndexError(f"Le créneau {slot_display} est hors limites des contenus générés.")
            
        content_data = all_daily_contents[slot_number]
        
        print(f"\n🎬 CRÉNEAU {slot_display}/{len(slot_hours)} - Heure cible: {slot_hours[slot_number]}h00")
        print("=" * 45)
        
        print(f"📝 Titre: {content_data.get('title', 'N/A')}")
        
        # (MODIFIÉ) On passe la config au constructeur (supposant qu'il l'accepte)
        # Si ce n'est pas le cas, il continuera à lire la globale, mais c'est une meilleure pratique
        creator = VideoCreator(config) 
        video_path = creator.create_professional_video(content_data)
        
        if video_path and os.path.exists(video_path):
            print(f"✅ Vidéo créée: {video_path}")
            return video_path, content_data
        else:
            raise RuntimeError(f"La fonction VideoCreator a échoué pour le créneau {slot_display}.")
        
    except Exception as e:
        print(f"❌ Erreur critique lors de la création pour le créneau {slot_display}: {e}")
        # (MODIFIÉ) Utilise le paramètre debug_mode
        if debug_mode:
            traceback.print_exc(file=sys.stdout)
        return None, None

def create_and_process_videos(
    mode: str, 
    slot_hours: List[int], 
    slot_pause_s: int,
    config: Dict[str, Any], # (MODIFIÉ) Injection de la config
    debug_mode: bool,       # (MODIFIÉ) Injection du mode debug
    force_run: bool         # (MODIFIÉ) Injection du flag force_run
) -> List[Dict[str, Any]]:
    """Gère la création et le traitement des vidéos basés sur le mode (prod ou --all)."""
    successful_videos = []
    
    # 1. Génération de TOUT le contenu pour la journée
    try:
        # (MODIFIÉ) On passe force_run au générateur
        # Il faudra peut-être adapter la signature de generate_daily_contents
        print(f"Génération du contenu (Forcé: {force_run})...")
        all_daily_contents = generate_daily_contents(force_run=force_run) 
        
        if not all_daily_contents or len(all_daily_contents) != len(slot_hours):
            print(f"⚠️ AVERTISSEMENT: Le générateur a produit {len(all_daily_contents)} contenus, mais le moteur attend {len(slot_hours)} créneaux.")
        
        print(f"📋 Contenus journaliers générés ({len(all_daily_contents)} au total).")
    except Exception as e:
        print(f"❌ Échec de la génération des contenus journaliers : {e}")
        return []
        
    slots_to_process = range(len(slot_hours)) if mode == "--all" else [get_current_slot(slot_hours)]
    
    print(f"➡️ Mode d'exécution: {'TOUS LES CRÉNEAUX' if mode == '--all' else f'CRÉNEAU {slots_to_process[0] + 1} (Production)'}")

    for slot in slots_to_process:
        # (MODIFIÉ) On passe la config et le debug_mode
        video_path, content_data = create_video_for_slot(
            slot, all_daily_contents, slot_hours, config, debug_mode
        )
        
        if video_path and content_data:
            successful_videos.append({
                'path': video_path,
                'title': content_data['title'],
                'slot': slot + 1,
                'content_data': content_data
            })
        
        if mode == "--all" and slot < len(slot_hours) - 1:
            print(f"\n⏳ Pause de {slot_pause_s}s avant le prochain créneau...")
            time.sleep(slot_pause_s)
    
    return successful_videos

def handle_upload(successful_videos: List[Dict[str, Any]], mode: str, config: Dict[str, Any]) -> None: # (MODIFIÉ)
    """Gère l'upload YouTube pour les vidéos réussies."""
    if not successful_videos:
        print("📤 Aucune vidéo à uploader.")
        return

    video_to_upload = successful_videos[0] if mode == "--all" else successful_videos[-1]
    
    print("\n📦 ÉTAPE FINALE: Tentative d'Upload YouTube...")
    try:
        # (MODIFIÉ) On passe la config au constructeur
        uploader = YouTubeUploader(config) 
        uploader.upload_video(video_to_upload['path'], video_to_upload['content_data'])
        print("✅ Upload terminé avec succès.")
    except ImportError:
        print("⚠️ Upload désactivé ou dépendance YouTube non trouvée.")
    except Exception as e:
        print(f"❌ Échec critique de l'Upload : {e}")

# (MODIFIÉ) Fonction pour gérer argparse
def parse_arguments() -> argparse.Namespace:
    """Parse les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(description="YouTube Auto Factory Engine")
    parser.add_argument(
        '--all',
        action='store_true',
        help="Forcer la génération et le traitement de TOUS les créneaux."
    )
    parser.add_argument(
        '--force-run',
        type=str,
        default='false',
        choices=['true', 'false'], # S'assure que seules ces valeurs sont acceptées
        help="Argument de CI/CD pour forcer l'exécution (ex: régénération de contenu)."
    )
    return parser.parse_args()

def main() -> bool:
    """Fonction principale du moteur de contenu."""
    # (MODIFIÉ) La variable globale n'est plus utilisée
    
    try:
        # --- 0. Arguments & Configuration ---
        args = parse_arguments()
        
        config = ConfigLoader().get_config()
        
        # (MODIFIÉ) Logique des modes gérée par argparse
        force_run_bool = args.force_run.lower() == 'true'
        mode = "--all" if args.all else "production"
        
        # Le mode DEBUG est lu une seule fois ici
        debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

        # --- 1. Initialisation ---
        slot_hours = config.get('WORKFLOW', {}).get('SLOT_HOURS', [8, 12, 16, 20])
        slot_pause_s = config.get('WORKFLOW', {}).get('SLOT_PAUSE_SECONDS', 5)
        
        print("=" * 60)
        print("🎯 YOUTUBE AUTO FACTORY - SYSTÈME QUOTIDIEN")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🐛 Mode DEBUG: {debug_mode}")
        print(f"🏃 Mode d'exécution: {mode.upper()}")
        print(f"🔄 Forcer l'exécution (force_run): {force_run_bool}")
        print(f"⏱️ Créneaux définis: {slot_hours}")
        
        # 2. Vérifications initiales
        print("\n📋 ÉTAPE 2: Vérification des dossiers de sortie...")
        
        output_root = config['PATHS']['OUTPUT_ROOT']
        ensure_directory(output_root)
        ensure_directory(os.path.join(output_root, config['PATHS']['AUDIO_DIR']))
        ensure_directory(os.path.join(output_root, config['PATHS']['VIDEO_DIR']))
        ensure_directory(os.path.join(output_root, config['PATHS']['IMAGE_DIR']))
        print("✅ Tous les dossiers sont prêts.")

        # 3. Création et traitement des vidéos
        # (MODIFIÉ) On passe les arguments et la config
        successful_videos = create_and_process_videos(
            mode, slot_hours, slot_pause_s, config, debug_mode, force_run_bool
        )
        
        # 4. Résumé final
        print("\n" + "=" * 50)
        print("📊 RAPPORT FINAL DE PRODUCTION")
        print(f"✅ Vidéos créées avec succès: {len(successful_videos)}/{len(slot_hours) if mode == '--all' else 1}")
        
        for video in successful_videos:
            print(f"   🎬 Créneau {video['slot']}: {video['title']}")
            
        # 5. Upload
        handle_upload(successful_videos, mode, config) # (MODIFIÉ)
        
        print("\n🎉 PROCESSUS TERMINÉ.")
        return len(successful_videos) > 0

    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE DANS MAIN: {e}")
        # (MODIFIÉ) On utilise la variable debug_mode lue au début
        if debug_mode:
            traceback.print_exc(file=sys.stdout)
        return False

if __name__ == "__main__":
    try:
        from content_factory.config_loader import ConfigLoader
    except ImportError:
        print("❌ ERREUR D'IMPORTATION: Veuillez lancer le script depuis le dossier racine du projet.")
        print(f"Ex: python3 -m content_factory.auto_content_engine")
        sys.exit(1)
        
    success = main()
    sys.exit(0 if success else 1)
