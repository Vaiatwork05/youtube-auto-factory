# content_factory/utils.py
import re
import os
from typing import List, Union, Any

# Constante pour les caractères invalides dans un nom de fichier standard (Windows/Unix)
# Caractères invalides classiques: < > : " / \ | ? *
# Plus les caractères de contrôle et les points au début/fin (souvent cachés ou problématiques)
INVALID_FILENAME_CHARS = re.compile(r'[<>:"/\\|?*\r\n\t]+')
# Caractères à convertir en underscore (espaces, traits d'union non désirés, caractères spéciaux)
TO_UNDERSCORE_CHARS = re.compile(r'[-\s]+')


def clean_filename(filename: str, max_length: int = 100) -> str:
    """
    Nettoie une chaîne de caractères pour un nom de fichier sûr et portable.

    Args:
        filename: La chaîne originale à nettoyer.
        max_length: Longueur maximale du nom de fichier (par défaut 100).

    Returns:
        Le nom de fichier nettoyé.
    """
    if not filename or not isinstance(filename, str):
        return "default_file"
    
    # ÉTAPE 1: Remplacer les caractères invalides par un underscore
    cleaned = INVALID_FILENAME_CHARS.sub('_', filename)
    
    # ÉTAPE 2: Remplacer les espaces et autres séparateurs courants par un underscore unique
    cleaned = TO_UNDERSCORE_CHARS.sub('_', cleaned)
    
    # ÉTAPE 3: Supprimer les underscores multiples consécutifs (optimisation de votre logique)
    # Note: On conserve un seul underscore entre les mots
    cleaned = re.sub(r'_+', '_', cleaned)

    # ÉTAPE 4: Supprimer les underscores et les points au début/fin (pour éviter les fichiers cachés)
    cleaned = cleaned.strip('_.')
    
    # Si vide après nettoyage, utiliser un nom par défaut
    if not cleaned:
        cleaned = "default_file"
    
    # Limiter la longueur
    return cleaned[:max_length]


def safe_path_join(directory: str, filename: str) -> str:
    """
    Crée un chemin de fichier sécurisé en nettoyant le nom du fichier.

    Args:
        directory: Le chemin du dossier (peut contenir des / ou \).
        filename: Le nom de fichier, nettoyé par clean_filename.

    Returns:
        Le chemin complet sécurisé.
    """
    # Pas besoin de striper le directory si on utilise os.path.join correctement
    clean_file = clean_filename(filename)
    return os.path.join(directory, clean_file)


def ensure_directory(path: str) -> str:
    """
    Crée un dossier et tous les dossiers parents nécessaires s'ils n'existent pas.
    
    Args:
        path: Le chemin du dossier à créer.

    Returns:
        Le chemin du dossier créé.
    """
    os.makedirs(path, exist_ok=True)
    return path


def clean_and_format_keywords(tags: Union[List[str], str, Any], max_tags: int = 20) -> List[str]:
    """
    Convertit une entrée (liste ou chaîne) en une liste de tags propres,
    en supprimant les doublons et en nettoyant les caractères.

    Args:
        tags: La liste de tags ou une chaîne de tags séparés par des virgules.
        max_tags: Nombre maximal de tags à retourner.

    Returns:
        Une liste de chaînes de caractères représentant des tags propres et uniques.
    """
    if isinstance(tags, str):
        # Séparer par virgules, espaces ou autres séparateurs courants
        tag_list = re.split(r'[,\s;|]+', tags)
    elif isinstance(tags, list):
        tag_list = tags
    else:
        return []
    
    cleaned_tags = set() # Utiliser un ensemble pour l'unicité
    
    for tag in tag_list:
        tag = str(tag).strip().lower()
        if not tag:
            continue
        
        # Nettoyage simple: enlever les caractères non alpha-numériques sauf - et _
        tag = re.sub(r'[^\w\-_]+', '', tag)
        
        if tag:
            cleaned_tags.add(tag)
            
    # Convertir en liste et limiter le nombre
    return list(cleaned_tags)[:max_tags]

# --- Bloc de Test (Non présent dans le fichier final, mais utile ici) ---
if __name__ == "__main__":
    print("🧪 Test des Utils...")
    
    # Test clean_filename
    test_name = "Mon Titre: Génial / Super * ?"
    cleaned = clean_filename(test_name)
    print(f"Clean Filename ('{test_name}') -> '{cleaned}' (Attendu: Mon_Titre_Genial_Super_)" )
    
    # Test safe_path_join
    path_join = safe_path_join("output/videos/", test_name)
    print(f"Safe Path Join -> '{path_join}' (Attendu: output/videos/Mon_Titre_Genial_Super_...)")
    
    # Test clean_and_format_keywords
    test_tags = ["Science", "IA ", "Automatique, ", "IA", "Quantum-Computing"]
    cleaned_tags = clean_and_format_keywords(test_tags)
    print(f"Clean Tags ({test_tags}) -> {cleaned_tags} (Attendu: ['science', 'ia', 'automatique', 'quantum-computing'])")
    
    test_string_tags = "Physique, Espace, Big Bang | Astronomie"
    cleaned_string_tags = clean_and_format_keywords(test_string_tags)
    print(f"Clean String Tags ('{test_string_tags}') -> {cleaned_string_tags}")

