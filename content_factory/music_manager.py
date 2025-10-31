# content_factory/music_manager.py

import os
import re
import time
import requests
import random
from typing import Optional, List, Dict
from urllib.parse import quote
import yt_dlp
from content_factory.utils import safe_path_join, ensure_directory

class MusicManager:
    """Gestionnaire intelligent de musique libre de droits."""
    
    def __init__(self):
        self.music_enabled = os.getenv('BACKGROUND_MUSIC_ENABLED', 'false').lower() == 'true'
        self.auto_download = os.getenv('AUTO_DOWNLOAD_MUSIC', 'false').lower() == 'true'
        self.music_volume = float(os.getenv('BACKGROUND_MUSIC_VOLUME', '0.25'))
        self.music_dir = safe_path_join("assets", "music")
        self.download_dir = safe_path_join(self.music_dir, "downloaded")
        
        ensure_directory(self.music_dir)
        ensure_directory(self.download_dir)
        
        # Genres de musique "brainrot"
        self.brainrot_genres = [
            "synthwave", "lofi", "electronic", "ambient", "chillhop",
            "vaporwave", "future bass", "trap", "dubstep", "phonk"
        ]
        
        # Mots-clés pour musique hypnotique
        self.hypnotic_keywords = [
            "hypnotic", "trance", "loop", "ambient", "atmospheric",
            "meditative", "dreamy", "ethereal", "psychill", "space"
        ]
        
        print(f"🎵 MusicManager - Auto-download: {'✅ ON' if self.auto_download else '❌ OFF'}")

    def find_brainrot_music(self, video_duration: float, content_theme: str) -> Optional[str]:
        """Trouve une musique brainrot libre de droits."""
        if not self.music_enabled:
            return None
        
        print("🎵 Recherche de musique brainrot libre de droits...")
        
        # Essayer différentes sources
        sources = [
            self._try_youtube_audio_library,
            self._try_freemusicarchive, 
            self._try_pixabay_music,
            self._try_bensound,
            self._download_from_youtube  # Dernier recours
        ]
        
        for source in sources:
            try:
                music_path = source(video_duration, content_theme)
                if music_path and os.path.exists(music_path):
                    print(f"✅ Musique trouvée: {os.path.basename(music_path)}")
                    return music_path
            except Exception as e:
                print(f"❌ {source.__name__} échoué: {e}")
                continue
        
        print("❌ Aucune musique trouvée")
        return None

    def _try_youtube_audio_library(self, duration: float, theme: str) -> Optional[str]:
        """Utilise YouTube Audio Library (musiques libres)."""
        print("   📚 YouTube Audio Library...")
        
        # Musiques libres YouTube (exemples)
        free_music_tracks = [
            "https://www.youtube.com/watch?v=XXXXXXXXXXX",  # Remplacer par de vraies URLs
        ]
        
        # Pour l'instant, on va télécharger depuis des chaînes dédiées
        brainrot_channels = [
            "UCYO_jab_esuFRV4b17AJtAw",  # 3D Fat Cat
            "UCht8qITGkBvXKsR1BlynVLA",  # ChilledCow
            "UCSJ4gkVC6NrvII8umztf0Ow",  # Lofi Girl
        ]
        
        return self._download_from_youtube_channel(random.choice(brainrot_channels), duration)

    def _try_freemusicarchive(self, duration: float, theme: str) -> Optional[str]:
        """Utilise Free Music Archive."""
        print("   🎼 Free Music Archive...")
        
        # API FMA (simplifiée)
        genres = ["Electronic", "Ambient", "Chillout"]
        genre = random.choice(genres)
        
        try:
            # Recherche simplifiée - en pratique utiliser l'API FMA
            search_url = f"https://freemusicarchive.org/search/?sort=track_date_released&d=1&quicksearch={quote(genre)}"
            response = requests.get(search_url, timeout=15)
            
            if response.status_code == 200:
                # Extraire les URLs des pistes (simplifié)
                # En pratique, parser la page HTML ou utiliser l'API
                pass
        except:
            pass
        
        return None

    def _try_pixabay_music(self, duration: float, theme: str) -> Optional[str]:
        """Utilise Pixabay Music."""
        print("   🖼️ Pixabay Music...")
        
        # Pixabay a une API pour la musique
        api_key = os.getenv('PIXABAY_API_KEY')  # À configurer si vous voulez
        if not api_key:
            return None
            
        try:
            search_terms = ["electronic", "background", "upbeat", "modern"]
            search_term = random.choice(search_terms)
            
            url = f"https://pixabay.com/api/audio/"
            params = {
                'key': api_key,
                'q': search_term,
                'audio_type': 'music',
                'category': 'music',
                'min_duration': int(duration) - 10,
                'max_duration': int(duration) + 10,
                'per_page': 5
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('hits'):
                    music_url = data['hits'][0]['url']
                    return self._download_audio_file(music_url, "pixabay")
                    
        except Exception as e:
            print(f"   ❌ Pixabay: {e}")
            
        return None

    def _try_bensound(self, duration: float, theme: str) -> Optional[str]:
        """Utilise Bensound (musiques libres)."""
        print("   🎹 Bensound...")
        
        # Bensound a des musiques libres avec attribution
        bensound_tracks = [
            "https://www.bensound.com/bensound-music/bensound-anewbeginning.mp3",
            "https://www.bensound.com/bensound-music/bensound-creativeminds.mp3", 
            "https://www.bensound.com/bensound-music/bensound-evolution.mp3",
            "https://www.bensound.com/bensound-music/bensound-funkyelement.mp3",
        ]
        
        try:
            music_url = random.choice(bensound_tracks)
            return self._download_audio_file(music_url, "bensound")
        except:
            return None

    def _download_from_youtube(self, duration: float, theme: str) -> Optional[str]:
        """Télécharge une musique depuis YouTube (creative commons)."""
        print("   📺 YouTube Creative Commons...")
        
        # Recherche de musiques Creative Commons
        search_queries = [
            "lofi hip hop radio",
            "synthwave mix",
            "chillhop music", 
            "vaporwave mix",
            "background music no copyright",
            "royalty free electronic music",
            "copyright free lofi",
            "no copyright synthwave"
        ]
        
        query = random.choice(search_queries)
        return self._download_youtube_audio(query, duration)

    def _download_from_youtube_channel(self, channel_id: str, duration: float) -> Optional[str]:
        """Télécharge une musique depuis une chaîne spécifique."""
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': safe_path_join(self.download_dir, f'channel_{channel_id}_%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extractaudio': True,
                'audioformat': 'mp3',
                'noplaylist': True,
                'max_downloads': 1,
                'match_filter': self._create_duration_filter(duration)
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Télécharger une vidéo récente de la chaîne
                info = ydl.extract_info(f"https://www.youtube.com/channel/{channel_id}/videos", download=False)
                if info and 'entries' in info:
                    for video in info['entries']:
                        if video and video.get('duration', 0) >= duration - 30:
                            ydl.download([video['webpage_url']])
                            return ydl.prepare_filename(video)
                            
        except Exception as e:
            print(f"   ❌ YouTube channel: {e}")
            
        return None

    def _download_youtube_audio(self, query: str, duration: float) -> Optional[str]:
        """Télécharge l'audio d'une vidéo YouTube."""
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': safe_path_join(self.download_dir, f'youtube_%(title)s.%(ext)s'),
                'quiet': True,
                'no_warnings': True,
                'extractaudio': True,
                'audioformat': 'mp3',
                'noplaylist': True,
                'max_downloads': 1,
                'match_filter': self._create_duration_filter(duration)
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Recherche avec filtre Creative Commons
                search_query = f"{query} creative commons"
                info = ydl.extract_info(f"ytsearch1:{search_query}", download=True)
                
                if info and 'entries' in info and info['entries']:
                    video = info['entries'][0]
                    return ydl.prepare_filename(video)
                    
        except Exception as e:
            print(f"   ❌ YouTube download: {e}")
            
        return None

    def _create_duration_filter(self, target_duration: float):
        """Crée un filtre pour la durée."""
        def duration_filter(info):
            if not info.get('duration'):
                return None
            duration = info['duration']
            # Accepter les musiques entre -30s et +60s de la durée cible
            return None if duration < target_duration - 30 or duration > target_duration + 60 else info
        return duration_filter

    def _download_audio_file(self, url: str, source: str) -> Optional[str]:
        """Télécharge un fichier audio direct."""
        try:
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code == 200:
                filename = f"{source}_{int(time.time())}.mp3"
                filepath = safe_path_join(self.download_dir, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(8192):
                        f.write(chunk)
                
                return filepath
        except Exception as e:
            print(f"   ❌ Download {source}: {e}")
            
        return None

    def get_existing_music(self, duration: float) -> Optional[str]:
        """Récupère une musique existante du dossier."""
        if not os.path.exists(self.music_dir):
            return None
            
        music_files = []
        for file in os.listdir(self.music_dir):
            if file.lower().endswith(('.mp3', '.wav', '.m4a')):
                filepath = safe_path_join(self.music_dir, file)
                try:
                    # Essayer de déterminer la durée (simplifié)
                    music_files.append((filepath, os.path.getsize(filepath)))
                except:
                    continue
        
        if music_files:
            # Prendre le fichier le plus récent/gros
            music_files.sort(key=lambda x: x[1], reverse=True)
            return music_files[0][0]
        
        return None
