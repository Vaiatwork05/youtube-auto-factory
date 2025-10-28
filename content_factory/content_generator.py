import requests
import random

def generate_science_script():
    """Génère un script scientifique simple"""
    topics = [
        "Pourquoi le ciel est bleu ? La lumière du soleil est dispersée par l'atmosphère...",
        "Les trous noirs : des monstres cosmiques qui dévorent tout, même la lumière...",
        "L'ADN : le code secret de la vie qui se trouve dans chaque cellule...",
        "Les atomes : les briques fondamentales de tout ce qui existe dans l'univers..."
    ]
    
    title = f"Science Fact #{random.randint(1000, 9999)}"
    script = random.choice(topics)
    
    return title, script

print("✅ Content Generator prêt !")
