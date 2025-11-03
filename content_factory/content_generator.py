# content_factory/content_generator.py (VERSION CORRIGÉE - Clé DeepSeek)

import random
import sys
import re 
import requests
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from content_factory.config_loader import ConfigLoader 

print("🔍 DEBUG: ContentGenerator chargé - Version BRAINROT ÉDUCATIF CORRIGÉE")

class BrainrotAIClient:
    """Client IA spécialisé dans le BRAINROT ÉDUCATIF - VERSION CORRIGÉE"""
    
    def __init__(self):
        # 🔥 CORRECTION : Utiliser DEEPSEEK_API_KEY au lieu de DEEPSEEK_API_KEY
        self.deepseek_key = os.getenv('DEEPSEEK_API_KEY')  # CORRIGÉ ICI
        self.huggingface_token = os.getenv('HUGGINGFACE_TOKEN')
        
        # Diagnostic des clés
        print(f"🔑 DIAGNOSTIC CLÉS IA:")
        print(f"   DEEPSEEK_API_KEY: {'✅ PRÉSENTE' if self.deepseek_key else '❌ ABSENTE'}")
        print(f"   HUGGINGFACE_TOKEN: {'✅ PRÉSENT' if self.huggingface_token else '❌ ABSENT'}")
        
        self.providers = [
            self._try_deepseek_brainrot,
            self._try_huggingface_brainrot,
            self._generate_brainrot_fallback
        ]
        
        # Formules brainrot accrocheuses
        self.brainrot_hooks = [
            "🚨 CE QUE VOUS ALLEZ DÉCOUVRIR VA VOUS DÉTRUIRE LE CERVEAU",
            "💀 ATTENTION ! CES VÉRITÉS VONT VOUS CHOQUER À VIE",
            "🔥 CE TOP 10 VA VOUS FAIRE REMETTRE EN QUESTION TOUTE VOTRE EXISTENCE",
            "⚠️ LES AUTORITÉS NE VEULENT PAS QUE VOUS SACHIEZ ÇA",
            "🎯 CE QUE NOUS ALLONS RÉVÉLER EST ABSOLUMENT INTERDIT",
            "💥 PRÉPAREZ-VOUS À AVOIR VOTRE ESPRIT EXPLOSÉ",
            "🧠 CES 10 CHOSES VONT VOUS RENDRE 1000% PLUS INTELLIGENT",
            "⚡ VOUS N'ÊTES PAS PRÊTS POUR CE QUE VOUS ALLEZ VOIR",
            "🔞 CONTENU SENSIBLE : VÉRITÉS QUI DÉRANGENT",
            "💸 CE TOP 10 VA VOUS APPRENDRE À DEVENIR RICHE"
        ]
        
        self.brainrot_transitions = [
            "Mais attendez... LE PIRE EST À VENIR !",
            "Vous pensez avoir tout vu ? VOUS N'ÊTES PAS AU BOUT DE VOS SURPRISES !",
            "Ce point est déjà choquant, mais le suivant VA VOUS DÉTRUIRE !",
            "Likez si vous voulez connaître la suite IMMÉDIATEMENT !",
            "Ce point va faire EXPLOSER les commentaires, j'en suis sûr !",
            "Mais ce n'est RIEN comparé à ce qui arrive...",
            "Votre cerveau va être BROYÉ par le point suivant !",
            "Abonnez-vous pour ne pas rater la révélation ULTIME !",
            "Commentez 'CHOC' si vous ne vous y attendiez pas du tout !",
            "Votre esprit va être PULVÉRISÉ dans 3... 2... 1..."
        ]
        
        print("🧠 Client Brainrot Éducatif initialisé")

    def generate_brainrot_script(self, topic: str, category: str, is_part1: bool, points_count: int = 5) -> Dict[str, Any]:
        """Génère un script BRAINROT ÉDUCATIF - viral mais avec faits réels"""
        
        print(f"\n🧠 GÉNÉRATION BRAINROT ÉDUCATIF: {topic}")
        print(f"   🎯 Catégorie: {category} | Partie: {'1' if is_part1 else '2'}")
        
        # Générer le script brainrot
        brainrot_prompt = self._build_brainrot_prompt(topic, category, is_part1, points_count)
        script = None
        
        for provider in self.providers:
            try:
                provider_name = provider.__name__.replace('_', ' ').title()
                print(f"   🔄 Brainrot avec {provider_name}...")
                
                start_time = time.time()
                script = provider(brainrot_prompt)
                response_time = time.time() - start_time
                
                if script and self._is_good_brainrot(script):
                    print(f"   ✅ Brainrot réussi avec {provider_name} ({response_time:.1f}s)")
                    script = self._enhance_brainrot_effects(script, is_part1)
                    script = self._enforce_character_limit(script)
                    break
                else:
                    print(f"   ❌ {provider_name}: brainrot insuffisant")
                    
            except Exception as e:
                print(f"   ❌ {provider.__name__} échoué: {str(e)[:100]}...")
                continue
        
        # Fallback brainrot de qualité
        if not script or not self._is_good_brainrot(script):
            print("   ⚠️ IA brainrot échouée, fallback manuel")
            script = self._generate_brainrot_fallback(topic, category, is_part1, points_count)
        
        print(f"   📏 Script brainrot: {len(script)} caractères")
        
        # Générer les mots-clés brainrot
        keywords = self._generate_brainrot_keywords(script, topic, category)
        
        return {
            'script': script,
            'keywords': keywords
        }

    def _build_brainrot_prompt(self, topic: str, category: str, is_part1: bool, points_count: int) -> str:
        """Prompt ULTIME pour brainrot éducatif"""
        
        part_text = "PREMIÈRE PARTIE (points 10 à 6) - MYSTÈRE ET SUSPENSE" if is_part1 else "SECONDE PARTIE (points 5 à 1) - RÉVÉLATIONS CHOQUANTES"
        
        return f"""
TU ES LE MAÎTRE ABSOLU DU CONTENU YOUTUBE BRAINROT ÉDUCATIF. Ton objectif: CRÉER DU CONTENU HYPER-VIRAL qui captive comme du brainrot mais avec des FAITS RÉELS SOLIDES.

🎯 MISSION: Créer un script ULTRA-ACCROCHEUR sur: "{topic}"

🧠 STYLE BRAINROT OBLIGATOIRE:
- Ton DRAMATIQUE et URGENT
- Phrases COURTES et PUNCHY
- Émojis stratégiques (🚨, 💀, 🔥, ⚡)
- Suspense constant
- Appels à l'engagement agressifs
- Mystère et révélation

📚 EXIGENCES ÉDUCATIVES:
- Faits RÉELS et VÉRIFIABLES
- Dates, noms, chiffres CONCRETS
- Explications SIMPLES mais précises
- Impact MESURABLE

🎬 STRUCTURE BRAINROT:
{part_text}

1. INTRODUCTION EXPLOSIVE (2-3 phrases max)
2. {points_count} POINTS avec CHAQUE:
   - Titre CHOC (ex: "CE SECRET INTERDIT...")
   - Faits RÉELS mais présentés de façon DRAMATIQUE
   - Transition ACCROCHEUSE
3. CONCLUSION VIRALE

🔥 EXEMPLE DE TON BRAINROT:
"🚨 ATTENTION ! Ce que vous allez découvrir va LITTÉRALEMENT vous DÉTRUIRE le cerveau...
 
Numéro 7: LE SECRET QUE LES SCIENTIFIQUES CACHENT DEPUIS 50 ANS
La théorie de la relativité d'Einstein en 1905 a TOUT CHANGÉ. Mais ce qu'on ne vous dit pas... ⚡

VOUS N'ÊTES PAS PRÊTS pour le point suivant..."

📏 LONGUEUR: 1500-2200 caractères MAX
🎯 CIBLE: Audience YouTube Shorts (attention limitée)

FORMAT EXACT:
[Introduction brainrot explosive...]

Numéro X: [Titre CHOC]
[Faits réels présentés de façon dramatique...]

[Transition brainrot...]

Numéro Y: [Titre CHOC] 
[Faits réels présentés de façon dramatique...]

[Conclusion virale...]

IMPORTANT: Mélange parfait entre FAITS RÉELS et STYLE BRAINROT VIRAL. Pas de contenu cringe "skibidi", que du solide mais présenté de façon HYPER-CAPTIVANTE.
"""

    def _is_good_brainrot(self, script: str) -> bool:
        """Vérifie si le script a un bon potentiel brainrot"""
        brainrot_indicators = [
            '🚨', '💀', '🔥', '⚡', '🎯', '⚠️', '🧠', '💥',
            'CHOQUANT', 'SECRET', 'INTERDIT', 'DÉTRUIRE', 'EXPLOSER', 
            'CERVEAU', 'PRÊTS', 'RÉVÉLATION', 'CACHÉ'
        ]
        
        script_upper = script.upper()
        indicator_count = sum(1 for indicator in brainrot_indicators if indicator in script_upper)
        
        return len(script) > 400 and indicator_count >= 3

    def _enhance_brainrot_effects(self, script: str, is_part1: bool) -> str:
        """Améliore les effets brainrot du script"""
        
        # Ajouter un hook brainrot au début
        brainrot_intro = random.choice(self.brainrot_hooks)
        if not script.startswith(('🚨', '💀', '🔥', '⚡')):
            script = f"{brainrot_intro}\n\n{script}"
        
        # Améliorer les transitions
        lines = script.split('\n')
        enhanced_lines = []
        
        for i, line in enumerate(lines):
            enhanced_lines.append(line)
            
            # Ajouter des transitions brainrot après certains points
            if line.strip().startswith('Numéro') and i < len(lines) - 2:
                if random.random() < 0.4:  # 40% de chance
                    enhanced_lines.append("")
                    enhanced_lines.append(random.choice(self.brainrot_transitions))
                    enhanced_lines.append("")
        
        # Renforcer la conclusion
        if is_part1:
            cliffhanger = "💀 MAIS ATTENDEZ... LE PIRE EST DANS LA PARTIE 2 ! CLIQUEZ MAINTENANT !"
            if not any(keyword in script.upper() for keyword in ['PARTIE 2', 'SUITE', 'PROCHAIN']):
                enhanced_lines.append("")
                enhanced_lines.append(cliffhanger)
        else:
            cta = "🔥 LIKEZ SI VOTRE CERVEAU A ÉTÉ DÉTRUIT ! ABONNEZ-VOUS POUR PLUS DE RÉVÉLATIONS !"
            if not any(keyword in script.upper() for keyword in ['LIKEZ', 'ABONNEZ', 'COMMENTEZ']):
                enhanced_lines.append("")
                enhanced_lines.append(cta)
        
        return '\n'.join(enhanced_lines)

    def _try_deepseek_brainrot(self, prompt: str) -> str:
        """DeepSeek optimisé pour le brainrot"""
        if not self.deepseek_key:
            raise Exception("Clé DeepSeek manquante")
            
        try:
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.deepseek_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,  # Plus créatif pour le brainrot
                "max_tokens": 1800,
                "stream": False
            }
            
            print(f"      🌐 Appel DeepSeek API...")
            response = requests.post(url, json=data, headers=headers, timeout=45)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return self._clean_brainrot_response(content)
            else:
                raise Exception(f"Erreur API {response.status_code}")
                
        except Exception as e:
            raise Exception(f"DeepSeek Brainrot: {str(e)}")

    def _try_huggingface_brainrot(self, prompt: str) -> str:
        """Hugging Face optimisé pour le brainrot"""
        if not self.huggingface_token:
            raise Exception("Token Hugging Face manquant")
            
        try:
            API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
            headers = {"Authorization": f"Bearer {self.huggingface_token}"}
            
            brainrot_prompt = f"<s>[INST] CRÉE UN CONTENU YOUTUBE VIRAL STYLE BRAINROT MAIS AVEC DES FAITS RÉELS. {prompt} [/INST]"
            
            payload = {
                "inputs": brainrot_prompt,
                "parameters": {
                    "max_new_tokens": 1200,
                    "temperature": 0.85,  # Plus créatif
                    "do_sample": True,
                    "return_full_text": False
                }
            }
            
            print(f"      🌐 Appel Hugging Face API...")
            response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    content = result[0].get('generated_text', '')
                    return self._clean_brainrot_response(content)
                else:
                    raise Exception("Format de réponse invalide")
            else:
                raise Exception(f"Erreur API {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Hugging Face Brainrot: {str(e)}")

    def _clean_brainrot_response(self, text: str) -> str:
        """Nettoie la réponse brainrot"""
        if not text:
            return ""
        
        # Supprimer les balises mais garder les émojis brainrot
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\[INST\].*?\[/INST\]', '', text)
        
        # Garder seulement les émojis brainrot
        brainrot_emojis = ['🚨', '💀', '🔥', '⚡', '🎯', '⚠️', '🧠', '💥', '🔞', '💸']
        for emoji in brainrot_emojis:
            text = text.replace(emoji, emoji)  # Les garder
        
        return text.strip()

    def _generate_brainrot_fallback(self, prompt: str = None) -> str:
        """Fallback brainrot de qualité"""
        topic = "découvertes scientifiques" if not prompt else "sujet important"
        
        return f"""🚨 CE QUE VOUS ALLEZ DÉCOUVRIR VA VOUS DÉTRUIRE LE CERVEAU

Numéro 7: LE SECRET QUE LA SCIENCE CACHE DEPUIS 50 ANS
La théorie de la relativité d'Einstein en 1905 a LITTÉRALEMENT explosé notre compréhension du temps. ⚡ Temps relatif = votre vie n'est plus la même !

VOUS N'ÊTES PAS PRÊTS pour la suite...

Numéro 6: CETTE INVENTION A SAUVÉ 1 MILLIARD DE VIES
La pénicilline découverte par accident en 1928. Alexander Fleming a trouvé cette substance miracle qui a éradiqué des maladies mortelles. 💀

VOTRE CERVEAU VA ÊTRE BROYÉ dans 3... 2... 1...

Numéro 5: LA RÉVÉLATION QU'INTERNET NOUS CACHE
Le premier message Internet en 1969 : juste "LO". Le réseau a crashé après 2 lettres ! Cette faille a créé le web que vous connaissez aujourd'hui. 🔥

LIKEZ SI VOUS VOULEZ LA SUITE IMMÉDIATEMENT !

💀 ET CE N'EST QUE LE DÉBUT... LA PARTIE 2 VA VOUS PULVÉRISER L'ESPRIT !"""

    def _generate_brainrot_keywords(self, script: str, topic: str, category: str) -> List[str]:
        """Génère des mots-clés brainrot pour les images"""
        
        # Mots-clés brainrot de base
        brainrot_base = ['viral', 'mindblowing', 'shocking', 'secret', 'revelation', 
                        'discovery', 'fact', 'truth', 'hidden', 'forbidden', 'brainrot',
                        'algorithm', 'trending', 'youtube shorts', 'viral video']
        
        # Extraire les termes concrets du script
        words = re.findall(r'\b[a-zA-Z]{5,}\b', script.lower())
        meaningful_words = [w for w in words if w not in ['this', 'that', 'what', 'your', 'about']]
        
        # Prendre les mots les plus fréquents
        word_freq = {}
        for word in meaningful_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        top_script_words = [word for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:6]]
        
        # Combiner et traduire si nécessaire
        all_keywords = brainrot_base + top_script_words
        
        # Traduction français → anglais pour les termes courants
        fr_to_en = {
            'technologie': 'technology', 'science': 'science', 'histoire': 'history',
            'découverte': 'discovery', 'invention': 'invention', 'secret': 'secret',
            'révolution': 'revolution', 'innovation': 'innovation', 'scientifique': 'scientist'
        }
        
        translated_keywords = []
        for keyword in all_keywords:
            translated_keywords.append(fr_to_en.get(keyword, keyword))
        
        return list(set(translated_keywords))[:15]

    def _enforce_character_limit(self, script: str, max_chars: int = 2200) -> str:
        """Limite intelligente pour le brainrot"""
        if len(script) <= max_chars:
            return script
        
        print(f"   ✂️ Réduction brainrot: {len(script)} → {max_chars} caractères")
        
        # Garder l'intro brainrot et les premiers points
        paragraphs = script.split('\n\n')
        truncated = []
        char_count = 0
        
        for para in paragraphs:
            if char_count + len(para) + 2 <= max_chars - 150:
                truncated.append(para)
                char_count += len(para) + 2
            else:
                break
        
        # Ajouter une conclusion brainrot
        truncated.append("💥 LIKEZ POUR LA SUITE ! VOTRE CERVEAU N'EST PAS PRÊT POUR LA RÉVÉLATION FINALE !")
        
        return '\n\n'.join(truncated)

