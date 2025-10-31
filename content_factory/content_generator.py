# content_factory/content_generator.py (VERSION BRAINROT TOP 10)

import random
import sys
import re 
from datetime import datetime
from typing import Dict, List, Any, Optional
from content_factory.config_loader import ConfigLoader 

# --- DONNÉES STATIQUES OPTIMISÉES POUR TOP 10 ---
TOP_10_TOPICS = {
    'science': [
        "SECRETS CHOCS DE LA SCIENCE QUE PERSONNE NE CONNAÎT",
        "DÉCOUVERTES SCIENTIFIQUES QUI VONT TOUT CHANGER",
        "INVENTIONS RÉVOLUTIONNAIRES QUI VONT BOULEVERSER NOTRE VIE",
        "PHÉNOMÈNES NATURELS LES PLUS FOUS DE LA PLANÈTE",
        "THÉORIES SCIENTIFIQUES QUI DEFIENT LA LOGIQUE",
        "EXPÉRIENCES LES PLUS DANGEREUSES DE L'HISTOIRE",
        "MIRACLES MÉDICAUX QUE LA SCIENCE NE PEUT EXPLIQUER",
        "PROPHÉTIES TECHNOLOGIQUES QUI SE RÉALISENT",
        "MYSTÈRES DE L'UNIVERS QUI RESTENT INEXPLIQUÉS",
        "INVENTIONS ACCIDENTELLES DEVENUES RÉVOLUTIONNAIRES"
    ],
    'technologie': [
        "GADGETS TECHNOLOGIQUES LES PLUS FOUS DE 2024",
        "INNOVATIONS TECH QUI VONT RENDRE VOS APPAREILS OBSOLÈTES",
        "SECRETS DES GÉANTS DE LA TECH QU'ILS CACHENT AU PUBLIC",
        "PRÉDICTIONS TECHNOLOGIQUES QUI VONT VOUS CHOQUER",
        "INVENTIONS QUI VONT CHANGER LE MONDE D'ICI 2030",
        "HACKS TECHNOLOGIQUES QUE SEULS LES PROS CONNAISSENT",
        "APPAREILS DU FUTUR DÉJÀ EN TEST SECRET",
        "RÉVÉLATIONS SUR L'IA QUI VONT VOUS EFFRAYER",
        "TECHNOLOGIES MILITAIRES CLASSÉES SECRET DÉFENSE",
        "INVENTIONS BIZARRES QUI ONT RAPPORTÉ DES MILLIONS"
    ],
    'sante_bienetre': [
        "SECRETS DE MÉDECINS QUE VOUS NE DEVEZ PAS IGNORER",
        "HABITUDES QUI DÉTRUISENT VOTRE SANTÉ SANS QUE VOUS LE SACHIEZ",
        "SUPER-ALIMENTS QUI GUÉRISSENT VRAIMENT",
        "MENTIRES DE L'INDUSTRIE PHARMACEUTIQUE RÉVÉLÉES",
        "MÉTHODES ANTI-ÂGE QUE LES CÉLÉBRITÉS CACHENT",
        "POISONS QUOTIDIENS DANS VOTRE ALIMENTATION",
        "TECHNIQUES DE GUÉRISON QUE LA MÉDECINE REFUSE",
        "SIGNES QUE VOTRE CORPS ENVOIE ET QUE VOUS IGNOREZ",
        "COMPLÉMENTS ALIMENTAIRES QUI FONCTIONNENT VRAIMENT",
        "SECRETS POUR VIVRE JUSQU'À 100 ANS EN BONNE SANTÉ"
    ],
    'psychologie': [
        "SIGNES QUE QUELQU'UN VOUS MANIPULE EN CE MOMENT",
        "TECHNIQUES DE PERSUASION UTILISÉES PAR LES PROS",
        "SECRETS DU CERVEAU QUE LA SCIENCE VIENT DE DÉCOUVRIR",
        "HABITUDES QUI DÉTRUISENT VOTRE MENTAL À VOTRE INSU",
        "POUVOIRS MENTAUX QUE VOUS POSSÉDEZ SANS LE SAVOIR",
        "SIGNES CACHÉS DU LANGAGE CORPOREL QUI TRAHISSENT TOUT",
        "TRAUMAS SECRETS QUI CONTRÔLENT VOS DÉCISIONS",
        "ILLUSIONS MENTALES QUI VOUS TROMPENT QUOTIDIENNEMENT",
        "SECRETS POUR LIRE DANS LES PENSÉES DES GENS",
        "MÉTHODES POUR EFFACER LES MAUVAIS SOUVENIRS"
    ],
    'argent_business': [
        "SECRETS POUR DEVENIR RICHE QUE LES MILLIONNAIRES CACHENT",
        "ERREURS FINANCIÈRES QUI VOUS EMPÊCHENT DE VOUS ENRICHIR",
        "MÉTHODES POUR GAGNER DE L'ARGENT PENDANT VOTRE SOMMEIL",
        "INVESTISSEMENTS QUI ONT RAPPORTÉ 1000% EN 1 AN",
        "SECRETS DES STARTUPS QUI ONT RAPPORTÉ DES MILLIONS",
        "HABITUDES DES GENS RICHES QUE VOUS POUVEZ COPIER",
        "ARNAQUES FINANCIÈRES DONT VOUS ÊTES VICTIME",
        "CRYPTOS QUI VONT EXPLOSER EN 2024",
        "BUSINESS EN LIGNE QUI MARCHENT VRAIMENT EN 2024",
        "SECRETS POUR NÉGOCIER DES SALAIRES DE FOU"
    ]
}

