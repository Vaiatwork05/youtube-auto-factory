# content_factory/config_loader.py (Mise à jour avec support .env)

import os
import re
import yaml
import sys
from typing import Dict, Any, Optional

# NOUVEL IMPORT
from dotenv import load_dotenv

# Chemins
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE_PATH = os.path.join(SCRIPT_DIR, '..', 'config.yaml')
ENV_FILE_PATH = os.path.join(SCRIPT_DIR, '..', '.env') # Chemin du fichier .env

# Regex
ENV_VAR_PATTERN = re.compile(r'\$\{([^}]+)\}')


class ConfigLoader:
    # ... (Le reste du code reste le même, notamment _instance et _config) ...
    _instance = None
    _config: Optional[Dict[str, Any]] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            # NOUVELLE ÉTAPE : Charger les variables .env en premier
            if os.path.exists(ENV_FILE_PATH):
                print(f"🛠️ Chargement des variables locales depuis {ENV_FILE_PATH}...")
                load_dotenv(ENV_FILE_PATH, override=True) # override=True écrase les variables existantes
            
            cls._instance._load_config()
        return cls._instance

    # ... (Le reste des méthodes (_interpret_env_vars, _load_config, get_config) est inchangé) ...
    # Le _load_config continue de faire l'interprétation des ${VARIABLE} en utilisant os.getenv,
    # qui contient maintenant les valeurs du .env.
    
    # NOTE: Pour les secrets YouTube (YOUTUBE_CLIENT_ID, etc.), GitHub Actions les injectera
    # en écrasant les valeurs éventuelles du .env, garantissant que la production utilise
    # toujours les secrets sécurisés et non les valeurs locales.
    pass

# --- Le bloc de test est omis ici pour la concision ---