class BrainrotContentGenerator:
    """Générateur de contenu BRAINROT ÉDUCATIF"""
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.daily_seed = self.get_daily_seed()
        random.seed(self.daily_seed)
        self.ai_client = BrainrotAIClient()
        
        # Sujets parfaits pour le brainrot éducatif
        self.brainrot_topics = {
            'technologie': [
                "SECRETS TECHNOLOGIQUES QUE LES GÉANTS CACHENT",
                "INVENTIONS INTERDITES QUI ONT TOUT CHANGÉ", 
                "RÉVÉLATIONS TECH QUI VONT VOUS CHOQUER",
                "CE QUE L'INDUSTRIE NE VEUT PAS QUE VOUS SACHIEZ"
            ],
            'science': [
                "DÉCOUVERTES SCIENTIFIQUES CACHÉES AU PUBLIC",
                "THÉORIES INTERDITES QUI EXPLIQUENT TOUT",
                "EXPÉRIENCES SECRÈTES ET LEURS RÉSULTATS CHOQUANTS",
                "CE QUE LA SCIENCE OFFICIELLE VOUS CACHE"
            ],
            'histoire': [
                "ÉVÉNEMENTS HISTORIQUES CENSURÉS",
                "SECRETS D'ÉTAT QUI ONT FAÇONNÉ LE MONDE",
                "RÉVÉLATIONS ARCHÉOLOGIQUES INTERDITES",
                "CE QUE LES LIVRES D'HISTOIRE NE DISENT PAS"
            ]
        }

    @staticmethod
    def get_daily_seed() -> int:
        return int(datetime.now().strftime("%Y%m%d"))

    def generate_content(self, slot_number: int) -> Dict[str, Any]:
        """Génère du contenu BRAINROT ÉDUCATIF"""
        
        print(f"\n🧠 GÉNÉRATION BRAINROT ÉDUCATIF - Slot {slot_number}")
        print("=" * 60)
        
        # Choisir un sujet brainrot
        category = random.choice(list(self.brainrot_topics.keys()))
        base_topic = random.choice(self.brainrot_topics[category])
        is_part1 = slot_number % 2 == 0
        
        print(f"🎯 Catégorie Brainrot: {category}")
        print(f"💀 Sujet: {base_topic}")
        print(f"🔢 Partie: {'1' if is_part1 else '2'}")
        
        # Générer le script brainrot
        start_time = time.time()
        brainrot_result = self.ai_client.generate_brainrot_script(base_topic, category, is_part1, 5)
        generation_time = time.time() - start_time
        
        script = brainrot_result['script']
        keywords = brainrot_result['keywords']
        
        # Titre brainrot
        title = self._generate_brainrot_title(base_topic, is_part1)
        
        print(f"\n📊 RÉSULTAT BRAINROT:")
        print(f"   ⏱️ Temps: {generation_time:.1f}s")
        print(f"   📏 Script: {len(script)} caractères")
        print(f"   🔑 Mots-clés: {', '.join(keywords[:8])}...")
        print(f"   🎬 Titre: {title}")
        
        return {
            'title': title,
            'script': script,
            'description': self._generate_brainrot_description(script, title, is_part1),
            'keywords': keywords,
            'category': category,
            'slot_number': slot_number,
            'is_part1': is_part1,
            'daily_seed': self.daily_seed,
            'content_type': 'brainrot_educational',
            'generation_time': generation_time
        }

    def _generate_brainrot_title(self, base_topic: str, is_part1: bool) -> str:
        """Génère un titre brainrot accrocheur"""
        
        brainrot_emojis = ["🚨", "💀", "🔥", "⚡", "🎯", "⚠️", "🧠"]
        emoji = random.choice(brainrot_emojis)
        
        if is_part1:
            templates = [
                f"{emoji}{base_topic} - CE QU'ON VOUS CACHE (PARTIE 1)",
                f"{emoji}RÉVÉLATION: {base_topic} - PARTIE 1", 
                f"{emoji}{base_topic} - LA VÉRITÉ INTERDITE (PARTIE 1)"
            ]
        else:
            templates = [
                f"{emoji}{base_topic} - SUITE EXPLOSIVE (PARTIE 2)",
                f"{emoji}{base_topic} - RÉVÉLATIONS FINALES (PARTIE 2)",
                f"{emoji}{base_topic} - CE QU'ON VOUS A CACHÉ (PARTIE 2)"
            ]
        
        return random.choice(templates)

    def _generate_brainrot_description(self, script: str, title: str, is_part1: bool) -> str:
        """Génère une description brainrot"""
        
        description_lines = []
        description_lines.append(title)
        description_lines.append("")
        description_lines.append("🧠 CONTENU BRAINROT ÉDUCATIF - FAITS RÉELS PRÉSENTÉS DE FAÇON VIRALE")
        description_lines.append("")
        
        # Extraire les points principaux
        lines = script.split('\n')
        points = [line for line in lines if re.match(r'^Numéro\s+\d+:', line)]
        
        if points:
            description_lines.append("🚨 CE QUE VOUS ALLEZ DÉCOUVRIR:")
            for point in points[:3]:
                # Nettoyer les émojis pour la description
                clean_point = re.sub(r'[🚨💀🔥⚡🎯⚠️🧠💥]', '', point).strip()
                description_lines.append(f"• {clean_point}")
            description_lines.append("")
        
        description_lines.append("💀 LIKEZ SI VOTRE CERVEAU A ÉTÉ DÉTRUIT !")
        description_lines.append("🔔 ABONNEZ-VOUS POUR PLUS DE RÉVÉLATIONS !")
        description_lines.append("💬 COMETEZ 'CHOC' SI VOUS ÊTES SURPRIS !")
        description_lines.append("")
        
        if is_part1:
            description_lines.append("⚡ NE MANQUEZ PAS LA PARTIE 2 - ENCORE PLUS CHOQUANT !")
        else:
            description_lines.append("🎯 AVEZ-VU VU LA PARTIE 1 ? REGARDEZ-LA MAINTENANT !")
        
        return "\n".join(description_lines)