# --- PHRASES ACCROCHE POUR LES TOP 10 ---
BRAINROT_PHRASES = {
    'intros': [
        "🚨 ATTENTION ! Ce que vous allez découvrir va totalement vous choquer...",
        "💀 Ce top 10 va vous retourner le cerveau, vous n'êtes pas prêts !",
        "🔥 Ce que nous allons révéler dans cette vidéo est absolument interdit...",
        "⚠️ Les autorités ne veulent pas que vous voyiez ce contenu...",
        "🎯 Ce top 10 va changer votre vie à jamais, regardez jusqu'au bout !",
        "💥 Ce que vous allez voir va vous faire remettre en question toute votre existence...",
        "🔞 Contenu sensible : ce top 10 contient des vérités qui dérangent...",
        "⚡ Prévenez vos amis, ce top 10 va faire exploser Internet !",
        "🧠 Ce que vous allez découvrir va vous rendre plus intelligent instantanément...",
        "💸 Ce top 10 va vous apprendre à devenir riche, ne le ratez pas !"
    ],
    'transitions': [
        "Mais avant de passer au point suivant, likez la vidéo si vous êtes choqué !",
        "Ce point est incroyable, mais attendez de voir la suite...",
        "Vous pensez avoir tout vu ? Vous n'êtes pas au bout de vos surprises !",
        "Commentez 'CHOC' si vous ne vous y attendiez pas du tout !",
        "Ce point va faire débat dans les commentaires, j'en suis sûr !",
        "Vous allez halluciner quand vous verrez le point suivant...",
        "Mais ce n'est rien comparé à ce qui arrive après...",
        "Likez si vous voulez connaître le point numéro 1 tout de suite !",
        "Ce point est déjà fou, mais le prochain va vous détruire !",
        "Abonnez-vous pour ne pas rater le point qui va tout changer !"
    ],
    'cliffhangers': [
        "Le point numéro 1 va vous retourner le cerveau, mais vous le verrez dans la partie 2 !",
        "Le meilleur est à venir dans la partie 2, vous n'êtes pas prêts !",
        "Le point numéro 1 est tellement choquant qu'il mérite sa propre vidéo !",
        "La suite de ce top 10 va vous détruire, cliquez sur la partie 2 maintenant !",
        "Le numéro 1 va vous faire halluciner, ne manquez pas la partie 2 !",
        "Le point final est tellement incroyable qu'on lui consacre une vidéo entière !",
        "Vous voulez connaître le point le plus choquant ? C'est dans la partie 2 !",
        "Le numéro 1 va tout changer, regardez la partie 2 immédiatement !",
        "Le point ultime est tellement fort qu'il nécessite une vidéo séparée !",
        "La révélation finale va vous exploser à la figure dans la partie 2 !"
    ],
    'cta_part2': [
        "📺 CLIQUEZ MAINTENANT SUR LA PARTIE 2 POUR LA SUITE CHOQUANTE !",
        "🔥 LA PARTIE 2 VA VOUS DÉTRUIRE, NE LA MANQUEZ PAS !",
        "🚨 LA RÉVÉLATION FINALE EST DANS LA PARTIE 2, CLIQUEZ !",
        "💀 LE POINT NUMÉRO 1 EST TELLEMENT FOU QU'IL EST DANS LA PARTIE 2 !",
        "⚡ VOUS VOULEZ SAVOIR LE MEILLEUR ? C'EST DANS LA PARTIE 2 !",
        "🎯 LA SUITE VA VOUS CHOQUER, CLIQUEZ SUR LA PARTIE 2 !",
        "💥 LE POINT ULTIME VOUS ATTEND DANS LA PARTIE 2 !",
        "🧠 LA RÉVÉLATION FINALE EST TELLEMENT INCROYABLE QU'ELLE EST DANS LA PARTIE 2 !",
        "💸 LE SECRET ULTIME POUR DEVENIR RICHE EST DANS LA PARTIE 2 !",
        "🔞 LE CONTENU LE PLUS SENSIBLE EST DANS LA PARTIE 2, CLIQUEZ !"
    ]
}

