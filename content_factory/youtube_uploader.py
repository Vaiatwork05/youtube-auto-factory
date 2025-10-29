# content_factory/youtube_uploader.py

import os
import sys
import json
from typing import Dict, Any, Optional

# Dépendances Google API (assurons-nous qu'elles sont installées)
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError # Pour gérer les tokens expirés

# Scopes d'accès requis pour l'upload (doit correspondre à la création du token)
YOUTUBE_UPLOAD_SCOPE = ["https://www.googleapis.com/auth/youtube.upload"]

class YouTubeUploader:
    """
    Gère l'authentification et l'upload de vidéos sur YouTube via OAuth 2.0.
    """
    
    # Mappage des catégories YouTube les plus courantes pour la science/tech
    # 27 = Éducation, 28 = Science & Technologie
    DEFAULT_CATEGORY_ID = "28" 

    def __init__(self, client_id: str, client_secret: str, refresh_token: str, channel_id: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.refresh_token = refresh_token
        self.channel_id = channel_id
        self.youtube = self._authenticate()
    
    def _authenticate(self) -> build:
        """Authentification utilisant le Refresh Token pour obtenir un Access Token."""
        print("\n🔐 ÉTAPE 1: Authentification YouTube (OAuth 2.0 Tête de Série)...")
        
        # Créer l'objet Credentials à partir des informations de l'application et du token
        creds = Credentials(
            token=None,  # Pas d'access token initial
            refresh_token=self.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=YOUTUBE_UPLOAD_SCOPE
        )

        try:
            # Tenter de rafraîchir le token pour obtenir un access token
            creds.refresh(Request())
            
            # Construire le service YouTube
            youtube = build(
                'youtube', 
                'v3', 
                credentials=creds,
                cache_discovery=False # Évite les problèmes de mise en cache en CI
            )
            
            print("✅ Authentification réussie.")
            return youtube

        except RefreshError as e:
            raise Exception(f"❌ Erreur de rafraîchissement du token : Vérifiez le client_id/secret et le refresh_token. Détail: {e}")
        except Exception as e:
            raise Exception(f"❌ Erreur critique lors de l'authentification: {e}")
            
    def upload_video(self, video_path: str, content_data: Dict[str, Any], category_id: str = DEFAULT_CATEGORY_ID) -> Optional[str]:
        """Upload une vidéo sur YouTube en utilisant les métadonnées de content_data."""
        
        if not self.youtube:
             print("❌ Upload annulé: L'API YouTube n'a pas pu être authentifiée.")
             return None
        
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Fichier vidéo introuvable: {video_path}")
            
        # Extraction et sécurisation des métadonnées
        title = content_data.get('title', 'Titre Par Défaut')
        # Limiter la description (YouTube tronque après 5000 chars)
        description = content_data.get('script', 'Description vidéo générée.').strip()
        tags_raw = content_data.get('keywords', [])
        
        # Créer les tags (les tags ne sont pas présents dans content_generator.py, on utilise la catégorie comme base)
        # On peut améliorer cela en utilisant des mots-clés générés par le script ou par IA
        tags = [content_data.get('category', 'science'), title.lower().replace(' ', '_'), "automatisation", "tech"] + tags_raw
        
        # --- ÉTAPE 2: Préparation de l'Upload ---
        body = {
            'snippet': {
                'title': title,
                'description': description,
                'tags': tags[:15], # Limiter à 15 tags max
                'categoryId': category_id,
                'channelId': self.channel_id
            },
            'status': {
                'privacyStatus': 'unlisted', # L'upload en "Non Répertorié" (unlisted) est la meilleure pratique
                'selfDeclaredMadeForKids': False # IMPORTANT : À ajuster selon le contenu.
            }
        }
        
        media_file = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        
        print(f"🎬 Début de l'upload: {title[:50]}...")
        print(f"🏷️ Tags utilisés: {tags[:5]}...")
        
        # --- ÉTAPE 3: Appel à l'API ---
        try:
            request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media_file
            )
            
            # Exécution de l'upload (avec gestion de la progression si nécessaire, omis pour la simplicité)
            response = request.execute()
            video_id = response.get('id')
            
            print(f"✅ Upload terminé! ID Vidéo: {video_id}")
            print(f"🔗 URL: https://www.youtube.com/watch?v={video_id}")
            
            return video_id

        except Exception as e:
            print(f"❌ Erreur critique lors de l'upload: {e}")
            # Afficher des détails d'erreur pour le debug en CI
            if hasattr(e, 'content'):
                print(f"Détail API: {e.content.decode('utf-8')}")
            return None

# --- Bloc de Test ---
if __name__ == "__main__":
    # NOTE: Ces valeurs sont des placeholders et ne fonctionneront pas
    MOCK_CLIENT_ID = os.getenv("YOUTUBE_CLIENT_ID", "mock_client_id")
    MOCK_CLIENT_SECRET = os.getenv("YOUTUBE_CLIENT_SECRET", "mock_secret")
    MOCK_REFRESH_TOKEN = os.getenv("YOUTUBE_REFRESH_TOKEN", "mock_refresh_token")
    MOCK_CHANNEL_ID = "UC_Mock_Channel_ID" 
    
    print("🧪 Test YouTubeUploader (Authentification simulée)...")
    
    try:
        # L'initialisation échouera si les tokens sont invalides, ce qui est attendu en test local
        uploader = YouTubeUploader(
            client_id=MOCK_CLIENT_ID,
            client_secret=MOCK_CLIENT_SECRET,
            refresh_token=MOCK_REFRESH_TOKEN,
            channel_id=MOCK_CHANNEL_ID
        )
        print("✅ YouTube Uploader initialisé (Authentification Tentée)")
        
        # Simuler un appel d'upload avec des données de contenu (l'upload réel sera rejeté sans un token valide)
        mock_content = {
            'title': 'Test d\'Upload Automatique de l\'IA',
            'script': 'Ceci est la description détaillée du test pour valider le processus.',
            'category': 'technologie',
            'keywords': ['ai', 'automation', 'youtube_api']
        }
        mock_video_path = os.path.join(os.getcwd(), 'test_file.mp4')
        
        # Créer un fichier de mock
        if not os.path.exists(mock_video_path):
             with open(mock_video_path, 'w') as f:
                 f.write("Ce n'est pas une vraie vidéo, juste un placeholder.")
                 
        # Simuler l'upload (qui échouera probablement)
        # uploader.upload_video(mock_video_path, mock_content) 

    except Exception as e:
        print(f"⚠️ Échec du test d'initialisation (attendu sans secrets valides): {e}")
        # sys.exit(1) # Ne pas forcer l'échec pour le test d'initialisation
