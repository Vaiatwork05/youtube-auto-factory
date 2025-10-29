# content_factory/content_generator.py (Intégration config.yaml)

import random
import sys
import re 
from datetime import datetime
from typing import Dict, List, Any, Optional
from content_factory.config_loader import ConfigLoader 

# --- DONNÉES STATIQUES DU CONTENU FILTRÉ et ÉLARGI ---
# Ces données définissent le contenu thématique
BASE_TOPICS = {
    'science': [
        "L'ADN et la Génétique : Les Bases", "Les Mystères des Trous Noirs et des Galaxies", 
        "Les Secrets de la Lumière et de l'Optique", "La Physique Quantique : Introduction",
        "La Création des Éléments Chimiques", "La Vie Extraterrestre : Recherche Scientifique",
        "Le Temps et l'Espace : La Théorie de la Relativité", "L'Origine de l'Univers et le Big Bang",
        "Les Superconducteurs et leurs Applications", "La Cristallographie et la Structure des Solides",
    ],
    'technologie': [
        "L'Intelligence Artificielle et le Machine Learning", "Les Innovations des Ordinateurs Quantiques", 
        "La Robotique et les Systèmes Autonomes", "La Réalité Virtuelle dans l'Éducation",
        "La 6G et le Futur des Réseaux Mobiles", "L'Éthique de la Technologie et de l'AI",
        "L'Impression 3D Industrielle", "Le Métavers et ses Applications Non Sociales",
        "Les Nanotechnologies et les Nano-Matériaux", "La Cryptographie Post-Quantique",
    ],
    'environnement': [
        "Les Énergies Renouvelables : Solaire et Éolien", "La Biodiversité et les Écosystèmes Terrestres",
        "L'Hydrologie et la Gestion de l'Eau", "La Géothermie : L'Énergie de la Terre",
        "La Reforestation par la Technologie", "Les Techniques de Dépollution des Océans", 
        "L'Agriculture Verticale et la Permaculture", "La Science des Matériaux Durables",
        "Le Stockage d'Énergie (Batteries et Piles à Combustible)", "La Modélisation Climatique : Les Bases",
    ],
    'espace': [
        "La Colonisation de Mars : Défis Techniques", "Les Prochaines Missions Spatiales (Artemis)",
        "Les Exoplanètes et la Zone Habitable", "Le Fonctionnement de la Station Spatiale Internationale",
        "Les Satellites et l'Observation Terrestre", "L'Histoire des Fusées et des Lanceurs",
        "Les Géantes Gazeuses : Jupiter et Saturne", "Les Astéroïdes et les Comètes : Composition",
        "Le Télescope Spatial James Webb (JWST) : Découvertes", "La Physique des Mouvements Stellaires",
    ],
    'sante_bienetre': [
        "Les Bases de la Nutrition Scientifique", "Le Fonctionnement du Sommeil et du Repos",
        "La Neuroplasticité et l'Apprentissage", "Les Bienfaits de l'Activité Physique sur le Cerveau",
        "Le Rôle du Microbiote Intestinal sur le Bien-être", "La Psychologie Positive et la Science du Bonheur",
        "La Prévention et les Bases de l'Immunologie", "Les Dernières Techniques d'Imagerie Médicale",
        "L'Horloge Biologique (Rythmes Circadiens)", "L'Impact de la Méditation sur le Cerveau",
    ]
}

