# content_factory/content_generator_daily.py
import random
from datetime import datetime, timedelta

class ContentGenerator:
    def __init__(self):
        self.base_topics = self.load_base_topics()
        self.daily_variations = self.generate_daily_variations()
    
    def load_base_topics(self):
        """Sujets de base organisés par catégories"""
        return {
            'science': [
                "L'ADN et la Génétique Moderne",
                "Les Mystères des Trous Noirs", 
                "L'Intelligence Artificielle Révolutionnaire",
                "Les Secrets du Cerveau Humain",
                "La Physique Quantique Expliquée",
                "Les Océans et le Changement Climatique",
                "Les Virus et le Système Immunitaire",
                "L'Énergie Nucléaire du Futur",
                "La Conquête Spatiale Moderne",
                "Les Superpouvoirs des Animaux"
            ],
            'technologie': [
                "La Révolution de l'IA Générative",
                "Les Ordinateurs Quantiques", 
                "La Réalité Virtuelle et Augmentée",
                "Les Véhicules Autonomes",
                "L'Internet des Objets Intelligents",
                "La Blockchain et les Cryptomonnaies",
                "La 5G et les Réseaux du Futur",
                "L'Impression 3D Médicale",
                "Les Smart Cities Intelligentes",
                "La Cybersécurité Moderne"
            ],
            'environnement': [
                "Les Énergies Renouvelables Innovantes",
                "La Biodiversité en Danger",
                "L'Agriculture du Futur",
                "La Gestion des Déchets Intelligente",
                "L'Eau : Ressource Précieuse",
                "Les Forêts et la Reforestation", 
                "L'Économie Circulaire",
                "Les Villes Vertes de Demain",
                "L'Alimentation Durable",
                "La Protection des Océans"
            ],
            'sante': [
                "Les Avancées Médicales Récents",
                "La Médecine Personnalisée",
                "Les Biotechnologies Révolutionnaires",
                "La Lutte contre le Cancer",
                "Le Microbiote Intestinal",
                "Les Thérapies Géniques",
                "La Longévité et le Vieillissement",
                "La Santé Mentale Moderne",
                "Les Vaccins du Futur",
                "La Chirurgie Robotique"
            ]
        }
    
    def get_daily_seed(self):
        """Génère une seed unique pour chaque jour"""
        today = datetime.now().strftime("%Y%m%d")
        return int(today)
    
    def get_video_slot_seed(self, slot_number):
        """Génère une seed unique pour chaque créneau vidéo"""
        today_seed = self.get_daily_seed()
        return today_seed + slot_number
    
    def generate_daily_variations(self):
        """Génère les variations quotidiennes"""
        seed = self.get_daily_seed()
        random.seed(seed)
        
        variations = {}
        categories = list(self.base_topics.keys())
        
        # Mélanger l'ordre des catégories pour la journée
        shuffled_categories = random.sample(categories, len(categories))
        
        for i, category in enumerate(shuffled_categories):
            # Sélectionner un sujet aléatoire dans la catégorie
            topic = random.choice(self.base_topics[category])
            
            # Générer des variations de titre
            title_variations = self.generate_title_variations(topic, category)
            
            variations[i] = {
                'category': category,
                'base_topic': topic,
                'titles': title_variations,
                'angle': self.generate_angle(category)
            }
        
        return variations
    
    def generate_title_variations(self, base_topic, category):
        """Génère des variations de titre pour un sujet"""
        prefixes = {
            'science': ["Découverte : ", "Science : ", "Innovation : ", "Révolution : "],
            'technologie': ["Tech : ", "Future : ", "Digital : ", "Innovation : "],
            'environnement': ["Écolo : ", "Durable : ", "Nature : ", "Planète : "],
            'sante': ["Santé : ", "Médecine : ", "Wellness : ", "Innovation : "]
        }
        
        suffixes = {
            'science': [" - La Vérité", " Révélé", " - Les Secrets", " Expliqué"],
            'technologie': [" - Le Futur", " Révolution", " - Les Tendances", " Moderne"],
            'environnement': [" - Solution", " - Avenir", " - Défi", " - Espoir"],
            'sante': [" - Révolution", " - Découverte", " - Avancée", " - Solution"]
        }
        
        category_prefixes = prefixes.get(category, ["", "", "", ""])
        category_suffixes = suffixes.get(category, ["", "", "", ""])
        
        variations = []
        for i in range(4):
            prefix = random.choice(category_prefixes)
            suffix = random.choice(category_suffixes)
            variations.append(f"{prefix}{base_topic}{suffix}")
        
        return variations
    
    def generate_angle(self, category):
        """Génère un angle d'approche pour le contenu"""
        angles = {
            'science': [
                "approche éducative et pédagogique",
                "angle découverte et innovation", 
                "perspective historique et évolution",
                "focus applications pratiques"
            ],
            'technologie': [
                "impact sur la société moderne",
                "innovations récentes et tendances",
                "comparaison technologies anciennes/nouvelles",
                "perspective futuriste"
            ],
            'environnement': [
                "solutions concrètes et actions",
                "impact sur la biodiversité",
                "innovations durables",
                "implication citoyenne"
            ],
            'sante': [
                "avancées médicales récentes",
                "conseils pratiques santé",
                "recherche scientifique",
                "témoignages et cas réels"
            ]
        }
        return random.choice(angles.get(category, ["angle informatif"]))
    
    def generate_script(self, base_topic, category, angle, slot_number):
        """Génère un script basé sur le sujet, catégorie et angle"""
        
        # Introduction variée selon le créneau
        introductions = [
            f"Aujourd'hui, explorons ensemble {base_topic.lower()}.",
            f"Plongeons dans l'univers fascinant de {base_topic.lower()}.",
            f"Découvrons les secrets de {base_topic.lower()}.",
            f"Partons à la découverte de {base_topic.lower()}."
        ]
        
        # Contenu principal avec variations
        content_templates = {
            'science': [
                f"La science derrière {base_topic.lower()} révèle des mécanismes extraordinaires. Les recherches récentes ont mis en lumière des aspects surprenants qui révolutionnent notre compréhension. {self.get_science_details(category)}",
                f"Les découvertes dans le domaine de {base_topic.lower()} transforment notre vision du monde. {self.get_science_impact(category)}"
            ],
            'technologie': [
                f"La technologie liée à {base_topic.lower()} évolue à une vitesse impressionnante. {self.get_tech_advancements(category)}",
                f"L'innovation dans {base_topic.lower()} ouvre des perspectives incroyables. {self.get_tech_future(category)}"
            ],
            'environnement': [
                f"L'enjeu de {base_topic.lower()} est crucial pour notre avenir. {self.get_environment_solutions(category)}",
                f"La protection de {base_topic.lower()} nécessite une action collective. {self.get_environment_actions(category)}"
            ],
            'sante': [
                f"Les avancées concernant {base_topic.lower()} transforment la médecine. {self.get_health_breakthroughs(category)}",
                f"La compréhension de {base_topic.lower()} améliore notre qualité de vie. {self.get_health_benefits(category)}"
            ]
        }
        
        introduction = introductions[slot_number % len(introductions)]
        main_content = random.choice(content_templates.get(category, [f"Le sujet de {base_topic.lower()} offre des perspectives fascinantes."]))
        
        # Conclusion adaptée
        conclusions = [
            "Cette exploration nous montre l'importance de continuer à rechercher et innover.",
            "Le futur s'annonce passionnant avec ces avancées remarquables.",
            "Restons curieux et ouverts à ces découvertes qui façonnent notre monde.",
            "Chaque progrès nous rapproche d'une compréhension plus complète de notre univers."
        ]
        
        conclusion = conclusions[slot_number % len(conclusions)]
        
        # Assembler le script
        script = f"{introduction}\n\n{main_content}\n\n{conclusion}"
        
        return script
    
    def get_science_details(self, category):
        """Détails scientifiques spécifiques"""
        details = {
            'science': "Les dernières études publiées dans des revues prestigieuses confirment l'importance de ces découvertes.",
            'technologie': "L'ingénierie de pointe permet des applications qui semblaient impossibles il y a quelques années.",
            'environnement': "Les données scientifiques récentes montrent l'urgence d'agir pour préserver notre écosystème.",
            'sante': "Les essais cliniques démontrent une efficacité prometteuse pour les traitements futurs."
        }
        return details.get(category, "Les recherches continuent de progresser à un rythme accéléré.")
    
    def get_science_impact(self, category):
        """Impact des découvertes scientifiques"""
        impacts = {
            'science': "Ces avancées pourraient bien révolutionner notre quotidien dans les prochaines années.",
            'technologie': "L'impact sur l'industrie et la société sera considérable.",
            'environnement': "Ces solutions pourraient sauver des écosystèmes entiers.",
            'sante': "Ces progrès pourraient sauver des millions de vies à travers le monde."
        }
        return impacts.get(category, "L'impact de ces découvertes dépasse nos attentes.")
    
    def get_tech_advancements(self, category):
        """Avancées technologiques"""
        advancements = {
            'science': "Les instruments de mesure deviennent de plus en plus précis.",
            'technologie': "Les processeurs atteignent des performances exceptionnelles.",
            'environnement': "Les capteurs permettent une surveillance en temps réel.",
            'sante': "Les dispositifs médicaux gagnent en précision et fiabilité."
        }
        return advancements.get(category, "L'innovation ouvre des possibilités insoupçonnées.")
    
    def get_tech_future(self, category):
        """Perspective future de la technologie"""
        futures = {
            'science': "Les laboratoires du futur seront entièrement automatisés.",
            'technologie': "L'intelligence artificielle va transformer tous les secteurs.",
            'environnement': "Les technologies vertes deviendront la norme.",
            'sante': "La médecine personnalisée sera accessible à tous."
        }
        return futures.get(category, "Le futur s'annonce passionnant avec ces innovations.")
    
    def get_environment_solutions(self, category):
        """Solutions environnementales"""
        solutions = {
            'science': "La recherche développe des solutions basées sur la nature.",
            'technologie': "Les technologies propres deviennent plus efficaces.",
            'environnement': "Les initiatives locales montrent des résultats prometteurs.",
            'sante': "Un environnement sain améliore directement la santé publique."
        }
        return solutions.get(category, "Des solutions existent et montrent leur efficacité.")
    
    def get_environment_actions(self, category):
        """Actions environnementales"""
        actions = {
            'science': "La science guide nos actions pour un impact maximal.",
            'technologie': "La tech nous donne les outils pour agir efficacement.",
            'environnement': "Chaque geste compte dans cette démarche collective.",
            'sante': "Protéger l'environnement, c'est protéger notre santé."
        }
        return actions.get(category, "L'action collective peut faire la différence.")
    
    def get_health_breakthroughs(self, category):
        """Percées médicales"""
        breakthroughs = {
            'science': "La recherche fondamentale ouvre de nouvelles voies thérapeutiques.",
            'technologie': "Les dispositifs médicaux révolutionnent les diagnostics.",
            'environnement': "Un environnement sain réduit les maladies chroniques.",
            'sante': "Les traitements deviennent plus ciblés et moins invasifs."
        }
        return breakthroughs.get(category, "La médecine progresse à un rythme impressionnant.")
    
    def get_health_benefits(self, category):
        """Bénéfices pour la santé"""
        benefits = {
            'science': "La compréhension des mécanismes biologiques s'améliore.",
            'technologie': "Le suivi médical devient plus accessible et précis.",
            'environnement': "La qualité de l'air et de l'eau influence directement la santé.",
            'sante': "La prévention permet d'éviter de nombreuses pathologies."
        }
        return benefits.get(category, "Ces avancées améliorent la qualité de vie de millions de personnes.")
    
    def generate_content(self, slot_number=0):
        """Génère le contenu pour un créneau spécifique"""
        # Réinitialiser les variations pour le jour
        self.daily_variations = self.generate_daily_variations()
        
        # Sélectionner la variation pour ce créneau
        variation_key = slot_number % len(self.daily_variations)
        variation = self.daily_variations[variation_key]
        
        # Générer le contenu final
        title = variation['titles'][slot_number % len(variation['titles'])]
        script = self.generate_script(
            variation['base_topic'], 
            variation['category'], 
            variation['angle'],
            slot_number
        )
        
        return {
            'title': title,
            'script': script,
            'category': variation['category'],
            'slot_number': slot_number,
            'daily_seed': self.get_daily_seed()
        }

# Fonction utilitaire pour générer 4 contenus
def generate_daily_contents():
    """Génère les 4 contenus de la journée"""
    generator = ContentGenerator()
    daily_contents = []
    
    for slot in range(4):
        content = generator.generate_content(slot)
        daily_contents.append(content)
    
    return daily_contents
