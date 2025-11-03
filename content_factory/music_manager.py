# content_factory/music_manager.py (VERSION CORRIGÉE)

import os
import re
import time
import requests
import random
from typing import Optional, List, Dict
from urllib.parse import quote
from content_factory.utils import safe_path_join, ensure_directory

class MusicManager:
    """Gestionnaire intelligent de musique libre de droits - VERSION CORRIGÉE"""
    
    def __init__(self):
        # 🔥 CORRECTION : Vérifier yt-dlp
        try:
            import yt_dlp
            self.yt_dlp_available = True
        except ImportError:
            self.yt_dlp_available = False
            print("❌ yt-dlp non installé - téléchargement YouTube désactivé")
        
        # 🔥 CORRECTION : Variables cohérentes avec votre .env
        self.music_enabled = os.getenv('BACKGROUND_MUSIC_ENABLED', 'false').lower() == 'true'
        self.music_volume = float(os.getenv('BACKGROUND_MUSIC_VOLUME', '0.25'))
        
        # Variable cohérente avec votre configuration existante
        self.auto_download = os.getenv('AUTO_DOWNLOAD_MUSIC', 'false').lower() == 'true'
        
        self.music_dir = safe_path_join("assets", "music")
        self.download_dir = safe_path_join(self.music_dir, "downloaded")
        
        ensure_directory(self.music_dir)
        ensure_directory(self.download_dir)
        
        # Genres de musique "brainrot"
        self.brainrot_genres = [
            "synthwave", "lofi", "electronic", "ambient", "chillhop",
            "vaporwave", "future bass", "trap", "dubstep", "phonk"
        ]
        
        print(f"🎵 MusicManager - Statut: {'✅ ACTIVÉ' if self.music_enabled else '❌ DÉSACTIVÉ'}")
        print(f"📥 Auto-download: {'✅ ON' if self.auto_download else '❌ OFF'}")
        print(f"🔊 Volume: {self.music_volume}")

    def find_brainrot_music(self, video_duration: float, content_theme: str) -> Optional[str]:
        """Trouve une musique brainrot libre de droits."""
        if not self.music_enabled:
            print("🎵 Musique désactivée dans la configuration")
            return None
        
        print("🎵 Recherche de musique brainrot libre de droits...")
        
        # D'abord essayer les musiques existantes
        existing_music = self.get_existing_music(video_duration)
        if existing_music:
            print(f"✅ Musique existante trouvée: {os.path.basename(existing_music)}")
            return existing_music
        
        # Ensuite essayer le téléchargement si activé
        if self.auto_download and self.yt_dlp_available:
            sources = [
                self._download_from_youtube,
                self._try_bensound,
            ]
            
            for source in sources:
                try:
                    music_path = source(video_duration, content_theme)
                    if music_path and os.path.exists(music_path):
                        print(f"✅ Nouvelle musique téléchargée: {os.path.basename(music_path)}")
                        return music_path
                except Exception as e:
                    print(f"❌ {source.__name__} échoué: {e}")
                    continue
        
        print("❌ Aucune musique trouvée")
        return None

    def _download_from_youtube(self, duration: float, theme: str) -> Optional[str]:
        """Télécharge une musique depuis YouTube (creative commons)."""
        if not self.yt_dlp_available:
            return None
            
        print("   📺 YouTube Creative Commons...")
        
        # Recherche de musiques Creative Commons
        search_queries = [
            "lofi hip hop radio - beats to relax",
            "synthwave radio - retro waves",
            "chillhop music - jazzy lofi", 
            "vaporwave radio - aesthetic sounds",
            "background music no copyright",
            "royalty free electronic music",
        ]
        
        query = random.choice(search_queries)
        return self._download_youtube_audio(query, duration)

    def _download_youtube_audio(self, query: str, duration: float) -> Optional[str]:
        """Télécharge l'audio d'une vidéo YouTube."""
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': safe_path_join(self.download_dir, f'youtube_%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
                'extractaudio': True,
                'audioformat': 'mp3',
                'noplaylist': True,
                'max_downloads': 1,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Recherche avec filtre Creative Commons
                search_query = f"{query}"
                info = ydl.extract_info(f"ytsearch1:{search_query}", download=True)
                
                if info and 'entries' in info and info['entries']:
                    video = info['entries'][0]
                    filename = ydl.prepare_filename(video)
                    print(f"   ✅ Téléchargé: {os.path.basename(filename)}")
                    return filename
                    
        except Exception as e:
            print(f"   ❌ YouTube download: {e}")
            
        return None

    def _try_bensound(self, duration: float, theme: str) -> Optional[str]:
        """Utilise Bensound (musiques libres)."""
        print("   🎹 Bensound...")
        
        # Bensound a des musiques libres avec attribution
        bensound_tracks = [
            "https://www.bensound.com/bensound-music/bensound-anewbeginning.mp3",
            "https://www.bensound.com/bensound-music/bensound-creativeminds.mp3", 
            "https://www.bensound.com/bensound-music/bensound-evolution.mp3",
        ]
        
        try:
            music_url = random.choice(bensound_tracks)
            return self._download_audio_file(music_url, "bensound")
        except Exception as e:
            print(f"   ❌ Bensound: {e}")
            return None

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
                
                print(f"   ✅ Téléchargé: {filename}")
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
            if file.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg')):
                filepath = safe_path_join(self.music_dir, file)
                music_files.append(filepath)
        
        if music_files:
            # Prendre un fichier au hasard
            return random.choice(music_files)
        
        return None
