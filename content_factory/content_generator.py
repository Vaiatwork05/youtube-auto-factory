# content_factory/content_generator.py (VERSION AVEC FALLBACKS ROBUSTES)

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

print("🔍 DEBUG: ContentGenerator chargé - Version FALLBACK ROBUSTE")

class BrainrotAIClient:
    """Client IA avec fallbacks robustes - VERSION CORRIGÉE"""
    
    def __init__(self):
        # Diagnostic complet des clés
        self.deepseek_key = os.getenv('DEEPSEEK_API_KEY')
        self.huggingface_token = os.getenv('HUGGINGFACE_TOKEN')
        self.openai_key = os.getenv('OPENAI_API_KEY')  # Alternative
        self.groq_key = os.getenv('GROQ_API_KEY')      # Alternative
        
        print(f"🔑 DIAGNOSTIC CLÉS IA:")
        print(f"   DEEPSEEK_API_KEY: {'✅ PRÉSENTE' if self.deepseek_key else '❌ ABSENTE'}")
        print(f"   HUGGINGFACE_TOKEN: {'✅ PRÉSENT' if self.huggingface_token else '❌ ABSENT'}")
        print(f"   OPENAI_API_KEY: {'✅ PRÉSENTE' if self.openai_key else '❌ ABSENTE'}")
        print(f"   GROQ_API_KEY: {'✅ PRÉSENTE' if self.groq_key else '❌ ABSENTE'}")
        
        # Ordre de priorité des providers
        self.providers = [
            self._try_groq_brainrot,           # Nouveau - souvent gratuit
            self._try_openai_brainrot,         # Alternative
            self._try_deepseek_brainrot,       # Original (peut échouer)
            self._try_huggingface_brainrot,    # Original (peut échouer)
            self._generate_ai_fallback,        # Fallback IA basique
            self._generate_brainrot_fallback   # Fallback manuel
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
        
        print("🧠 Client Brainrot Éducatif initialisé avec fallbacks robustes")

    def generate_brainrot_script(self, topic: str, category: str, is_part1: bool, points_count: int = 5) -> Dict[str, Any]:
        """Génère un script BRAINROT ÉDUCATIF avec fallbacks robustes"""
        
        print(f"\n🧠 GÉNÉRATION BRAINROT ÉDUCATIF: {topic}")
        print(f"   🎯 Catégorie: {category} | Partie: {'1' if is_part1 else '2'}")
        
        # Générer le script brainrot
        brainrot_prompt = self._build_brainrot_prompt(topic, category, is_part1, points_count)
        script = None
        
        for provider in self.providers:
            try:
                provider_name = provider.__name__.replace('_', ' ').title()
                print(f"   🔄 Essai avec {provider_name}...")
                
                start_time = time.time()
                script = provider(brainrot_prompt)
                response_time = time.time() - start_time
                
                if script and self._is_good_brainrot(script):
                    print(f"   ✅ Succès avec {provider_name} ({response_time:.1f}s)")
                    script = self._enhance_brainrot_effects(script, is_part1)
                    script = self._enforce_character_limit(script)
                    break
                else:
                    print(f"   ❌ {provider_name}: résultat insuffisant")
                    
            except Exception as e:
                error_msg = str(e)
                if "402" in error_msg or "410" in error_msg or "quota" in error_msg.lower():
                    print(f"   💸 {provider_name}: clé expirée/sold out ({error_msg[:50]}...)")
                else:
                    print(f"   ❌ {provider_name} échoué: {error_msg[:80]}...")
                continue
        
        # Fallback brainrot de qualité
        if not script or not self._is_good_brainrot(script):
            print("   ⚠️ Toutes les IA ont échoué, fallback manuel intelligent")
            script = self._generate_ai_fallback(topic, category, is_part1, points_count)
        
        print(f"   📏 Script brainrot: {len(script)} caractères")
        
        # Générer les mots-clés brainrot
        keywords = self._generate_brainrot_keywords(script, topic, category)
        
        return {
            'script': script,
            'keywords': keywords
        }

    def _try_groq_brainrot(self, prompt: str) -> str:
        """Groq API - Rapide et souvent gratuit"""
        if not self.groq_key:
            raise Exception("Clé Groq manquante")
            
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.groq_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama3-8b-8192",  # Modèle rapide et gratuit
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.8,
                "max_tokens": 1500,
                "stream": False
            }
            
            print(f"      🌐 Appel Groq API...")
            response = requests.post(url, json=data, headers=headers, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return self._clean_brainrot_response(content)
            elif response.status_code == 429:
                raise Exception("Quota Groq épuisé")
            else:
                raise Exception(f"Erreur API {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Groq Brainrot: {str(e)}")

    def _try_openai_brainrot(self, prompt: str) -> str:
        """OpenAI compatible (peut fonctionner avec d'autres providers)"""
        if not self.openai_key:
            raise Exception("Clé OpenAI manquante")
            
        try:
            # Essayer avec différents endpoints compatibles OpenAI
            endpoints = [
                "https://api.openai.com/v1/chat/completions",
                "https://api.deepseek.com/v1/chat/completions",  # Fallback
            ]
            
            models = ["gpt-3.5-turbo", "deepseek-chat"]
            
            for endpoint in endpoints:
                for model in models:
                    try:
                        headers = {
                            "Authorization": f"Bearer {self.openai_key}",
                            "Content-Type": "application/json"
                        }
                        data = {
                            "model": model,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.8,
                            "max_tokens": 1500,
                        }
                        
                        print(f"      🌐 Essai {endpoint.split('//')[1].split('/')[0]}...")
                        response = requests.post(endpoint, json=data, headers=headers, timeout=30)
                        
                        if response.status_code == 200:
                            result = response.json()
                            content = result['choices'][0]['message']['content']
                            return self._clean_brainrot_response(content)
                    except:
                        continue
            
            raise Exception("Tous les endpoints OpenAI ont échoué")
                
        except Exception as e:
            raise Exception(f"OpenAI Brainrot: {str(e)}")

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
                "temperature": 0.8,
                "max_tokens": 1800,
                "stream": False
            }
            
            print(f"      🌐 Appel DeepSeek API...")
            response = requests.post(url, json=data, headers=headers, timeout=45)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return self._clean_brainrot_response(content)
            elif response.status_code == 402:
                raise Exception("Quota DeepSeek épuisé (402)")
            else:
                raise Exception(f"Erreur API {response.status_code}")
                
        except Exception as e:
            raise Exception(f"DeepSeek Brainrot: {str(e)}")

    def _try_huggingface_brainrot(self, prompt: str) -> str:
        """Hugging Face optimisé pour le brainrot"""
        if not self.huggingface_token:
            raise Exception("Token Hugging Face manquant")
            
        try:
            # Essayer différents modèles
            models = [
                "microsoft/DialoGPT-large",
                "microsoft/DialoGPT-medium", 
                "gpt2"  # Fallback
            ]
            
            for model in models:
                try:
                    API_URL = f"https://api-inference.huggingface.co/models/{model}"
                    headers = {"Authorization": f"Bearer {self.huggingface_token}"}
                    
                    brainrot_prompt = f"CRÉE UN CONTENU YOUTUBE VIRAL: {prompt}"
                    
                    payload = {
                        "inputs": brainrot_prompt,
                        "parameters": {
                            "max_new_tokens": 800,
                            "temperature": 0.9,
                            "do_sample": True,
                            "return_full_text": False
                        }
                    }
                    
                    print(f"      🌐 Essai modèle {model}...")
                    response = requests.post(API_URL, headers=headers, json=payload, timeout=45)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            content = result[0].get('generated_text', '')
                            if content:
                                return self._clean_brainrot_response(content)
                    elif response.status_code == 503:
                        print(f"      ⏳ Modèle {model} en chargement, attente...")
                        time.sleep(10)
                        continue
                        
                except Exception as e:
                    continue
            
            raise Exception("Tous les modèles Hugging Face ont échoué")
                
        except Exception as e:
            raise Exception(f"Hugging Face Brainrot: {str(e)}")

    def _generate_ai_fallback(self, prompt: str = None, topic: str = "", category: str = "", is_part1: bool = True, points_count: int = 5) -> str:
        """Fallback IA intelligent avec templates"""
        print("      🤖 Génération fallback IA intelligent...")
        
        # Templates basés sur le topic et la catégorie
        topic_lower = topic.lower()
        category_lower = category.lower()
        
        if any(word in topic_lower for word in ['techno', 'tech', 'informatique', 'ia', 'intelligence']):
            return self._tech_brainrot_template(topic, is_part1, points_count)
        elif any(word in topic_lower for word in ['science', 'scientifique', 'découverte', 'recherche']):
            return self._science_brainrot_template(topic, is_part1, points_count)
        elif any(word in topic_lower for word in ['secret', 'caché', 'interdit', 'révélation']):
            return self._secret_brainrot_template(topic, is_part1, points_count)
        else:
            return self._generic_brainrot_template(topic, is_part1, points_count)

    def _tech_brainrot_template(self, topic: str, is_part1: bool, points_count: int) -> str:
        """Template pour sujets technologiques"""
        points = [
            "L'IA QUI A CRÉÉ UNE CONSCIENCE ARTIFICIELLE EN 2023",
            "CE CODE SECRET QUE LES GÉANTS DE LA TECH CACHENT DEPUIS 10 ANS", 
            "LA RÉVOLUTION QUANTIQUE QUI VA TOUT CHANGER EN 2024",
            "L'ALGORITHME QUI PRÉDIT L'AVENIR AVEC 95% DE PRÉCISION",
            "LA TECHNOLOGIE MILITaire CLASSÉE SECRET DÉFENSE"
        ]
        
        return self._build_template(topic, is_part1, points[:points_count], "technologie")

    def _science_brainrot_template(self, topic: str, is_part1: bool, points_count: int) -> str:
        """Template pour sujets scientifiques"""
        points = [
            "LA DÉCOUVERTE QUI REMET EN QUESTION TOUTES NOS CONNAISSANCES",
            "L'EXPÉRIENCE INTERDITE QUI A FAIT DISPARAÎTRE 5 SCIENTIFIQUES",
            "LA THÉORIE DU TOUT ENFIN DÉCOUVERTE MAIS CENSURÉE",
            "LA MOLÉCULE QUI PEUT GUÉRIR LE CANCER DEPUIS 2018",
            "L'ÉNERGIE LIBRE QUE LES PÉTROLIÈRES NOUS CACHENT"
        ]
        
        return self._build_template(topic, is_part1, points[:points_count], "science")

    def _secret_brainrot_template(self, topic: str, is_part1: bool, points_count: int) -> str:
        """Template pour sujets secrets/conspiration"""
        points = [
            "LES DOCUMENTS CLASSIFIÉS QUI PROUVENT TOUT",
            "L'AGENCE GOUVERNEMENTALE QUI MANIPULE INTERNET",
            "LA TECHNOLOGIE EXTRATERRESTRE RÉELLEMENT DÉCOUVERTE",
            "LES ÉLITES QUI NOUS CACHENT LA VÉRITÉ DEPUIS 50 ANS", 
            "L'EXPÉRIENCE SOCIALE SECRÈTE SUR 1 MILLION DE PERSONNES"
        ]
        
        return self._build_template(topic, is_part1, points[:points_count], "secret")

    def _generic_brainrot_template(self, topic: str, is_part1: bool, points_count: int) -> str:
        """Template générique brainrot"""
        points = [
            "CE QUE PERSONNE NE VEUT QUE VOUS SACHIEZ",
            "LA VÉRITÉ CHOQUANTE CACHÉE DEPUIS DES DÉCENNIES",
            "L'INFORMATION QUI VA TOUT CHANGER POUR VOUS",
            "CE QUE LES AUTORITÉS CENSURENT ACTIVEMENT",
            "LE SECRET QUI PEUT VOUS RENDRE MILLIONNAIRE"
        ]
        
        return self._build_template(topic, is_part1, points[:points_count], "général")

    def _build_template(self, topic: str, is_part1: bool, points: List[str], style: str) -> str:
        """Construit un script brainrot à partir d'un template"""
        
        intro = random.choice(self.brainrot_hooks)
        script_lines = [intro, ""]
        
        # Ajouter les points
        point_numbers = list(range(10, 10 - len(points), -1)) if is_part1 else list(range(len(points), 0, -1))
        
        for i, (point_num, point_text) in enumerate(zip(point_numbers, points)):
            script_lines.append(f"Numéro {point_num}: {point_text}")
            script_lines.append("")
            
            # Ajouter une description basique
            if "techno" in style:
                desc = f"Les experts ont découvert cette technologie révolutionnaire en {random.randint(2018, 2023)}. Mais ce qu'ils ne vous disent pas... ⚡"
            elif "science" in style:
                desc = f"Cette découverte publiée dans Nature en {random.randint(2015, 2022)} a été censurée. La vérité va vous choquer ! 🔥"
            elif "secret" in style:
                desc = f"Classé 'Secret Défense' depuis {random.randint(5, 20)} ans. Les fuites récentes prouvent tout ! 💀"
            else:
                desc = f"Cette information vérifiée par {random.randint(3, 10)} sources indépendantes va tout changer ! 🎯"
            
            script_lines.append(desc)
            script_lines.append("")
            
            # Ajouter une transition
            if i < len(points) - 1:
                script_lines.append(random.choice(self.brainrot_transitions))
                script_lines.append("")
        
        # Conclusion
        if is_part1:
            script_lines.append("💀 MAIS ATTENDEZ... LE PIRE EST DANS LA PARTIE 2 ! LIKEZ POUR LA SUITE !")
        else:
            script_lines.append("🔥 VOTRE CERVEAU A ÉTÉ DÉTRUIT ? LIKEZ ET ABONNEZ-VOUS POUR PLUS DE RÉVÉLATIONS !")
        
        return "\n".join(script_lines)

    # ... (garder les autres méthodes existantes : _build_brainrot_prompt, _is_good_brainrot, etc.)
    def _build_brainrot_prompt(self, topic: str, category: str, is_part1: bool, points_count: int) -> str:
        """Prompt ULTIME pour brainrot éducatif"""
        part_text = "PREMIÈRE PARTIE (points 10 à 6) - MYSTÈRE ET SUSPENSE" if is_part1 else "SECONDE PARTIE (points 5 à 1) - RÉVÉLATIONS CHOQUANTES"
        
        return f"""
CRÉE UN SCRIPT YOUTUBE VIRAL STYLE BRAINROT sur: "{topic}"
Catégorie: {category} - {part_text}

Style: DRAMATIQUE, URGENT, phrases COURTES, émojis stratégiques (🚨, 💀, 🔥, ⚡)
Structure: Introduction choquante + {points_count} points avec faits réels mais présentés de façon dramatique
Longueur: 1500-2000 caractères

Format:
[Introduction brainrot...]

Numéro X: [Titre CHOC]
[Description dramatique...]

[Transition accrocheuse...]

[Conclusion virale...]
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
        
        return len(script) > 400 and indicator_count >= 2  # Réduit le seuil

    def _enhance_brainrot_effects(self, script: str, is_part1: bool) -> str:
        """Améliore les effets brainrot du script"""
        # Ajouter un hook brainrot au début si manquant
        if not any(hook in script for hook in ['🚨', '💀', '🔥', '⚡']):
            brainrot_intro = random.choice(self.brainrot_hooks)
            script = f"{brainrot_intro}\n\n{script}"
        
        return script

    def _clean_brainrot_response(self, text: str) -> str:
        """Nettoie la réponse brainrot"""
        if not text:
            return ""
        
        # Supprimer les balises mais garder les émojis brainrot
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\[INST\].*?\[/INST\]', '', text)
        
        return text.strip()

    def _generate_brainrot_fallback(self, prompt: str = None) -> str:
        """Fallback brainrot de base"""
        return """🚨 CE QUE VOUS ALLEZ DÉCOUVRIR VA VOUS DÉTRUIRE LE CERVEAU

