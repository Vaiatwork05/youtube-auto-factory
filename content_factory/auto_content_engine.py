# auto_content_engine.py (VERSION AVEC LOGS STRATÉGIQUES)

#!/usr/bin/env python3
"""
YouTube Auto Factory - Orchestrateur Principal
Version avec logging étendu pour le debug
"""

import os
import sys
import time
import traceback
import argparse
from datetime import datetime
from typing import Dict, Any, Tuple, List, Optional

# =============================================================================
# GESTION ROBUSTE DES IMPORTS
# =============================================================================

def setup_imports():
    """Configure les chemins d'import."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    if script_dir not in sys.path:
        sys.path.insert(0, script_dir)

setup_imports()

try:
    from content_factory.content_generator import generate_daily_contents
    from content_factory.video_creator import VideoCreator
    from content_factory.youtube_uploader import YouTubeUploader
    from content_factory.utils import ensure_directory
    from content_factory.config_loader import ConfigLoader
    IMPORT_SUCCESS = True
    print("✅ IMPORTS RÉUSSIS - Tous les modules chargés")
except ImportError as e:
    print(f"❌ ERREUR CRITIQUE - Import impossible: {e}")
    IMPORT_SUCCESS = False

# =============================================================================
# FONCTIONS PRINCIPALES AVEC LOGGING ÉTENDU
# =============================================================================

def get_current_slot(slot_hours: List[int]) -> int:
    """Détermine le créneau actuel."""
    current_hour = datetime.now().hour
    print(f"🕐 Heure actuelle: {current_hour}h")
    
    if current_hour >= slot_hours[-1]:
        slot = len(slot_hours) - 1
        print(f"🎯 Créneau sélectionné: {slot + 1} (dernier de la journée)")
        return slot
    
    for i, hour in enumerate(slot_hours):
        if current_hour < hour:
            slot = i - 1 if i > 0 else 0
            print(f"🎯 Créneau sélectionné: {slot + 1}")
            return slot
    
    print(f"🎯 Créneau sélectionné: 1 (par défaut)")
    return 0

def create_video_for_slot(
    slot_number: int, 
    all_daily_contents: List[Dict[str, Any]], 
    slot_hours: List[int],
    config: Dict[str, Any],
    debug_mode: bool = False
) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
    """
    Crée une vidéo pour un créneau spécifique.
    Version avec logging étendu pour identifier les blocages.
    """
    slot_display = slot_number + 1
    target_hour = slot_hours[slot_number]
    
    print(f"\n🎬 DÉBUT CRÉNEAU {slot_display}/{len(slot_hours)}")
    print(f"   Heure cible: {target_hour:02d}h00")
    print("=" * 50)
    
    try:
        # 🔍 LOG 1: Validation des données d'entrée
        print(f"🔍 [SLOT-{slot_display}] Validation des données...")
        
        if slot_number >= len(all_daily_contents):
            raise IndexError(f"Aucun contenu généré pour le créneau {slot_display}")
        
        if slot_number < 0:
            raise ValueError(f"Numéro de créneau invalide: {slot_number}")
        
        content_data = all_daily_contents[slot_number]
        print(f"✅ [SLOT-{slot_display}] Données récupérées - Clés: {list(content_data.keys())}")
        
        if not content_data or 'title' not in content_data:
            raise ValueError(f"Données de contenu invalides pour le créneau {slot_display}")
        
        print(f"📝 [SLOT-{slot_display}] Titre: {content_data['title']}")
        print(f"📊 [SLOT-{slot_display}] Type: {content_data.get('content_type', 'N/A')}")
        print(f"🎯 [SLOT-{slot_display}] Thème: {content_data.get('category', 'N/A')}")
        print(f"🔑 [SLOT-{slot_display}] Mots-clés: {', '.join(content_data.get('keywords', [])[:3])}")
        
        # 🔍 LOG 2: Initialisation VideoCreator
        print(f"🔧 [SLOT-{slot_display}] Initialisation VideoCreator...")
        creator = VideoCreator()
        print(f"✅ [SLOT-{slot_display}] VideoCreator initialisé")
        
        # 🔍 LOG 3: Appel à la création vidéo (POINT CRITIQUE)
        print(f"🚀 [SLOT-{slot_display}] Appel create_professional_video()...")
        print(f"📦 [SLOT-{slot_display}] Données envoyées:")
        print(f"   - Title: {content_data.get('title', 'N/A')}")
        print(f"   - Script length: {len(content_data.get('script', ''))} caractères")
        print(f"   - Keywords: {len(content_data.get('keywords', []))} mots-clés")
        
        start_time = time.time()
        video_path = creator.create_video(content_data)
        creation_time = time.time() - start_time
        
        print(f"⏱️ [SLOT-{slot_display}] Temps de création: {creation_time:.1f}s")
        print(f"📤 [SLOT-{slot_display}] Résultat video_creator: {video_path}")
        
        # 🔍 LOG 4: Validation du résultat
        if not video_path:
            print(f"❌ [SLOT-{slot_display}] ERREUR: video_path est None/empty")
            raise RuntimeError("Aucun chemin vidéo retourné")
        
        print(f"🔍 [SLOT-{slot_display}] Vérification existence fichier...")
        if not os.path.exists(video_path):
            print(f"❌ [SLOT-{slot_display}] Fichier non trouvé: {video_path}")
            print(f"🔍 [SLOT-{slot_display}] Répertoire parent: {os.path.dirname(video_path)}")
            print(f"🔍 [SLOT-{slot_display}] Contenu du répertoire:")
            try:
                if os.path.exists(os.path.dirname(video_path)):
                    files = os.listdir(os.path.dirname(video_path))
                    for f in files[:10]:  # Premier 10 fichiers
                        print(f"   - {f}")
            except Exception as dir_error:
                print(f"   ⚠️ Impossible de lister: {dir_error}")
            
            raise FileNotFoundError(f"Fichier vidéo non trouvé: {video_path}")
        
        # 🔍 LOG 5: Succès avec détails
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # Taille en MB
        print(f"✅ [SLOT-{slot_display}] VIDÉO CRÉÉE AVEC SUCCÈS")
        print(f"   📁 Chemin: {video_path}")
        print(f"   📏 Taille: {file_size:.2f} MB")
        print(f"   🕐 Création: {datetime.now().strftime('%H:%M:%S')}")
        
        return video_path, content_data
        
    except Exception as e:
        print(f"❌ [SLOT-{slot_display}] ERREUR CRITIQUE: {e}")
        if debug_mode:
            print(f"🔍 [SLOT-{slot_display}] Debug - Traceback complet:")
            traceback.print_exc()
        return None, None

def create_and_process_videos(
    mode: str,
    slot_hours: List[int], 
    slot_pause_s: int,
    config: Dict[str, Any],
    debug_mode: bool = False,
    force_run: bool = False
) -> List[Dict[str, Any]]:
    """
    Orchestre la création et le traitement des vidéos.
    Version avec logging étendu.
    """
    successful_videos = []
    
    print("\n" + "=" * 60)
    print("📦 PHASE 1: GÉNÉRATION DU CONTENU QUOTIDIEN")
    print("=" * 60)
    
    # 1. Génération du contenu
    try:
        print(f"🔄 Génération des contenus en cours...")
        start_time = time.time()
        all_daily_contents = generate_daily_contents()
        gen_time = time.time() - start_time
        
        if not all_daily_contents:
            raise RuntimeError("Aucun contenu généré")
        
        expected_slots = len(slot_hours)
        actual_slots = len(all_daily_contents)
        
        print(f"✅ Génération terminée en {gen_time:.1f}s")
        print(f"📊 Résultat: {actual_slots} contenus générés sur {expected_slots} attendus")
        
        # 🔍 LOG: Détail des contenus générés
        for i, content in enumerate(all_daily_contents):
            print(f"   {i+1}. {content.get('title', 'Sans titre')}")
        
        if actual_slots != expected_slots:
            print(f"⚠️  Écart détecté: {actual_slots} contenus vs {expected_slots} créneaux")
            
    except Exception as e:
        print(f"❌ ÉCHEC - Génération du contenu: {e}")
        if debug_mode:
            print("🔍 Stack trace génération:")
            traceback.print_exc()
        return []
    
    # 2. Détermination des créneaux à traiter
    print(f"\n🎯 PHASE 2: PLANIFICATION DES CRÉNEAUX")
    print("-" * 40)
    
    if mode == "all":
        slots_to_process = list(range(len(slot_hours)))
        print(f"🔧 Mode: TOUS LES CRÉNEAUX ({len(slots_to_process)} créneaux)")
    else:
        current_slot = get_current_slot(slot_hours)
        slots_to_process = [current_slot]
        print(f"🔧 Mode: PRODUCTION (créneau {current_slot + 1})")
    
    # 3. Traitement des créneaux
    print(f"\n🎬 PHASE 3: CRÉATION DES VIDÉOS")
    print("-" * 40)
    
    total_slots = len(slots_to_process)
    print(f"📋 Total des créneaux à traiter: {total_slots}")
    
    for i, slot in enumerate(slots_to_process, 1):
        print(f"\n🔧 TRAITEMENT {i}/{total_slots} - Créneau {slot + 1}")
        print("-" * 30)
        
        video_path, content_data = create_video_for_slot(
            slot, all_daily_contents, slot_hours, config, debug_mode
        )
        
        if video_path and content_data:
            successful_videos.append({
                'path': video_path,
                'title': content_data['title'],
                'slot': slot + 1,
                'content_data': content_data,
                'created_at': datetime.now().isoformat()
            })
            print(f"🎉 Créneau {slot + 1} - SUCCÈS COMPLET")
        else:
            print(f"💥 Créneau {slot + 1} - ÉCHEC CRITIQUE")
        
        # Pause entre les créneaux (sauf pour le dernier)
        if mode == "all" and i < total_slots:
            print(f"\n⏳ Pause de {slot_pause_s} secondes...")
            time.sleep(slot_pause_s)
    
    print(f"\n📊 BILAN CRÉATION: {len(successful_videos)}/{total_slots} vidéos créées")
    return successful_videos

def handle_upload(
    successful_videos: List[Dict[str, Any]], 
    mode: str, 
    config: Dict[str, Any]
) -> bool:
    """Gère l'upload YouTube des vidéos."""
    print(f"\n📤 PHASE 4: UPLOAD YOUTUBE")
    print("-" * 40)
    
    if not successful_videos:
        print("📭 Aucune vidéo à uploader")
        return False
    
    print(f"📦 Vidéos disponibles: {len(successful_videos)}")
    
    # Sélection de la vidéo à uploader
    if mode == "all":
        video_to_upload = successful_videos[0]
        print(f"📤 Upload de la première vidéo (créneau {video_to_upload['slot']})")
    else:
        video_to_upload = successful_videos[-1]
        print(f"📤 Upload de la vidéo du créneau {video_to_upload['slot']}")
    
    print(f"🎬 Titre: {video_to_upload['title']}")
    print(f"📁 Fichier: {video_to_upload['path']}")
    print(f"📏 Taille: {os.path.getsize(video_to_upload['path']) / (1024 * 1024):.1f} MB")
    
    try:
        print("🔧 Initialisation YouTubeUploader...")
        uploader = YouTubeUploader()
        print("🚀 Début upload...")
        
        result = uploader.upload_video(
            video_to_upload['path'], 
            video_to_upload['content_data']
        )
        
        if result:
            print("✅ Upload YouTube - SUCCÈS")
            return True
        else:
            print("⚠️ Upload YouTube - ÉCHEC ou DÉSACTIVÉ")
            return False
            
    except Exception as e:
        print(f"❌ ERREUR - Upload YouTube: {e}")
        if debug_mode:
            traceback.print_exc()
        return False