class ContentGenerator:
    def __init__(self, base_topics: Dict = TOP_10_TOPICS):
        self.base_topics = base_topics
        self.config = ConfigLoader().get_config()
        self.daily_variations = self._generate_daily_variations()
        self.global_tags: List[str] = self.config['YOUTUBE_UPLOADER'].get('GLOBAL_TAGS', [])
    
    @staticmethod
    def get_daily_seed() -> int:
        return int(datetime.now().strftime("%Y%m%d"))
        
    def _generate_daily_variations(self) -> Dict[int, Dict[str, Any]]:
        """Génère 2 sujets TOP 10 pour la journée (un pour chaque paire de vidéos)."""
        seed = self.get_daily_seed()
        random.seed(seed)
        
        num_slots = self.config['WORKFLOW'].get('DAILY_SLOTS', 4)
        variations = {}
        
        # Sélectionner 2 catégories différentes pour la journée
        categories = list(self.base_topics.keys())
        selected_categories = random.sample(categories, min(2, len(categories)))
        
        # Premier sujet TOP 10 (slots 0 et 1)
        topic1 = random.choice(self.base_topics[selected_categories[0]])
        variations[0] = {
            'category': selected_categories[0],
            'base_topic': topic1,
            'is_part1': True,
            'daily_seed': seed
        }
        variations[1] = {
            'category': selected_categories[0],
            'base_topic': topic1,
            'is_part1': False,
            'daily_seed': seed
        }
        
        # Deuxième sujet TOP 10 (slots 2 et 3) si nécessaire
        if num_slots > 2:
            topic2 = random.choice(self.base_topics[selected_categories[1]])
            variations[2] = {
                'category': selected_categories[1],
                'base_topic': topic2,
                'is_part1': True,
                'daily_seed': seed
            }
            variations[3] = {
                'category': selected_categories[1],
                'base_topic': topic2,
                'is_part1': False,
                'daily_seed': seed
            }
        
        return variations
    
    def _generate_brainrot_title(self, base_topic: str, category: str, is_part1: bool, slot_number: int) -> str:
        """Génère des titres putaclics optimisés algorithme."""
        
        part_indicators = {
            True: ["(PARTIE 1)", "(TOP 10-6)", "(PREMIÈRE PARTIE)", "(DÉBUT CHOQUANT)"],
            False: ["(PARTIE 2)", "(TOP 5-1)", "(SUITE EXPLOSIVE)", "(FIN INCROYABLE)"]
        }
        
        emoji_combos = ["🚨", "💀", "🔥", "⚠️", "🎯", "💥", "🔞", "⚡", "🧠", "💸"]
        
        title_templates_part1 = [
            f"{random.choice(emoji_combos)}TOP 10 {base_topic} {random.choice(part_indicators[True])}",
            f"{random.choice(emoji_combos)}LES 10 {base_topic} {random.choice(part_indicators[True])}",
            f"{random.choice(emoji_combos)}10 {base_topic} QUI VONT VOUS CHOQUER {random.choice(part_indicators[True])}",
            f"{random.choice(emoji_combos)}DÉCOUVREZ LES 10 {base_topic} {random.choice(part_indicators[True])}"
        ]
        
        title_templates_part2 = [
            f"{random.choice(emoji_combos)}LE MEILLEUR ARRIVE ! {base_topic} {random.choice(part_indicators[False])}",
            f"{random.choice(emoji_combos)}LA SUITE CHOQUANTE ! {base_topic} {random.choice(part_indicators[False])}",
            f"{random.choice(emoji_combos)}VOUS N'ÊTES PAS PRÊTS ! {base_topic} {random.choice(part_indicators[False])}",
            f"{random.choice(emoji_combos)}LA RÉVÉLATION FINALE ! {base_topic} {random.choice(part_indicators[False])}"
        ]
        
        templates = title_templates_part1 if is_part1 else title_templates_part2
        return random.choice(templates)
    
    def _generate_top10_points(self, category: str, base_topic: str, is_part1: bool) -> List[str]:
        """Génère les points du TOP 10 selon la partie."""
        
        # Points génériques adaptables à toutes les catégories
        all_points = [
            "La révélation secrète que les experts cachent au public",
            "L'astuce incroyable que seuls les initiés connaissent", 
            "Le phénomène bizarre que la science ne peut expliquer",
            "La technique révolutionnaire qui change toutes les règles",
            "Le secret choquant qui va vous faire tout remettre en question",
            "La découverte accidentelle devenue révolutionnaire",
            "La méthode interdite qui fonctionne vraiment",
            "La vérité cachée que personne n'ose révéler",
            "Le hack génial qui va vous simplifier la vie",
            "La révélation ultime qui va tout changer"
        ]
        
        if is_part1:
            # Points 10 à 6 (accrocheurs mais pas les meilleurs)
            return all_points[5:10]  # Points 10 à 6
        else:
            # Points 5 à 1 (les meilleurs pour la fin)
            return all_points[0:5]   # Points 5 à 1
    
    def generate_script(self, base_topic: str, category: str, is_part1: bool, slot_number: int) -> str:
        """Génère un script brainrot ultra-optimisé pour la rétention."""
        
        points = self._generate_top10_points(category, base_topic, is_part1)
        script_lines = []
        
        # INTRODUCTION EXPLOSIVE
        script_lines.append(random.choice(BRAINROT_PHRASES['intros']))
        script_lines.append("")
        
        # POINTS DU TOP 10
        start_num = 10 if is_part1 else 5
        for i, point in enumerate(points):
            point_num = start_num - i
            script_lines.append(f"#{point_num} - {point}")
            script_lines.append("")
            
            # Ajouter une phrase d'explication punchy
            explanation = self._generate_point_explanation(category, point_num)
            script_lines.append(explanation)
            script_lines.append("")
            
            # Transition/CTA toutes les 2 points
            if i < len(points) - 1 and i % 2 == 0:
                script_lines.append(random.choice(BRAINROT_PHRASES['transitions']))
                script_lines.append("")
        
        # CONCLUSION AVEC CLIFFHANGER OU CTA
        if is_part1:
            script_lines.append("🎯 MAIS ATTENDEZ... LE MEILLEUR EST À VENIR !")
            script_lines.append("")
            script_lines.append(random.choice(BRAINROT_PHRASES['cliffhangers']))
            script_lines.append("")
            script_lines.append("👉 " + random.choice(BRAINROT_PHRASES['cta_part2']))
        else:
            script_lines.append("💥 ET VOILÀ ! LE POINT NUMÉRO 1 QUI CHANGE TOUT !")
            script_lines.append("")
            script_lines.append("🔥 LIKEZ SI VOUS ÊTES CHOQUÉ !")
            script_lines.append("🔔 ABONNEZ-VOUS POUR PLUS DE CONTENU EXPLOSIF !")
            script_lines.append("💬 COMETEZ LE POINT QUI VOUS A LE PLUS SURPRIS !")
        
        return "\n".join(script_lines)
    
    def _generate_point_explanation(self, category: str, point_num: int) -> str:
        """Génère des explications punchy pour chaque point."""
        
        explanations = {
            'science': [
                "Les dernières recherches prouvent que c'est bien réel !",
                "La science vient de confirmer cette incroyable découverte !",
                "Les experts sont sans voix face à cette révélation !",
                "Cette vérité va révolutionner notre compréhension du monde !",
                "Les preuves sont accablantes, impossible de nier !"
            ],
            'technologie': [
                "Cette technologie va rendre tout ce que vous connaissez obsolète !",
                "Les géants de la tech tentent de cacher cette innovation !",
                "Cette invention va changer votre quotidien à jamais !",
                "Le futur est déjà là, et c'est incroyable !",
                "Cette révélation va faire trembler l'industrie toute entière !"
            ],
            'sante_bienetre': [
                "Votre santé ne sera plus jamais la même après ça !",
                "Les médecins sont choqués par l'efficacité de cette méthode !",
                "Cette découverte va prolonger votre vie de 10 ans !",
                "Votre corps vous remerciera pour cette révélation !",
                "La science confirme : ça marche vraiment !"
            ],
            'psychologie': [
                "Votre cerveau va être bouleversé par cette révélation !",
                "Les psychologues utilisent cette technique en secret !",
                "Cette connaissance va changer vos relations à jamais !",
                "Vous ne verrez plus jamais les gens de la même façon !",
                "Votre mental va devenir invincible avec ça !"
            ],
            'argent_business': [
                "Votre compte en banche va exploser avec cette méthode !",
                "Les millionnaires utilisent cette technique depuis des années !",
                "Votre vie financière va changer radicalement !",
                "Cette stratégie a déjà créé des centaines de millionnaires !",
                "Vous allez enfin comprendre comment devenir riche !"
            ]
        }
        
        category_explanations = explanations.get(category, explanations['science'])
        return random.choice(category_explanations)
    
    def _generate_keywords(self, base_topic: str, category: str, is_part1: bool) -> List[str]:
        """Génère des mots-clés trending et optimisés."""
        
        # Mots-clés de base
        base_keywords = [
            'top 10', 'choc', 'révélation', 'secret', 'choquant',
            'incroyable', 'interdit', 'caché', 'vérité', 'explosif',
            'brainrot', 'addictif', 'viral', 'trending', 'algorithm'
        ]
        
        # Mots-clés spécifiques partie
        part_keywords = ['partie 1', 'début', 'top 10-6'] if is_part1 else ['partie 2', 'suite', 'fin', 'top 5-1']
        
        # Mots-clés catégorie
        category_keywords = {
            'science': ['science', 'découverte', 'recherche', 'innovation'],
            'technologie': ['tech', 'ia', 'innovation', 'futur'],
            'sante_bienetre': ['santé', 'bienêtre', 'médecine', 'corps'],
            'psychologie': ['psycho', 'mental', 'cerveau', 'comportement'],
            'argent_business': ['argent', 'riche', 'business', 'millionnaire']
        }.get(category, [])
        
        # Mots-clés trending 2024
        trending_keywords = [
            'viral tiktok', 'shorts', 'algorithm hack', 'youtube money',
            'content strategy', 'views hack', 'engagement', 'ctr'
        ]
        
        all_keywords = base_keywords + part_keywords + category_keywords + trending_keywords + self.global_tags
        return list(set(all_keywords))[:20]  # Limite YouTube
    
    def generate_content(self, slot_number: int) -> Dict[str, Any]:
        """Produit le contenu brainrot complet pour un créneau."""
        
        if slot_number not in self.daily_variations:
            raise RuntimeError(f"Aucun sujet défini pour le slot {slot_number}")
        
        variation = self.daily_variations[slot_number]
        
        title = self._generate_brainrot_title(
            variation['base_topic'], 
            variation['category'], 
            variation['is_part1'],
            slot_number
        )
        
        script = self.generate_script(
            variation['base_topic'], 
            variation['category'], 
            variation['is_part1'],
            slot_number
        )
        
        keywords = self._generate_keywords(
            variation['base_topic'], 
            variation['category'], 
            variation['is_part1']
        )
        
        # DESCRIPTION OPTIMISÉE POUR L'ALGORITHME
        description = self._generate_youtube_description(
            script, title, variation['is_part1'], slot_number
        )
        
        return {
            'title': title,
            'script': script,
            'description': description,
            'keywords': keywords,
            'category': variation['category'],
            'slot_number': slot_number,
            'is_part1': variation['is_part1'],
            'daily_seed': variation['daily_seed'],
            'content_type': 'top10_brainrot'
        }
    
    def _generate_youtube_description(self, script: str, title: str, is_part1: bool, slot_number: int) -> str:
        """Génère une description YouTube ultra-optimisée."""
        
        # Nettoyer le script pour la description
        clean_script = script.replace('🚨', '').replace('💀', '').replace('🔥', '').replace('🎯', '').replace('💥', '')
        clean_script = clean_script[:300] + "..." if len(clean_script) > 300 else clean_script
        
        description_lines = []
        
        # Première ligne accrocheuse
        description_lines.append(f"🔔 {title}")
        description_lines.append("")
        
        # Script court
        description_lines.append(clean_script)
        description_lines.append("")
        
        # CTA agressif
        description_lines.append("⬇️⬇️ ABONNE-TOI MAINTENANT ⬇️⬇️")
        description_lines.append("")
        description_lines.append("💖 LIKE si tu as aimé la vidéo !")
        description_lines.append("💬 COMMENTE ton point préféré !")
        description_lines.append("🔔 ACTIVE les notifications !")
        description_lines.append("")
        
        # Référence à l'autre partie
        if is_part1:
            description_lines.append("🎯 REGARDE LA PARTIE 2 POUR LA SUITE EXPLOSIVE !")
        else:
            description_lines.append("🔥 AS-TU VU LA PARTIE 1 ? REGARDE LA TOUTE DE SUITE !")
        
        description_lines.append("")
        description_lines.append("#top10 #viral #choc #révélation #brainrot")
        
        return "\n".join(description_lines)