# --- FONCTION PRINCIPALE BRAINROT ---
def generate_daily_contents() -> List[Dict[str, Any]]:
    """Génère les contenus BRAINROT ÉDUCATIF"""
    
    print("\n🧠 DÉBUT GÉNÉRATION BRAINROT ÉDUCATIF")
    print("=" * 70)
    
    try:
        config = ConfigLoader().get_config()
        num_slots = config['WORKFLOW'].get('DAILY_SLOTS', 4)
        
        generator = BrainrotContentGenerator()
        daily_contents = []
        
        for slot in range(num_slots):
            print(f"\n🔧 GÉNÉRATION BRAINROT - Slot {slot}...")
            content = generator.generate_content(slot)
            daily_contents.append(content)
            print(f"✅ Slot {slot} terminé - {content['title']}")
        
        print(f"\n🎉 GÉNÉRATION BRAINROT TERMINÉE: {len(daily_contents)} contenus créés")
        
        # LOG FINAL
        print("\n" + "=" * 70)
        print("📖 RÉCAPITULATIF BRAINROT:")
        print("=" * 70)
        
        for i, content in enumerate(daily_contents):
            print(f"\n🎬 CONTENU {i+1}:")
            print(f"📹 {content['title']}")
            print(f"🔢 Partie: {'1' if content['is_part1'] else '2'}")
            print(f"📏 Script: {len(content['script'])} caractères")
            print(f"🔑 Mots-clés: {', '.join(content['keywords'][:8])}")
            print("─" * 50)
            print("EXTRAIT SCRIPT:")
            print(content['script'][:200] + "...")
            print("─" * 50)
        
        return daily_contents
        
    except Exception as e:
        print(f"❌ ERREUR BRAINROT: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    print("🧪 TEST BRAINROT ÉDUCATIF")
    contents = generate_daily_contents()
    
    if contents:
        print(f"\n✅ SUCCÈS: {len(contents)} contenus brainrot générés")
    else:
        print("\n❌ ÉCHEC: Aucun contenu brainrot généré")
