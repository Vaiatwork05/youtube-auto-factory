# content_factory/youtube_uploader.py (Intégration config.yaml)

import os
import sys
import json
from typing import Dict, Any, Optional, List

# Dépendances Google API
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

# Imports du projet
from content_factory.config_loader import ConfigLoader
from content_factory.utils import clean_and_format_keywords

# Scopes d'accès requis pour l'upload
YOUTUBE_UPLOAD_SCOPE = ["https://www.googleapis.com/auth/youtube.upload"]

class YouTubeUploader:
    """
    Gère l'authentification et l'upload de vidéos sur YouTube via OAuth 2.0,
    en utilisant les paramètres du config.yaml.
    """
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.uploader_config = self.config['YOUTUBE_UPLOADER']
        self.channel_id = self.config['WORKFLOW']['TARGET_CHANNEL_ID']
        
        # Récupération des secrets via la configuration (déjà interprétés par ConfigLoader)
        self.client_id = self.uploader_config['CLIENT_ID']
        self.client_secret = self.uploader_config['CLIENT_SECRET']
        self.refresh_token = self.uploader_config['REFRESH_TOKEN']
        
        self.youtube = self._authenticate()
    
    def _authenticate(self) -> build:
        """Authentification utilisant le Refresh Token pour obtenir un Access Token."""
        print("\n🔐 ÉTAPE 1: Authentification YouTube (OAuth 2.0 Tête de Série)...")
        
        if not self.client_id or not self.client_secret or not self.refresh_token:
            raise Exception("❌ Authentification annulée: Un ou plusieurs secrets (ID, Secret, Token) sont manquants dans la configuration.")
        
        creds = Credentials(
            token=None,
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=YOUTUBE_UPLOAD_SCOPE
        )

        try:
            creds.refresh(Request())
            
            youtube = build(
                'youtube', 
                'v3', 
                credentials=creds,
                cache_discovery=False
            )
            
            print("✅ Authentification réussie.")
            return youtube

        except RefreshError as e:
            raise Exception(f"❌ Erreur de rafraîchissement du token : Vérifiez les secrets ou que le token est valide. Détail: {e}")
        except Exception as e:
            raise Exception(f"❌ Erreur critique lors de l'authentification: {e}")
            
    def upload_video(self, video_path: str, content_data: Dict[str, Any]) -> Optional[str]:
        """Upload une vidéo sur YouTube en utilisant les métadonnées de content_data."""
        
        if not self.youtube:
             print("❌ Upload annulé: L'API YouTube n'a pas pu être authentifiée.")
             return None
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Fichier vidéo introuvable: {video_path}")
            
        # Extraction et sécurisation des métadonnées
        title = content_data.get('title', 'Titre Par Défaut')
        description = content_data.get('script', 'Description vidéo générée.').strip()
        
        # Générer des tags propres et uniques à partir des mots-clés du contenu
        raw_keywords = content_data.get('keywords', [])
        # Ajout des tags par défaut à partir de la catégorie
        default_tags = [content_data.get('category', 'science'), "automatisation", "science"]
        
        all_tags = default_tags + raw_keywords
        tags: List[str] = clean_and_format_keywords(all_tags, max_tags=15)
        
        
        # Préparation du corps de la requête
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags,
                'categoryId': self.uploader_config.get('DEFAULT_CATEGORY_ID', '28'),
                'channelId': self.channel_id
            },
            'status': {
                'privacyStatus': self.uploader_config.get('PRIVACY_STATUS', 'unlisted'),
                'selfDeclaredMadeForKids': self.uploader_config.get('MADE_FOR_KIDS', False)
            }
        }
        
        media_file = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        print(f"🎬 Début de l'upload: {title[:50]}...")
        print(f"🏷️ Tags utilisés: {tags}...")
        
        # Appel à l'API
        try:
            request = self.youtube.videos().insert(
                part=','.join(body['snippet'].keys()) + ',' + ','.join(body['status'].keys()),
                body=body,
                media_body=media_file
            )
            
            response = request.execute()
            video_id = response.get('id')
            
            print(f"✅ Upload terminé! ID Vidéo: {video_id}")
            print(f"🔗 URL: https://www.youtube.com/watch?v={video_id}")
            
            return video_id

        except Exception as e:
            print(f"❌ Erreur critique lors de l'upload: {e}")
            if hasattr(e, 'content'):
                print(f"Détail API: {e.content.decode('utf-8')}")
            return None

# --- Le bloc de test est omis ici pour la concision ---
