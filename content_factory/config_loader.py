# content_factory/config_loader.py

import yaml
import os
import sys

# La classe utilise le modèle Singleton pour ne charger le fichier qu'une seule fois.
class ConfigLoader:
    _config = None
    
    # Constante pour le chemin du fichier config.yaml
    # Le chemin est construit par rapport au répertoire courant du script Python.
    _config_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'config.yaml' # Assurez-vous que config.yaml est dans le répertoire 'app/'
    )

    def __init__(self):
        # Ligne 8 (la ligne critique où l'erreur apparaissait) est maintenant ici, 
        # elle est traitée dans un contexte de code valide (début de fonction).
        if ConfigLoader._config is None:
            self._load_config()

    def _load_config(self):
        """Charge le fichier YAML depuis le chemin spécifié."""
        try:
            # Tente d'ouvrir et de lire le fichier
            with open(self._config_path, 'r', encoding='utf-8') as f:
                ConfigLoader._config = yaml.safe_load(f)
                
            if ConfigLoader._config is None:
                # Gère le cas où le fichier est vide
                ConfigLoader._config = {}
                
        except FileNotFoundError:
            print(f"❌ Erreur: Le fichier de configuration 'config.yaml' est introuvable au chemin : {self._config_path}", file=sys.stderr)
            sys.exit(1) # Arrêt du programme si la configuration n'est pas trouvée
        except yaml.YAMLError as e:
            # Gère les erreurs de syntaxe dans le fichier YAML (s'il est mal formaté)
            print(f"❌ Erreur: Le fichier 'config.yaml' est mal formaté (YAML Error: {e})", file=sys.stderr)
            sys.exit(1)

    def get_config(self):
        """Retourne le dictionnaire de configuration chargé."""
        return ConfigLoader._config

# --- Bloc de Test ---
if __name__ == "__main__":
    print("🧪 Test ConfigLoader...")
    try:
        config = ConfigLoader().get_config()
        print("✅ ConfigLoader chargé avec succès.")
        print(f"  -> Nombre de slots quotidiens: {config.get('WORKFLOW', {}).get('DAILY_SLOTS')}")
    except Exception as e:
        print(f"❌ Test échoué avec erreur: {e}", file=sys.stderr)