def setup_directories(config: Dict[str, Any]) -> bool:
    """Crée et vérifie les répertoires nécessaires."""
    print("\n📁 CONFIGURATION DES RÉPERTOIRES")
    print("-" * 40)
    
    try:
        paths_config = config.get('PATHS', {})
        output_root = paths_config.get('OUTPUT_ROOT', 'output')
        
        directories = [
            output_root,
            os.path.join(output_root, paths_config.get('AUDIO_DIR', 'audio')),
            os.path.join(output_root, paths_config.get('VIDEO_DIR', 'videos')),
            os.path.join(output_root, paths_config.get('IMAGE_DIR', 'images')),
            os.path.join(output_root, paths_config.get('LOG_DIR', 'logs')),
            "assets/music"
        ]
        
        success_count = 0
        for directory in directories:
            success = ensure_directory(directory)
            if success:
                print(f"✅ {directory}")
                success_count += 1
            else:
                print(f"❌ {directory}")
        
        print(f"🎯 Répertoires configurés: {success_count}/{len(directories)}")
        return success_count == len(directories)
        
    except Exception as e:
        print(f"❌ ERREUR - Configuration des répertoires: {e}")
        return False

def parse_arguments() -> argparse.Namespace:
    """Parse les arguments de ligne de commande."""
    parser = argparse.ArgumentParser(
        description="YouTube Auto Factory - Système de génération automatique de contenu"
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help="Traiter TOUS les créneaux de la journée"
    )
    
    parser.add_argument(
        '--force-run',
        type=str,
        choices=['true', 'false'],
        default='false',
        help="Forcer la régénération du contenu (true/false)"
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help="Activer le mode debug (logs détaillés)"
    )
    
    return parser.parse_args()

