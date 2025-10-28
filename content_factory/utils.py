# content_factory/utils.py
import re
import os

def clean_filename(filename):
    """
    Nettoie le nom de fichier pour enlever les caractères invalides
    """
    if not filename:
        return "default_file"
    
    # Remplacer les caractères problématiques
    invalid_chars = r'[<>:"/\\|?*\'\r\n]'
    cleaned = re.sub(invalid_chars, '_', filename)
    
    # Remplacer les espaces et caractères spéciaux
    cleaned = re.sub(r'[^\w\-_.]', '_', cleaned)
    
    # Supprimer les underscores multiples
    cleaned = re.sub(r'_+', '_', cleaned)
    
    # Supprimer les underscores au début et à la fin
    cleaned = cleaned.strip('_')
    
    # Si vide après nettoyage, utiliser un nom par défaut
    if not cleaned:
        cleaned = "default_file"
    
    # Limiter la longueur
    return cleaned[:100]

def safe_path_join(directory, filename):
    """
    Crée un chemin de fichier sécurisé
    """
    clean_dir = directory.strip('/\\')
    clean_file = clean_filename(filename)
    return os.path.join(clean_dir, clean_file)

def ensure_directory(path):
    """
    Crée un dossier s'il n'existe pas
    """
    os.makedirs(path, exist_ok=True)
    return path