# Modèles pour les variations de titre et d'angle
TITLE_TEMPLATES = {
    'prefixes': {
        'science': ["Découverte : ", "Science : ", "Innovation : ", "Révolution : "],
        'technologie': ["Tech : ", "Future : ", "Digital : ", "Innovation : "],
        'environnement': ["Écolo : ", "Durable : ", "Nature : ", "Planète : "],
        'espace': ["Espace : ", "Cosmos : ", "Mission : ", "Découverte : "],
        'sante_bienetre': ["Santé : ", "Bien-être : ", "Cerveau : ", "Science : "]
    },
    'suffixes': {
        'science': [" - La Vérité", " Révélé", " - Les Secrets", " Expliqué"],
        'technologie': [" - Le Futur", " Révolution", " - Les Tendances", " Moderne"],
        'environnement': [" - Solution", " - Avenir", " - Défi", " - Espoir"],
        'espace': [" - Les Secrets", " - Le Voyage", " - La Nouvelle Ère", " Expliqué"],
        'sante_bienetre': [" - Avancée", " - Solution", " - Les Bases", " Scientifique"],
    },
    'angles': {
        'science': ["approche éducative et pédagogique", "angle découverte et innovation", "perspective historique et évolution", "focus applications pratiques"],
        'technologie': ["impact sur la société moderne", "innovations récentes et tendances", "comparaison technologies anciennes/nouvelles", "perspective futuriste"],
        'environnement': ["solutions concrètes et actions", "impact sur la biodiversité", "innovations durables", "implication citoyenne"],
        # CORRECTION APPLIQUÉE ICI (ligne 70 de votre code initial)
        'espace': ["défis techniques et ingénierie", "découvertes astronomiques récentes", "perspective scientifique et hypothèses", "focus sur l'exploration humaine"],
        'sante_bienetre': ["bases scientifiques et études", "conseils pratiques pour le quotidien", "mécanismes biologiques et chimiques", "perspective d'amélioration de la qualité de vie"],
    }
}


