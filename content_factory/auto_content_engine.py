#!/usr/bin/env python3
"""
YouTube Auto Factory - Orchestrateur Principal
Version optimisée pour GitHub Actions avec gestion hybride .env + secrets
"""

import os
import sys
import time
import argparse
from datetime import datetime
from typing import Dict, Any, List, Optional

# =============================================================================
# 🔧 CONFIGURATION HYBRIDE .env + SECRETS GITHUB
# =============================================================================

def setup_hybrid_environment():
    """Configure l'environnement avec priorité GitHub Secrets mais conserve .env"""
    try:
        from dotenv import load_dotenv
        load_dotenv(override=False)  # Charger .env sans écraser les variables existantes
        
        # Mapping des secrets GitHub vers variables d'environnement
        secret_mapping = {
            'DEEPSEEK_API_KEY': 'DEEPSEEK_API_KEY',
            'UNSPLASH_API_KEY': 'UNSPLASH_API_KEY', 
            'HUGGINGFACE_TOKEN': 'HUGGINGFACE_TOKEN',
            'GEMINI_API_KEY': 'GEMINI_API_KEY',
            'GROQ_API_KEY': 'GROQ_API_KEY',
            'OPENAI_API_KEY': 'OPENAI_API_KEY'
        }
        
        # Injecter les secrets GitHub (priorité sur .env)
        for secret_name, env_var in secret_mapping.items():
            secret_value = os.getenv(secret_name)
            if secret_value:
                os.environ[env_var] = secret_value
                print(f"✅ {env_var} chargé depuis GitHub Secrets")
            elif os.getenv(env_var):
                print(f"🔸 {env_var} chargé depuis .env")
            else:
                print(f"⚠️ {env_var} non définie")
                
    except ImportError:
        print("🔸 python-dotenv non disponible - utilisation variables système")

# Initialisation immédiate
setup_hybrid_environment()

# =============================================================================
# IMPORTS CONDITIONNELS
# =============================================================================

def setup_imports():
    """Configure les chemins d'import Python"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

setup_imports()

# Import des modules avec gestion d'erreur
try:
    from content_factory.content_generator import generate_daily_contents
    from content_factory.video_creator import VideoCreator
    from content_factory.youtube_uploader import YouTubeUploader
    from content_factory.config_loader import ConfigLoader
    MODULES_LOADED = True
except ImportError as e:
    print(f"❌ Erreur import: {e}")
    MODULES_LOADED = False

# =============================================================================
# FONCTIONS PRINCIPALES
# =============================================================================

def validate_environment() -> bool:
    """Valide la configuration environnement"""
    required_vars = ['DEEPSEEK_API_KEY', 'UNSPLASH_API_KEY']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Variables manquantes: {missing}")
        return False
    
    print("✅ Environnement validé")
    return True

def get_processing_slots(mode: str, slot_hours: List[int]) -> List[int]:
    """Détermine les créneaux à traiter"""
    if mode == "all":
        return list(range(len(slot_hours)))
    
    current_hour = datetime.now().hour
    for i, hour in enumerate(slot_hours):
        if current_hour < hour:
            return [i - 1] if i > 0 else [0]
    
    return [len(slot_hours) - 1]

def process_single_slot(slot_idx: int, contents: List[Dict]) -> Optional[Dict]:
    """Traite un créneau individuel"""
    print(f"🎬 Créneau {slot_idx + 1}")
    
    if slot_idx >= len(contents):
        print("❌ Aucun contenu pour ce créneau")
        return None
    
    content = contents[slot_idx]
    
    try:
        creator = VideoCreator()
        video_path = creator.create_video(content)
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)
            print(f"✅ Vidéo créée: {file_size:.1f}MB")
            return {'path': video_path, 'content': content, 'slot': slot_idx + 1}
        else:
            print("❌ Échec création vidéo")
            return None
            
    except Exception as e:
        print(f"❌ Erreur création: {e}")
        return None

def upload_videos(videos: List[Dict], config: Dict) -> bool:
    """Gère l'upload YouTube"""
    if not videos or not config.get('YOUTUBE', {}).get('ENABLE_AUTO_UPLOAD', False):
        return False
    
    try:
        uploader = YouTubeUploader()
        return uploader.upload_video(videos[0]['path'], videos[0]['content'])
    except Exception as e:
        print(f"❌ Erreur upload: {e}")
        return False

# =============================================================================
# ORCHESTRATEUR PRINCIPAL
# =============================================================================

def execute_production_cycle(config: Dict, args: argparse.Namespace) -> bool:
    """Exécute un cycle complet de production"""
    
    # 1. Génération du contenu
    print("📝 Génération du contenu...")
    contents = generate_daily_contents()
    if not contents:
        print("❌ Échec génération contenu")
        return False
    
    # 2. Détermination des créneaux
    slot_hours = config.get('WORKFLOW', {}).get('SLOT_HOURS', [8, 12, 16, 20])
    slots_to_process = get_processing_slots("all" if args.all else "auto", slot_hours)
    
    print(f"🎯 Créneaux à traiter: {[s+1 for s in slots_to_process]}")
    
    # 3. Création des vidéos
    successful_videos = []
    for slot_idx in slots_to_process:
        result = process_single_slot(slot_idx, contents)
        if result:
            successful_videos.append(result)
        
        # Pause entre les créneaux
        if slot_idx != slots_to_process[-1]:
            time.sleep(config.get('WORKFLOW', {}).get('SLOT_PAUSE_SECONDS', 10))
    
    # 4. Upload YouTube
    if successful_videos and config.get('YOUTUBE', {}).get('ENABLE_AUTO_UPLOAD', False):
        print("📤 Upload YouTube...")
        upload_success = upload_videos(successful_videos, config)
        print(f"📤 Upload: {'✅' if upload_success else '❌'}")
    
    # Rapport final
    print(f"\n📊 Production terminée: {len(successful_videos)}/{len(slots_to_process)} vidéos créées")
    return len(successful_videos) > 0

# =============================================================================
# POINT D'ENTRÉE
# =============================================================================

def main():
    """Fonction principale"""
    
    if not MODULES_LOADED:
        print("❌ Modules non chargés - Arrêt")
        return False
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--all', action='store_true', help="Traiter tous les créneaux")
    parser.add_argument('--force-run', type=str, default='false')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()
    
    print("🚀 YouTube Auto Factory - Démarrage")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔧 Mode: {'COMPLET' if args.all else 'AUTO'}")
    
    # Validation initiale
    if not validate_environment():
        return False
    
    try:
        config = ConfigLoader().get_config()
        success = execute_production_cycle(config, args)
        print(f"\n🎯 Résultat: {'SUCCÈS' if success else 'ÉCHEC'}")
        return success
        
    except Exception as e:
        print(f"💥 Erreur critique: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
