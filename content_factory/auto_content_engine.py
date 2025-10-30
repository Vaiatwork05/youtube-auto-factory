# content_factory/auto_content_engine.py

import os
import sys
import time
import traceback
import argparse
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional

# Gestion robuste des imports
try:
    # Import relatif (quand exécuté en tant que module)
    from .content_generator import generate_daily_contents
    from .video_creator import VideoCreator
    from .youtube_uploader import YouTubeUploader
    from .utils import ensure_directory
    from .config_loader import ConfigLoader
except ImportError:
    # Import absolu (quand exécuté directement)
    from content_factory.content_generator import generate_daily_contents
    from content_factory.video_creator import VideoCreator
    from content_factory.youtube_uploader import YouTubeUploader
    from content_factory.utils import ensure_directory
    from content_factory.config_loader import ConfigLoader

# ... (le reste du code reste identique)

def main() -> bool:
    """Fonction principale du moteur de contenu."""
    try:
        # --- 0. Arguments & Configuration ---
        args = parse_arguments()
        
        config = ConfigLoader().get_config()
        
        force_run_bool = args.force_run.lower() == 'true'
        mode = "--all" if args.all else "production"
        
        debug_mode = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

        # --- 1. Initialisation ---
        workflow_config = config.get('WORKFLOW', {})
        slot_hours = workflow_config.get('SLOT_HOURS', [8, 12, 16, 20])
        slot_pause_s = workflow_config.get('SLOT_PAUSE_SECONDS', 5)
        
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
        successful_videos = create_and_process_videos(
            mode, slot_hours, slot_pause_s, config, debug_mode, force_run_bool
        )
        
        # 4. Résumé final
        print("\n" + "=" * 50)
        print("📊 RAPPORT FINAL DE PRODUCTION")
        expected = len(slot_hours) if mode == "--all" else 1
        print(f"✅ Vidéos créées avec succès: {len(successful_videos)}/{expected}")
        
        for video in successful_videos:
            print(f"   🎬 Créneau {video['slot']}: {video['title']}")
            
        # 5. Upload
        handle_upload(successful_videos, mode, config)
        
        print("\n🎉 PROCESSUS TERMINÉ.")
        return len(successful_videos) > 0

    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE DANS MAIN: {e}")
        if debug_mode:
            traceback.print_exc(file=sys.stdout)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
