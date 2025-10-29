# config.yaml
# --- Configuration globale pour YouTube Auto Factory ---

# --- CHEMINS & ORGANISATION ---
PATHS:
  OUTPUT_ROOT: "output"
  VIDEO_DIR: "videos"
  AUDIO_DIR: "audio"
  IMAGE_DIR: "images"
  LOG_DIR: "logs"

# --- FLUX DE TRAVAIL & PLANIFICATION ---
WORKFLOW:
  # Nombre de vidéos à produire chaque jour (doit correspondre à la CRON)
  DAILY_SLOTS: 4
  # Doit correspondre à l'heure UTC de la CRON. Ex: 06 (pour 08h00 CEST)
  SLOT_HOURS_UTC: [6, 10, 14, 18] 

# --- GESTION AUDIO (AudioGenerator) ---
AUDIO_GENERATOR:
  # Voix Edge TTS (ex: "fr-FR-DeniseNeural")
  DEFAULT_VOICE: "fr-FR-DeniseNeural" 
  # Vitesse de parole (1.0 = normale; 1.1 = 10% plus rapide)
  SPEAKING_RATE: 1.05 

# --- GESTION VIDÉO (VideoCreator) ---
VIDEO_CREATOR:
  # Résolution de la vidéo [Largeur, Hauteur] (720p par défaut)
  RESOLUTION: [1280, 720] 
  # Fréquence d'images par seconde
  FPS: 24
  # Bitrate vidéo pour la qualité (5 Mbps)
  BITRATE: "5000k"
  # Nombre d'images à utiliser pour toute la vidéo (minimum 2)
  IMAGES_PER_VIDEO: 10
  # Durée de la vidéo de secours silencieuse (en secondes)
  FALLBACK_DURATION_S: 15

# --- GESTION DES IMAGES (ImageManager) ---
IMAGE_MANAGER:
  CACHE_IMAGES: True
  CLEANUP_OLD_IMAGES: True
  # Nombre maximum d'images à conserver dans le répertoire /output/images
  MAX_IMAGES_TO_KEEP: 100 
  # Note: La résolution est prise depuis VIDEO_CREATOR

# --- GESTION YOUTUBE (YouTubeUploader) ---
YOUTUBE_UPLOADER:
  # Tags génériques appliqués à TOUTES les vidéos
  GLOBAL_TAGS: ["science", "technologie", "innovation", "faits", "Vaiatwork05"]
  # Visibilité par défaut: 'private', 'public', 'unlisted'
  VISIBILITY: "unlisted"
  # Catégorie YouTube ID (ex: Science & Technologie = 28)
  CATEGORY_ID: 28 

# --- SECRETS & CLÉS D'API ---
SECRETS:
  # Doit être récupéré de votre tableau de bord Unsplash (voir réponse précédente)
  UNSPLASH_API_KEY: ""
  # Clé nécessaire pour l'authentification OAuth2 (doit être configurée via .env ou Secrets)
  YOUTUBE_CLIENT_SECRET: "" 