class ContentGenerator:
    def __init__(self, base_topics: Dict = BASE_TOPICS):
        self.base_topics = base_topics
        self.config = ConfigLoader().get_config()
        self.daily_variations = self._generate_daily_variations()
        self.global_tags: List[str] = self.config['YOUTUBE_UPLOADER'].get('GLOBAL_TAGS', [])
    
    @staticmethod
    def get_daily_seed() -> int:
        return int(datetime.now().strftime("%Y%m%d"))
        
    def _generate_daily_variations(self) -> Dict[int, Dict[str, Any]]:
        """Génère un pool de sujets pour la journée, basé sur la seed quotidienne."""
        seed = self.get_daily_seed()
        random.seed(seed)
        variations = {}
        categories = list(self.base_topics.keys())
        
        num_slots = self.config['WORKFLOW'].get('DAILY_SLOTS', 4)
        
        # Choisir les catégories, puis un sujet unique par catégorie
        categories_for_day = random.sample(categories, min(num_slots, len(categories)))
        
        for i, category in enumerate(categories_for_day):
            topic = random.choice(self.base_topics[category])
            variations[i] = {
                'category': category,
                'base_topic': topic,
                'titles': self._generate_title_variations(topic, category),
                'angle': random.choice(TITLE_TEMPLATES['angles'].get(category, ["angle informatif"])),
                'daily_seed': seed
            }
        
        # Si moins de sujets que de slots, on répète les sujets aléatoirement
        if len(variations) < num_slots:
            original_variations = list(variations.values())
            for i in range(len(variations), num_slots):
                variations[i] = random.choice(original_variations)
                
        return variations
    
    def _generate_title_variations(self, base_topic: str, category: str) -> List[str]:
        """Crée plusieurs variations de titres pour augmenter le CTR."""
        prefixes = TITLE_TEMPLATES['prefixes'].get(category, [""])
        suffixes = TITLE_TEMPLATES['suffixes'].get(category, [""])
        variations = []
        # Générer 4 variations
        for _ in range(4): 
            prefix = random.choice(prefixes) if prefixes else ""
            suffix = random.choice(suffixes) if suffixes else ""
            variations.append(f"{prefix}{base_topic}{suffix}".strip())
        return variations
    
    def _get_script_detail(self, category: str, detail_type: str) -> str:
        # Détails du script (basés sur le code fourni)
        DETAILS_MAP = {
            'science': {
                'details': "Les dernières études confirment l'importance de ces découvertes.",
                'impacts': "Ces avancées pourraient bien révolutionner notre quotidien dans les prochaines années.",
            },
            'technologie': {
                'details': "La technologie évolue à une vitesse impressionnante. L'innovation ouvre des perspectives incroyables.",
                'impacts': "L'intelligence artificielle va transformer tous les secteurs.",
            },
            'environnement': {
                'details': "Les données scientifiques récentes montrent l'urgence d'agir pour préserver notre écosystème.",
                'impacts': "Ces solutions pourraient sauver des écosystèmes entiers.",
            },
            'espace': {
                'details': "Ce chapitre de l'exploration spatiale est riche en défis techniques.",
                'impacts': "L'exploration de l'espace nous apporte des innovations directement applicables sur Terre.",
            },
            'sante_bienetre': {
                'details': "La recherche fondamentale ouvre de nouvelles voies thérapeutiques et de bien-être.",
                'impacts': "Ces progrès améliorent la qualité de vie et la longévité de millions de personnes.",
            }
        }
        return DETAILS_MAP.get(category, {}).get(detail_type, "Des recherches continuent de progresser à un rythme accéléré.")
        
    def generate_script(self, base_topic: str, category: str, angle: str, slot_number: int) -> str:
        # La logique de génération du script reste identique pour maintenir l'auto-suffisance

        introductions = [
            f"Aujourd'hui, explorons ensemble **{base_topic.lower()}**.",
            f"Plongeons dans l'univers fascinant de **{base_topic.lower()}**.",
            f"Découvrons les secrets de **{base_topic.lower()}**.",
            f"Partons à la découverte de **{base_topic.lower()}**."
        ]
        conclusions = [
            "Cette exploration nous montre l'importance de continuer à rechercher et innover.",
            "Le futur s'annonce passionnant avec ces avancées remarquables.",
            "Restons curieux et ouverts à ces découvertes qui façonnent notre monde.",
            "Chaque progrès nous rapproche d'une compréhension plus complète de notre univers."
        ]
        
        main_content_templates = {
            'science': [f"La science derrière {base_topic.lower()} révèle des mécanismes extraordinaires. ({self._get_script_detail('science', 'details')})",],
            'technologie': [f"Les défis techniques de {base_topic.lower()} sont immenses. ({self._get_script_detail('technologie', 'details')})",],
            'environnement': [f"L'enjeu de l'environnement est crucial pour notre avenir. ({self._get_script_detail('environnement', 'details')})",],
            'espace': [f"Ce chapitre de l'exploration spatiale est riche en découvertes. ({self._get_script_detail('espace', 'details')})",],
            'sante_bienetre': [f"Les bases scientifiques du bien-être sont primordiales. ({self._get_script_detail('sante_bienetre', 'details')})",],
        }
        
        main_content = random.choice(main_content_templates.get(category, 
                                                               [f"Le sujet de {base_topic.lower()} offre des perspectives fascinantes et est traité sous l'angle de **{angle}**."]))

        introduction = introductions[slot_number % len(introductions)]
        conclusion = conclusions[slot_number % len(conclusions)]
        
        script = f"{introduction}\n\n{main_content}\n\n{conclusion}"
        
        return script
    
    def _generate_keywords(self, base_topic: str, category: str) -> List[str]:
        """Génère des mots-clés pour l'ImageManager et le YouTubeUploader."""
        
        # Nettoyer le sujet de base (enlever les articles, les verbes d'état, les symboles)
        cleaned_topic = re.sub(r'[\'":\s]+', ' ', base_topic).strip()
        cleaned_topic = re.sub(r'\b(l\'|la|le|les|des|du|un|une|et|à|de|en|aux|avec|sur|ou|par|dans|qui|que)\b', '', cleaned_topic, flags=re.IGNORECASE).strip()
        
        # Mots-clés basés sur le sujet et la catégorie
        topic_tags = [tag.strip() for tag in cleaned_topic.split() if len(tag) > 3]
        
        # Mots-clés spécifiques à la catégorie
        category_tags = {
            'science': ['science', 'recherche', 'découverte', 'innovation'],
            'technologie': ['tech', 'futur', 'numérique', 'ia', 'robotique'],
            'environnement': ['nature', 'écologie', 'durable', 'planète', 'climat'],
            'espace': ['cosmos', 'astronomie', 'univers', 'exploration', 'nasa'],
            'sante_bienetre': ['santé', 'bienêtre', 'corps', 'cerveau', 'science'],
        }.get(category, [])
        
        # Mots-clés longs (pour le SEO)
        long_tags = [base_topic, category]
        
        # Suppression des doublons et application des tags globaux
        all_tags = list(set(topic_tags + category_tags + long_tags + self.global_tags))
        
        # Limiter à 15 tags pour Youtube
        return all_tags[:15]

    def generate_content(self, slot_number: int) -> Dict[str, Any]:
        """Produit le dictionnaire de contenu complet pour un créneau donné."""
        
        num_variations = len(self.daily_variations)
        if num_variations == 0:
            # Devrait jamais arriver si BASE_TOPICS n'est pas vide
            raise RuntimeError("Aucun sujet n'a pu être généré à partir des thèmes de base.")

        # Utiliser l'index du slot pour sélectionner le sujet du jour
        variation_key = slot_number % num_variations
        variation = self.daily_variations[variation_key]
        
        title = variation['titles'][slot_number % len(variation['titles'])]
        
        script = self.generate_script(
            variation['base_topic'], 
            variation['category'], 
            variation['angle'],
            slot_number
        )
        
        keywords = self._generate_keywords(variation['base_topic'], variation['category'])
        
        # La description YouTube est basée sur le script + un appel à l'action
        description = f"{script.replace('**', '')}\n\n---\n\nExplorez la science, la technologie, l'environnement et l'espace avec nous ! Abonnez-vous pour plus de découvertes fascinantes."
        
        return {
            'title': title,
            'script': script,
            'description': description, # NOUVEAU
            'keywords': keywords, # NOUVEAU
            'category': variation['category'],
            'slot_number': slot_number,
            'daily_seed': variation['daily_seed']
        }

