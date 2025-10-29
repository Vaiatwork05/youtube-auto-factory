# content_factory/config_loader.py

import os
import re
import yaml
import sys
from typing import Dict, Any, Optional

# Chemin vers le fichier de configuration (assumons qu'il est à la racine du projet)
CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.yaml')

# Regex pour identifier les placeholders de variables d'environnement: ${VARIABLE_NAME}
ENV_VAR_PATTERN = re.compile(r'\$\{([^}]+)\}')


class ConfigLoader:
    """
    Chargeur de configuration YAML (Singleton).
    Charge les paramètres depuis config.yaml une seule fois et interprète
    les variables d'environnement.
    """
    _instance = None
    _config: Optional[Dict[str, Any]] = None

    def __new__(cls):
        """Assure que seulement une instance de ConfigLoader est créée (Singleton)."""
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _interpret_env_vars(self, data: Any) -> Any:
        """
        Interprète récursivement les chaînes de caractères contenant des
        placeholders ${VARIABLE_NAME} avec les valeurs du système.
        """
        if isinstance(data, dict):
            return {k: self._interpret_env_vars(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._interpret_env_vars(i) for i in data]
        elif isinstance(data, str):
            match = ENV_VAR_PATTERN.search(data)
            if match:
                # Récupère le nom de la variable d'environnement
                var_name = match.group(1)
                # Récupère la valeur, ou lève une erreur si elle n'existe pas (pour les secrets critiques)
                env_value = os.getenv(var_name)
                
                if env_value is None:
                    # Pour les secrets critiques (ID, KEY), on force l'échec
                    if any(s in var_name for s in ['CLIENT_ID', 'SECRET', 'TOKEN']):
                        raise ValueError(f"❌ SECRET MANQUANT: La variable d'environnement {var_name} n'est pas définie. Impossible de procéder.")
                    # Pour les variables non critiques, on peut laisser la valeur originale ou un défaut
                    print(f"⚠️ AVERTISSEMENT: La variable d'environnement {var_name} n'est pas définie. Utilisant la chaîne de substitution.")
                    return data
                
                # Si la chaîne contient UNIQUEMENT le placeholder (ex: "CLIENT_ID: ${...}"),
                # on remplace par la valeur brute pour conserver les types (nombre, booléen) si le shell le permet.
                if data == match.group(0):
                    return env_value
                else:
                    # Si la chaîne contient du texte autour, on fait une substitution simple de la sous-chaîne
                    return data.replace(match.group(0), env_value)
            return data
        return data

    def _load_config(self):
        """Charge le fichier YAML et applique l'interprétation des variables."""
        print(f"🛠️ Chargement de la configuration depuis {CONFIG_FILE_PATH}...")
        
        if not os.path.exists(CONFIG_FILE_PATH):
            print(f"❌ Erreur: Fichier de configuration non trouvé à: {CONFIG_FILE_PATH}")
            sys.exit(1)

        try:
            with open(CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
                raw_config = yaml.safe_load(f)
            
            # Interpréter les variables d'environnement après le chargement
            self._config = self._interpret_env_vars
