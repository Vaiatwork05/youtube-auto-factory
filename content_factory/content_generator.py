import random
import requests

class ContentGenerator:
    def __init__(self):
        self.science_topics = [
            {
                "title": "Le Mystère des Trous Noirs",
                "script": "Les trous noirs sont des régions de l'espace où la gravité est si intense que même la lumière ne peut s'en échapper. Ils se forment lorsque des étoiles massives s'effondrent sur elles-mêmes à la fin de leur vie.",
                "tags": ["science", "espace", "astronomie", "trous noirs"]
            },
            {
                "title": "L'ADN : Code de la Vie", 
                "script": "L'ADN contient les instructions génétiques qui font de vous un être unique. Cette molécule en double hélice se trouve dans chaque cellule de votre corps et détermine tout, de votre couleur des yeux à votre prédisposition à certaines maladies.",
                "tags": ["science", "adn", "génétique", "biologie"]
            },
            {
                "title": "Pourquoi le Ciel est Bleu ?",
                "script": "La lumière du soleil est blanche, mais en traversant l'atmosphère terrestre, elle entre en collision avec les molécules d'air. La lumière bleue, plus courte, est dispersée dans toutes les directions, donnant au ciel sa couleur caractéristique.",
                "tags": ["science", "ciel", "lumière", "physique"]
            },
            {
                "title": "Les Superpouvoirs des Abeilles",
                "script": "Les abeilles peuvent reconnaître les visages humains, danser pour communiquer la localisation des fleurs, et leur système de navigation est si précis qu'elles retrouvent toujours leur ruche.",
                "tags": ["science", "abeilles", "nature", "insectes"]
            }
        ]
    
    def generate_script(self):
        """Génère un script scientifique aléatoire"""
        topic = random.choice(self.science_topics)
        
        return {
            "title": topic["title"],
            "script": topic["script"],
            "tags": topic["tags"],
            "description": f"{topic['script'][:100]}... #science #éducation #facts"
        }

# Test
if __name__ == "__main__":
    generator = ContentGenerator()
    script = generator.generate_script()
    print("📝 Script généré:", script)