def main() -> bool:
    """Fonction principale du moteur de contenu."""
    
    if not IMPORT_SUCCESS:
        print("❌ Impossible de démarrer - Erreur d'import des modules")
        return False
    
    try:
        # INITIALISATION
        print("🔧 PHASE 0: INITIALISATION")
        print("-" * 40)
        
        args = parse_arguments()
        config = ConfigLoader().get_config()
        
        force_run = args.force_run.lower() == 'true'
        debug_mode = args.debug or os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        mode = "all" if args.all else "production"
        
        workflow_config = config.get('WORKFLOW', {})
        slot_hours = workflow_config.get('SLOT_HOURS', [8, 12, 16, 20])
        slot_pause = workflow_config.get('SLOT_PAUSE_SECONDS', 10)
        
        # DÉMARRAGE
        print("\n" + "=" * 70)
        print("🎯 YOUTUBE AUTO FACTORY - MOTEUR DE PRODUCTION")
        print("=" * 70)
        print(f"📅 Lancement: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Mode: {mode.upper()}")
        print(f"🐛 Debug: {debug_mode}")
        print(f"🔄 Force run: {force_run}")
        print(f"⏰ Créneaux: {slot_hours}")
        print(f"⏱️ Pause: {slot_pause}s")
        print(f"🎵 Musique: {'✅ ACTIVÉE' if os.getenv('BACKGROUND_MUSIC_ENABLED', 'false').lower() == 'true' else '❌ DÉSACTIVÉE'}")
        
        # PRÉPARATION
        if not setup_directories(config):
            print("❌ Échec configuration - Arrêt du processus")
            return False
        
        # CRÉATION DES VIDÉOS
        successful_videos = create_and_process_videos(
            mode=mode,
            slot_hours=slot_hours,
            slot_pause_s=slot_pause,
            config=config,
            debug_mode=debug_mode,
            force_run=force_run
        )
        
        # UPLOAD YOUTUBE
        upload_success = handle_upload(successful_videos, mode, config)
        
        # RAPPORT FINAL
        print("\n" + "=" * 70)
        print("📊 RAPPORT FINAL DE PRODUCTION")
        print("=" * 70)
        
        total_slots = len(slot_hours) if mode == "all" else 1
        success_count = len(successful_videos)
        
        print(f"🎯 Créneaux traités: {success_count}/{total_slots}")
        print(f"📤 Upload YouTube: {'✅ SUCCÈS' if upload_success else '⚠️ NON RÉALISÉ'}")
        print(f"🎵 Musique: {'✅ INTÉGRÉE' if success_count > 0 and os.getenv('BACKGROUND_MUSIC_ENABLED', 'false').lower() == 'true' else '❌ ABSENTE'}")
        
        if successful_videos:
            print("\n📋 VIDÉOS PRODUITES:")
            for video in successful_videos:
                file_exists = os.path.exists(video['path'])
                file_size = os.path.getsize(video['path']) / (1024 * 1024) if file_exists else 0
                print(f"   🎬 Créneau {video['slot']}: {video['title']} ({file_size:.1f} MB)")
        
        success_message = "PROCESSUS TERMINÉ AVEC SUCCÈS" if success_count > 0 else "PROCESSUS TERMINÉ - AUCUNE VIDÉO PRODUITE"
        print(f"\n🎉 {success_message}")
        
        return success_count > 0
        
    except KeyboardInterrupt:
        print("\n⏹️ Processus interrompu par l'utilisateur")
        return False
        
    except Exception as e:
        print(f"\n💥 ERREUR CRITIQUE: {e}")
        if debug_mode:
            print("\n🔍 Stack trace complète:")
            traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