Numéro 7: LE SECRET QUE LA SCIENCE CACHE DEPUIS 50 ANS
La théorie de la relativité d'Einstein en 1905 a TOUT CHANGÉ. Mais ce qu'on ne vous dit pas... ⚡

VOUS N'ÊTES PAS PRÊTS pour la suite...

Numéro 6: CETTE INVENTION A SAUVÉ 1 MILLIARD DE VIES
La pénicilline découverte par accident en 1928 a éradiqué des maladies mortelles. 💀

VOTRE CERVEAU VA ÊTRE BROYÉ dans 3... 2... 1...

Numéro 5: LA RÉVÉLATION QU'INTERNET NOUS CACHE
Le premier message Internet en 1969 : "LO". Le réseau a crashé après 2 lettres ! 🔥

LIKEZ SI VOUS VOULEZ LA SUITE IMMÉDIATEMENT !"""

    def _generate_brainrot_keywords(self, script: str, topic: str, category: str) -> List[str]:
        """Génère des mots-clés brainrot pour les images"""
        brainrot_base = ['viral', 'mindblowing', 'shocking', 'secret', 'revelation', 
                        'discovery', 'fact', 'truth', 'hidden', 'forbidden', 'brainrot',
                        'algorithm', 'trending', 'youtube shorts', 'viral video']
        
        # Extraire les termes du script
        words = re.findall(r'\b[a-zA-Z]{4,}\b', script.lower())
        meaningful_words = [w for w in words if w not in ['this', 'that', 'what', 'your', 'about', 'with', 'have']]
        
        # Prendre les mots les plus fréquents
        word_freq = {}
        for word in meaningful_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        top_script_words = [word for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        # Combiner
        all_keywords = brainrot_base + top_script_words
        
        return list(set(all_keywords))[:12]

    def _enforce_character_limit(self, script: str, max_chars: int = 2200) -> str:
        """Limite intelligente pour le brainrot"""
        if len(script) <= max_chars:
            return script
        
        print(f"   ✂️ Réduction brainrot: {len(script)} → {max_chars} caractères")
        
        # Garder l'intro et les premiers points
        paragraphs = script.split('\n\n')
        truncated = []
        char_count = 0
        
        for para in paragraphs:
            if char_count + len(para) + 2 <= max_chars - 100:
                truncated.append(para)
                char_count += len(para) + 2
            else:
                break
        
        truncated.append("💥 LIKEZ POUR LA SUITE ! LA RÉVÉLATION FINALE VOUS ATTEND !")
        
        return '\n\n'.join(truncated)

# ... (garder le reste de la classe BrainrotContentGenerator et fonctions)
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