# --- FONCTION PRINCIPALE ---
def generate_daily_contents() -> List[Dict[str, Any]]:
    """Génère les contenus brainrot pour la journée."""
    try:
        config = ConfigLoader().get_config()
        num_slots = config['WORKFLOW'].get('DAILY_SLOTS', 4)
        
        generator = ContentGenerator()
        daily_contents = [generator.generate_content(slot) for slot in range(num_slots)]
        
        print(f"🎯 {len(daily_contents)} contenus BRAINROT générés !")
        for content in daily_contents:
            part = "PARTIE 1" if content['is_part1'] else "PARTIE 2"
            print(f"   📹 Slot {content['slot_number']}: {content['title']} ({part})")
        
        return daily_contents
        
    except Exception as e:
        print(f"❌ Erreur brainrot: {e}", file=sys.stderr)
        return []

# --- TEST ---
if __name__ == "__main__":
    print("🧪 TEST BRAINROT CONTENT GENERATOR...")
    try:
        contents = generate_daily_contents()
        if not contents:
            print("❌ Test échoué")
            sys.exit(1)
            
        print(f"\n✅ {len(contents)} CONTENUS BRAINROT GÉNÉRÉS !")
        for content in contents:
            print("-" * 60)
            print(f"🎯 SLOT {content['slot_number']} | {content['category'].upper()}")
            print(f"📹 {content['title']}")
            print(f"🔑 MOTS-CLÉS: {', '.join(content['keywords'][:5])}...")
            print(f"📝 SCRIPT: {content['script'][:100]}...")
            
    except Exception as e:
        print(f"❌ Test brainrot échoué: {e}")
        sys.exit(1)
