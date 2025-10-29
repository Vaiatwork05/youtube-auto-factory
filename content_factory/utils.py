# content_factory/utils.py

import re
import os
from typing import List, Union, Any

# Constantes de Regex
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\r\n\t]+')
TO_UNDERSCORE_CHARS = re.compile(r'[-\s]+')


def clean_filename(filename: str, max_length: int = 100) -> str:
    """Nettoie une chaîne pour un nom de fichier sûr et portable."""
    if not filename or not isinstance(filename, str):
        return "default_file"
    
    # 1. Remplacer les caractères invalides
    cleaned = INVALID_FILENAME_CHARS.sub('_', filename)
    
    # 2. Remplacer les séparateurs courants par un underscore unique
    cleaned = TO_UNDERSCORE_CHARS.sub('_', cleaned)
    
    # 3. Supprimer les underscores multiples
    cleaned = re.sub(r'_+', '_', cleaned)

    # 4. Supprimer les underscores et les points au début/fin
    cleaned = cleaned.strip('_.')
    
    if not cleaned:
        cleaned = "default_file"
    
    return cleaned[:max_length]


def safe_path_join(directory: str, filename: str) -> str:
    """Crée un chemin de fichier sécurisé."""
    clean_file = clean_filename(filename)
    return os.path.join(directory, clean_file)


def ensure_directory(path: str) -> str:
    """Crée un dossier et tous les dossiers parents nécessaires s'ils n'existent pas."""
    os.makedirs(path, exist_ok=True)
    return path


def clean_and_format_keywords(tags: Union[List[str], str, Any], max_tags: int = 20) -> List[str]:
    """Convertit une entrée en une liste de tags propres, uniques et limités."""
    if isinstance(tags, str):
        tag_list = re.split(r'[,\s;|]+', tags)
    elif isinstance(tags, list):
        tag_list = tags
    else:
        return []
    
    cleaned_tags = set()
    
    for tag in tag_list:
        tag = str(tag).strip().lower()
        if not tag:
            continue
        
        # Nettoyage: enlever les caractères non alpha-numériques sauf - et _
        tag = re.sub(r'[^\w\-_]+', '', tag)
        
        if tag:
            cleaned_tags.add(tag)
            
    return list(cleaned_tags)[:max_tags]

# --- Le bloc de test est omis ici pour la concision ---
