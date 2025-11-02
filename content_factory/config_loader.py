# content_factory/config_loader.py

import os
import sys
from typing import Dict, Any, List

class ConfigLoader:
    _config = None

    def __init__(self):
        if ConfigLoader._config is None:
            self._load_config_from_env()

    def _load_config_from_env(self):
        """Charge toute la configuration depuis les variables d'environnement"""
        
        ConfigLoader._config = {
            'WORKFLOW': {
                'DAILY_SLOTS': self._get_int('DAILY_SLOTS', 4),
                'SLOT_HOURS': self._get_int_list('SLOT_HOURS', [8, 12, 16, 20]),
                'SLOT_PAUSE_SECONDS': self._get_int('SLOT_PAUSE_SECONDS', 10),
                'DEFAULT_LANGUAGE': self._get_str('DEFAULT_LANGUAGE', 'fr'),
                'ENABLE_AUTO_UPLOAD': self._get_bool('ENABLE_AUTO_UPLOAD', False)
            },
            'PATHS': {
                'OUTPUT_ROOT': self._get_str('OUTPUT_ROOT', 'output'),
                'VIDEO_DIR': self._get_str('VIDEO_DIR', 'videos'),
                'AUDIO_DIR': self._get_str('AUDIO_DIR', 'audio'),
                'IMAGE_DIR': self._get_str('IMAGE_DIR', 'images'),
                'LOG_DIR': self._get_str('LOG_DIR', 'logs'),
                'MUSIC_DIR': self._get_str('MUSIC_DIR', 'assets/music'),
                'TEMP_DIR': self._get_str('TEMP_DIR', 'temp')
            },
            'VIDEO_CREATOR': {
                'RESOLUTION': [1080, 1920],  # Format Shorts forcé
                'FPS': self._get_int('VIDEO_FPS', 30),
                'MAX_DURATION': self._get_int('MAX_AUDIO_DURATION', 120),
                'MIN_DURATION': self._get_int('MIN_AUDIO_DURATION', 15),
                'MIN_IMAGE_DURATION': self._get_float('MIN_IMAGE_DURATION', 2.5),
                'MAX_IMAGE_DURATION': self._get_float('MAX_IMAGE_DURATION', 5.0),
                'VIDEO_CODEC': self._get_str('VIDEO_CODEC', 'libx264'),
                'AUDIO_CODEC': self._get_str('AUDIO_CODEC', 'aac'),
                'BITRATE': self._get_str('BITRATE', '5000k')
            },
            'YOUTUBE_UPLOADER': {
                'DEFAULT_CATEGORY_ID': self._get_str('YOUTUBE_CATEGORY', '28'),
                'PRIVACY_STATUS': self._get_str('YOUTUBE_PRIVACY', 'unlisted'),
                'MADE_FOR_KIDS': self._get_bool('YOUTUBE_MADE_FOR_KIDS', False),
                'CLIENT_ID': self._get_str('YOUTUBE_OAUTH_CLIENT_ID', ''),
                'CLIENT_SECRET': self._get_str('YOUTUBE_OAUTH_CLIENT_SECRET', ''),
                'API_KEY': self._get_str('YOUTUBE_API_KEY', ''),
                'UPLOAD_MAX_RETRIES': self._get_int('UPLOAD_MAX_RETRIES', 3),
                'UPLOAD_TIMEOUT': self._get_int('UPLOAD_TIMEOUT', 300),
                'GLOBAL_TAGS': ['top10', 'brainrot', 'viral', 'shorts', 'trending', 'algorithm', 'addictive']
            },
            'AUDIO_GENERATOR': {
                'BACKGROUND_MUSIC_ENABLED': self._get_bool('BACKGROUND_MUSIC_ENABLED', False),
                'BACKGROUND_MUSIC_VOLUME': self._get_float('BACKGROUND_MUSIC_VOLUME', 0.25),
                'BACKGROUND_MUSIC_FADE_IN': self._get_float('BACKGROUND_MUSIC_FADE_IN', 2.0),
                'BACKGROUND_MUSIC_FADE_OUT': self._get_float('BACKGROUND_MUSIC_FADE_OUT', 3.0),
                'TTS_VOICES': self._get_str_list('TTS_VOICES', ['fr-FR-DeniseNeural']),
                'DEFAULT_VOICE': self._get_str('DEFAULT_TTS_VOICE', 'fr-FR-DeniseNeural'),
                'TTS_SPEED': self._get_float('TTS_SPEED', 1.1),
                'TTS_RETRY_COUNT': self._get_int('TTS_RETRY_COUNT', 3),
                'TTS_ENGINE': self._get_str('TTS_ENGINE', 'edge-tts'),
                'AUDIO_QUALITY': self._get_str('AUDIO_QUALITY', 'high'),
                'AUDIO_BITRATE': self._get_str('AUDIO_BITRATE', '192k'),
                'ENABLE_AUDIO_NORMALIZATION': self._get_bool('ENABLE_AUDIO_NORMALIZATION', True)
            },
            'IMAGE_MANAGER': {
                'UNSPLASH_API_KEY': self._get_str('UNSPLASH_API_KEY', ''),
                'IMAGES_PER_VIDEO': self._get_int('IMAGES_PER_VIDEO', 8),
                'IMAGE_QUALITY': self._get_int('IMAGE_QUALITY', 85),
                'IMAGE_CACHE_ENABLED': self._get_bool('IMAGE_CACHE_ENABLED', True),
                'MAX_CACHE_SIZE_MB': self._get_int('MAX_CACHE_SIZE_MB', 500),
                'CLEANUP_OLD_IMAGES': self._get_bool('CLEANUP_OLD_IMAGES', True),
                'MAX_IMAGES_TO_KEEP': self._get_int('MAX_IMAGES_TO_KEEP', 100),
                'IMAGE_SEARCH_TIMEOUT': self._get_int('IMAGE_SEARCH_TIMEOUT', 30)
            },
            'MUSIC_MANAGER': {
                'AUTO_DOWNLOAD_MUSIC': self._get_bool('AUTO_DOWNLOAD_MUSIC', False),
                'MUSIC_SEARCH_ENGINE': self._get_str('MUSIC_SEARCH_ENGINE', 'youtube'),
                'MUSIC_GENRES': self._get_str_list('MUSIC_GENRES', ['electronic', 'ambient', 'lofi']),
                'MUSIC_MOOD': self._get_str_list('MUSIC_MOOD', ['hypnotic', 'energetic']),
                'MAX_MUSIC_DOWNLOAD_TIME': self._get_int('MAX_MUSIC_DOWNLOAD_TIME', 30),
                'MUSIC_FALLBACK_SOURCES': self._get_str_list('MUSIC_FALLBACK_SOURCES', ['youtube', 'local']),
                'PREFER_INSTRUMENTAL': self._get_bool('PREFER_INSTRUMENTAL', True),
                'MAX_MUSIC_FILE_SIZE_MB': self._get_int('MAX_MUSIC_FILE_SIZE_MB', 10)
            },
            'PERFORMANCE': {
                'MAX_CONCURRENT_DOWNLOADS': self._get_int('MAX_CONCURRENT_DOWNLOADS', 3),
                'REQUEST_TIMEOUT': self._get_int('REQUEST_TIMEOUT', 30),
                'MAX_MEMORY_USAGE_MB': self._get_int('MAX_MEMORY_USAGE_MB', 2048),
                'ENABLE_GARBAGE_COLLECTION': self._get_bool('ENABLE_GARBAGE_COLLECTION', True),
                'CLEANUP_TEMP_FILES': self._get_bool('CLEANUP_TEMP_FILES', True),
                'MAX_RETRY_ATTEMPTS': self._get_int('MAX_RETRY_ATTEMPTS', 3),
                'RETRY_DELAY_SECONDS': self._get_int('RETRY_DELAY_SECONDS', 5)
            },
            'BRAINROT': {
                'ENABLE_BRAINROT_STYLE': self._get_bool('ENABLE_BRAINROT_STYLE', True),
                'BRAINROT_INTENSITY': self._get_str('BRAINROT_INTENSITY', 'high'),
                'ENABLE_DYNAMIC_TRANSITIONS': self._get_bool('ENABLE_DYNAMIC_TRANSITIONS', True),
                'ENABLE_EMOJI_OVERLAY': self._get_bool('ENABLE_EMOJI_OVERLAY', True),
                'TOP10_PART1_DURATION': self._get_int('TOP10_PART1_DURATION', 60),
                'TOP10_PART2_DURATION': self._get_int('TOP10_PART2_DURATION', 45),
                'ENABLE_PART_LINKING': self._get_bool('ENABLE_PART_LINKING', True),
                'AUTO_GENERATE_CLIFFHANGERS': self._get_bool('AUTO_GENERATE_CLIFFHANGERS', True)
            },
            'APP': {
                'APP_ENV': self._get_str('APP_ENV', 'production'),
                'DEBUG_MODE': self._get_bool('DEBUG_MODE', False),
                'LOG_LEVEL': self._get_str('LOG_LEVEL', 'INFO'),
                'ENABLE_METRICS': self._get_bool('ENABLE_METRICS', True),
                'LOG_TO_FILE': self._get_bool('LOG_TO_FILE', True),
                'MAX_LOG_FILE_SIZE': self._get_str('MAX_LOG_FILE_SIZE', '50MB'),
                'LOG_RETENTION_DAYS': self._get_int('LOG_RETENTION_DAYS', 7)
            }
        }

    def _get_str(self, key: str, default: str) -> str:
        """Récupère une variable string avec valeur par défaut"""
        return os.getenv(key, default)

    def _get_int(self, key: str, default: int) -> int:
        """Récupère une variable integer avec valeur par défaut"""
        try:
            return int(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

    def _get_float(self, key: str, default: float) -> float:
        """Récupère une variable float avec valeur par défaut"""
        try:
            return float(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

    def _get_bool(self, key: str, default: bool) -> bool:
        """Récupère une variable booléenne avec valeur par défaut"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')

    def _get_str_list(self, key: str, default: List[str]) -> List[str]:
        """Récupère une liste de strings avec valeur par défaut"""
        value = os.getenv(key, '')
        if not value:
            return default
        return [item.strip() for item in value.split(',') if item.strip()]

    def _get_int_list(self, key: str, default: List[int]) -> List[int]:
        """Récupère une liste d'entiers avec valeur par défaut"""
        value = os.getenv(key, '')
        if not value:
            return default
        try:
            return [int(item.strip()) for item in value.split(',') if item.strip()]
        except (ValueError, TypeError):
            return default

    def get_config(self) -> Dict[str, Any]:
        """Retourne la configuration complète"""
        return ConfigLoader._config

    def print_config_summary(self):
        """Affiche un résumé de la configuration"""
        config = self.get_config()
        print("🎯 CONFIGURATION RÉSUMÉ")
        print("=" * 50)
        print(f"📊 Workflow: {config['WORKFLOW']['DAILY_SLOTS']} slots, Auto-upload: {config['WORKFLOW']['ENABLE_AUTO_UPLOAD']}")
        print(f"🎬 Vidéo: {config['VIDEO_CREATOR']['RESOLUTION'][0]}x{config['VIDEO_CREATOR']['RESOLUTION'][1]}, {config['VIDEO_CREATOR']['FPS']} FPS")
        print(f"🎵 Audio: TTS={config['AUDIO_GENERATOR']['TTS_ENGINE']}, Musique={config['AUDIO_GENERATOR']['BACKGROUND_MUSIC_ENABLED']}")
        print(f"🖼️ Images: {config['IMAGE_MANAGER']['IMAGES_PER_VIDEO']}/vidéo, Qualité: {config['IMAGE_MANAGER']['IMAGE_QUALITY']}%")
        print(f"🧠 Brainrot: {config['BRAINROT']['BRAINROT_INTENSITY']}, Style: {config['BRAINROT']['ENABLE_BRAINROT_STYLE']}")
        print(f"⚡ Performance: {config['PERFORMANCE']['MAX_CONCURRENT_DOWNLOADS']} téléchargements concurrents")
        print("=" * 50)

# Instance globale
config_loader = ConfigLoader()

# --- Test ---
if __name__ == "__main__":
    print("🧪 Test ConfigLoader complet...")
    try:
        loader = ConfigLoader()
        config = loader.get_config()
        
        print("✅ ConfigLoader chargé avec succès!")
        loader.print_config_summary()
        
        # Test d'accès à quelques valeurs
        print("\n🔍 Tests d'accès:")
        print(f"  - Résolution: {config['VIDEO_CREATOR']['RESOLUTION']}")
        print(f"  - Voix TTS: {config['AUDIO_GENERATOR']['DEFAULT_VOICE']}")
        print(f"  - Clé Unsplash: {'✅' if config['IMAGE_MANAGER']['UNSPLASH_API_KEY'] else '❌'}")
        print(f"  - Clé YouTube: {'✅' if config['YOUTUBE_UPLOADER']['API_KEY'] else '❌'}")
        
    except Exception as e:
        print(f"❌ Test échoué: {e}")
        sys.exit(1)