# --- Fonction principale d'Export ---
def generate_daily_contents() -> List[Dict[str, Any]]:
    """Génère le nombre de contenus définis dans la configuration."""
    try:
        config = ConfigLoader().get_config()
        # Lire DAILY_SLOTS avec une valeur par défaut de 4 si la clé est manquante
        num_slots = config['WORKFLOW'].get('DAILY_SLOTS', 4) 
        
        generator = ContentGenerator()
        daily_contents = [generator.generate_content(slot) for slot in range(num_slots)]
        
        return daily_contents
    except Exception as e:
        print(f"❌ Erreur critique dans generate_daily_contents: {e}", file=sys.stderr)
        return []

# --- Bloc de Test ---
if __name__ == "__main__":
    print("🧪 Test ContentGenerator...")
    try:
        contents = generate_daily_contents()
        if not contents:
            print("❌ Test échoué: Aucune donnée générée.")
            sys.exit(1)
            
        print(f"✅ {len(contents)} Contenus générés pour la journée.")
        for content in contents:
            print("-" * 50)
            print(f"Créneau {content['slot_number'] + 1} | Catégorie: {content['category'].upper()}")
            print(f"Titre: {content['title']}")
            print(f"Mots-clés: {content['keywords']}")
            
            # Vérification critique pour le ImageManager
            if not content.get('keywords') or len(content['keywords']) < 3:
                 print("⚠️ Avertissement: Moins de 3 mots-clés générés.")
                 sys.exit(1)
                 
    except Exception as e:
        print(f"❌ Test échoué avec erreur: {e}")
        sys.exit(1)
