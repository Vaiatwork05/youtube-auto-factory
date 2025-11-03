# content_factory/config_loader.py (VERSION CORRIGÉE)

import os
import sys
from typing import Dict, Any, List

class ConfigLoader:
    _config = None

    def __init__(self):
        if ConfigLoader._config is None:
            self._load_config_from_env()

    def _load_config_from_env(self):
        """Charge la configuration depuis ton .env ACTUEL"""
        
        ConfigLoader._config = {
            'WORKFLOW': {
                'DAILY_SLOTS': self._get_int('DAILY_SLOTS', 4),
                'SLOT_HOURS': self._get_int_list('SLOT_HOURS', [8, 12, 16, 20]),
                'SLOT_PAUSE_SECONDS': self._get_int('SLOT_PAUSE_SECONDS', 5),
                'ENABLE_AUTO_UPLOAD': self._get_bool('ENABLE_AUTO_UPLOAD', False),
                'UPLOAD_MAX_RETRIES': self._get_int('UPLOAD_MAX_RETRIES', 0)
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
                'RESOLUTION': [1080, 1920],
                'FPS': self._get_int('VIDEO_FPS', 30),
                'VIDEO_CODEC': self._get_str('VIDEO_CODEC', 'libx264'),
                'AUDIO_CODEC': self._get_str('AUDIO_CODEC', 'aac'),
                'VIDEO_BITRATE': self._get_str('VIDEO_BITRATE', '12000k'),
                'AUDIO_BITRATE': self._get_str('AUDIO_BITRATE', '320k'),
                'MIN_IMAGE_DURATION': self._get_float('MIN_IMAGE_DURATION', 3.0),
                'MAX_IMAGE_DURATION': self._get_float('MAX_IMAGE_DURATION', 6.0),
                'MAX_VIDEO_GENERATION_TIME': self._get_int('MAX_VIDEO_GENERATION_TIME', 600)
            },
            'AUDIO_GENERATOR': {
                'MAX_AUDIO_DURATION': self._get_int('MAX_AUDIO_DURATION', 65),
                'MIN_AUDIO_DURATION': self._get_int('MIN_AUDIO_DURATION', 45),
                'TTS_VOICES': self._get_str_list('TTS_VOICES', ['fr-FR-DeniseNeural', 'fr-FR-HenriNeural', 'fr-FR-AlainNeural']),
                'DEFAULT_VOICE': self._get_str('DEFAULT_TTS_VOICE', 'fr-FR-AlainNeural'),
                'TTS_SPEED': self._get_float('TTS_SPEED', 1.15),
                'TTS_RETRY_COUNT': self._get_int('TTS_RETRY_COUNT', 5),
                'TTS_ENGINE': self._get_str('TTS_ENGINE', 'edge-tts'),
                'AUDIO_QUALITY': self._get_str('AUDIO_QUALITY', 'ultra'),
                'AUDIO_BITRATE': self._get_str('AUDIO_BITRATE', '320k'),
                'ENABLE_AUDIO_NORMALIZATION': self._get_bool('ENABLE_AUDIO_NORMALIZATION', True),
                'BACKGROUND_MUSIC_ENABLED': self._get_bool('BACKGROUND_MUSIC_ENABLED', False),
                'BACKGROUND_MUSIC_VOLUME': self._get_float('BACKGROUND_MUSIC_VOLUME', 0.20)
            },
            'AI_GENERATOR': {
                'DEEPSEEK_API_KEY': self._get_str('DEEPSEEK_API_KEY', ''),
                'HUGGINGFACE_TOKEN': self._get_str('HUGGINGFACE_TOKEN', ''),
                'AI_PROVIDER': self._get_str('AI_PROVIDER', 'deepseek'),
                'AI_MODEL': self._get_str('AI_MODEL', 'deepseek-chat'),
                'AI_TEMPERATURE': self._get_float('AI_TEMPERATURE', 0.7),
                'AI_MAX_TOKENS': self._get_int('AI_MAX_TOKENS', 2000),
                'AI_ENABLED': self._get_bool('AI_ENABLED', True),
                'AI_FALLBACK_ENABLED': self._get_bool('AI_FALLBACK_ENABLED', True)
            },
            'IMAGE_MANAGER': {
                'UNSPLASH_API_KEY': self._get_str('UNSPLASH_API_KEY', ''),
                'REDDIT_CLIENT_ID': self._get_str('REDDIT_CLIENT_ID', ''),
                'REDDIT_CLIENT_SECRET': self._get_str('REDDIT_CLIENT_SECRET', ''),
                'REDDIT_USER_AGENT': self._get_str('REDDIT_USER_AGENT', 'youtube-auto-factory-v1'),
                'IMAGES_PER_VIDEO': self._get_int('IMAGES_PER_VIDEO', 12),
                'IMAGE_QUALITY': self._get_int('IMAGE_QUALITY', 95),
                'IMAGE_CACHE_ENABLED': self._get_bool('IMAGE_CACHE_ENABLED', True),
                'MAX_CACHE_SIZE_MB': self._get_int('MAX_CACHE_SIZE_MB', 1000),
                'CLEANUP_OLD_IMAGES': self._get_bool('CLEANUP_OLD_IMAGES', True),
                'MAX_IMAGES_TO_KEEP': self._get_int('MAX_IMAGES_TO_KEEP', 50),
                'IMAGE_SEARCH_TIMEOUT': self._get_int('IMAGE_SEARCH_TIMEOUT', 45)
            },
            'BRAINROT': {
                'ENABLE_BRAINROT_STYLE': self._get_bool('ENABLE_BRAINROT_STYLE', True),
                'BRAINROT_INTENSITY': self._get_str('BRAINROT_INTENSITY', 'ultra'),
                'ENABLE_DYNAMIC_TRANSITIONS': self._get_bool('ENABLE_DYNAMIC_TRANSITIONS', True),
                'ENABLE_EMOJI_OVERLAY': self._get_bool('ENABLE_EMOJI_OVERLAY', False),
                'TOP10_PART1_DURATION': self._get_int('TOP10_PART1_DURATION', 59),
                'TOP10_PART2_DURATION': self._get_int('TOP10_PART2_DURATION', 59),
                'ENABLE_PART_LINKING': self._get_bool('ENABLE_PART_LINKING', True),
                'AUTO_GENERATE_CLIFFHANGERS': self._get_bool('AUTO_GENERATE_CLIFFHANGERS', True)
            },
            'PERFORMANCE': {
                'MAX_CONCURRENT_DOWNLOADS': self._get_int('MAX_CONCURRENT_DOWNLOADS', 2),
                'REQUEST_TIMEOUT': self._get_int('REQUEST_TIMEOUT', 60),
                'MAX_MEMORY_USAGE_MB': self._get_int('MAX_MEMORY_USAGE_MB', 4096),
                'ENABLE_GARBAGE_COLLECTION': self._get_bool('ENABLE_GARBAGE_COLLECTION', True),
                'CLEANUP_TEMP_FILES': self._get_bool('CLEANUP_TEMP_FILES', True),
                'MAX_RETRY_ATTEMPTS': self._get_int('MAX_RETRY_ATTEMPTS', 5),
                'RETRY_DELAY_SECONDS': self._get_int('RETRY_DELAY_SECONDS', 3),
                'CONNECTION_TIMEOUT': self._get_int('CONNECTION_TIMEOUT', 45),
                'ENABLE_RATE_LIMITING': self._get_bool('ENABLE_RATE_LIMITING', True)
            },
            'APP': {
                'APP_ENV': self._get_str('APP_ENV', 'production'),
                'DEBUG_MODE': self._get_bool('DEBUG_MODE', True),
                'LOG_LEVEL': self._get_str('LOG_LEVEL', 'DEBUG'),
                'ENABLE_METRICS': self._get_bool('ENABLE_METRICS', True),
                'LOG_TO_FILE': self._get_bool('LOG_TO_FILE', True),
                'MAX_LOG_FILE_SIZE': self._get_str('MAX_LOG_FILE_SIZE', '100MB'),
                'LOG_RETENTION_DAYS': self._get_int('LOG_RETENTION_DAYS', 3),
                'ENABLE_DEBUG_FALLBACKS': self._get_bool('ENABLE_DEBUG_FALLBACKS', True),
                'VERBOSE_LOGGING': self._get_bool('VERBOSE_LOGGING', True),
                'ENABLE_DIAGNOSTIC_MODE': self._get_bool('ENABLE_DIAGNOSTIC_MODE', True)
            }
        }

    def _get_str(self, key: str, default: str) -> str:
        return os.getenv(key, default)

    def _get_int(self, key: str, default: int) -> int:
        try:
            return int(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

    def _get_float(self, key: str, default: float) -> float:
        try:
            return float(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

    def _get_bool(self, key: str, default: bool) -> bool:
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')

    def _get_str_list(self, key: str, default: List[str]) -> List[str]:
        value = os.getenv(key, '')
        if not value:
            return default
        return [item.strip() for item in value.split(',') if item.strip()]

    def _get_int_list(self, key: str, default: List[int]) -> List[int]:
        value = os.getenv(key, '')
        if not value:
            return default
        try:
            return [int(item.strip()) for item in value.split(',') if item.strip()]
        except (ValueError, TypeError):
            return default

    def get_config(self) -> Dict[str, Any]:
        return ConfigLoader._config

    def print_config_summary(self):
        """Affiche un résumé de la configuration ACTUELLE"""
        config = self.get_config()
        print("🎯 CONFIGURATION ACTUELLE")
        print("=" * 50)
        print(f"🤖 IA: {config['AI_GENERATOR']['AI_PROVIDER']} | DeepSeek: {'✅' if config['AI_GENERATOR']['DEEPSEEK_API_KEY'] else '❌'} | HF: {'✅' if config['AI_GENERATOR']['HUGGINGFACE_TOKEN'] else '❌'}")
        print(f"🎬 Vidéo: {config['VIDEO_CREATOR']['RESOLUTION'][0]}x{config['VIDEO_CREATOR']['RESOLUTION'][1]} | Bitrate: {config['VIDEO_CREATOR']['VIDEO_BITRATE']}")
        print(f"🎵 Audio: TTS {config['AUDIO_GENERATOR']['DEFAULT_VOICE']} | Qualité: {config['AUDIO_GENERATOR']['AUDIO_QUALITY']}")
        print(f"🖼️ Images: {config['IMAGE_MANAGER']['IMAGES_PER_VIDEO']}/vidéo | Unsplash: {'✅' if config['IMAGE_MANAGER']['UNSPLASH_API_KEY'] else '❌'}")
        print(f"🧠 Brainrot: Intensité {config['BRAINROT']['BRAINROT_INTENSITY']} | Style: {config['BRAINROT']['ENABLE_BRAINROT_STYLE']}")
        print(f"⚡ Performance: {config['PERFORMANCE']['MAX_CONCURRENT_DOWNLOADS']} téléchargements | Timeout: {config['PERFORMANCE']['REQUEST_TIMEOUT']}s")
        print("=" * 50)

# Instance globale
config_loader = ConfigLoader()

if __name__ == "__main__":
    print("🧪 Test ConfigLoader corrigé...")
    try:
        loader = ConfigLoader()
        config = loader.get_config()
        
        print("✅ ConfigLoader CORRIGÉ chargé avec succès!")
        loader.print_config_summary()
        
    except Exception as e:
        print(f"❌ Test échoué: {e}")
        sys.exit(1)
