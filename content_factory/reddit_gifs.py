# content_factory/reddit_gifs.py (VERSION INTELLIGENTE)

import os
import re
import time
import random
import requests
from typing import List, Dict, Optional
from urllib.parse import quote

class BrainrotGIFProvider:
    """Fournisseur de GIFs intelligent avec analyse de contenu."""
    
    def __init__(self):
        # SUBREDDITS GÉNÉRAUX (meilleurs résultats)
        self.best_subreddits = [
            "gifs", "reactiongifs", "interestingasfuck", "beamazed", 
            "nextfuckinglevel", "perfectloops", "woahdude", "blackmagicfuckery"
        ]
        
        self.user_agent = "YouTubeBrainrotFactory/1.0"
        self.rate_limit_delay = 0.7
        
        # Mots vides français
        self.stop_words = {
            'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'ou', 
            'à', 'dans', 'pour', 'sur', 'avec', 'par', 'ce', 'cette', 'ces',
            'son', 'sa', 'ses', 'que', 'qui', 'quoi', 'quand', 'où', 'comment', 'pourquoi'
        }
        
        # Mapping français → anglais
        self.fr_to_en = {
            'technologie': 'technology', 'science': 'science', 'psychologie': 'psychology',
            'argent': 'money', 'santé': 'health', 'innovation': 'innovation', 'robot': 'robot',
            'intelligence': 'ai', 'artificielle': 'artificial intelligence', 'numérique': 'digital',
            'virtuel': 'virtual reality', 'données': 'data', 'sécurité': 'security',
            'confidentiel': 'secret', 'persuasion': 'persuasion', 'influence': 'influence',
            'militaire': 'military', 'défense': 'defense', 'classée': 'classified',
            'secret': 'secret', 'recherche': 'research', 'découverte': 'discovery',
            'médecine': 'medicine', 'business': 'business', 'richesse': 'wealth',
            'succès': 'success', 'espionnage': 'spy', 'sécret': 'secret'
        }
        
        # Mapping termes techniques → termes visuels
        self.visual_mapping = {
            'technologie': 'future tech',
            'innovation': 'invention breakthrough',
            'recherche': 'discovery experiment', 
            'psychologie': 'mind brain psychology',
            'argent': 'money success wealth',
            'santé': 'health fitness medicine',
            'science': 'science experiment',
            'militaire': 'military defense army',
            'persuasion': 'influence mind control',
            'défense': 'security protection',
            'espionnage': 'spy surveillance',
            'données': 'data analytics'
        }

    def extract_keywords_from_content(self, content_data: Dict) -> List[str]:
        """Extrait des mots-clés pertinents du script et titre"""
        script = content_data.get('script', '')
        title = content_data.get('title', '')
        category = content_data.get('category', 'general')
        
        print(f"🧠 Analyse du contenu: {title[:50]}...")
        
        # Combiner script et titre pour plus de contexte
        full_text = title + " " + script
        
        # Extraction des mots significatifs
        words = re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', full_text.lower())
        meaningful_words = [w for w in words if w not in self.stop_words]
        
        # Comptage de fréquence
        word_freq = {}
        for word in meaningful_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Prendre les 12 mots les plus fréquents
        top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:12]
        keywords = [word for word, freq in top_words]
        
        print(f"   📊 Mots-clés bruts: {keywords}")
        return keywords

    def optimize_search_terms(self, keywords: List[str], content_data: Dict) -> List[str]:
        """Transforme les mots-clés en termes optimisés pour GIFs"""
        category = content_data.get('category', 'general')
        is_part1 = content_data.get('is_part1', True)
        title = content_data.get('title', '')
        
        optimized_terms = []
        
        # Traduire et mapper chaque mot-clé
        for keyword in keywords:
            # Traduction français → anglais
            english_term = self.fr_to_en.get(keyword.lower(), keyword.lower())
            optimized_terms.append(english_term)
            
            # Ajouter le mapping visuel si disponible
            visual_term = self.visual_mapping.get(keyword.lower())
            if visual_term:
                optimized_terms.extend(visual_term.split())
        
        # Ajouter des termes de catégorie
        category_terms = self._get_category_terms(category)
        optimized_terms.extend(category_terms)
        
        # Ajouter des termes émotionnels basés sur le titre
        emotional_terms = self._extract_emotional_terms(title, is_part1)
        optimized_terms.extend(emotional_terms)
        
        # Dédupliquer
        unique_terms = list(dict.fromkeys(optimized_terms))
        
        # Mélanger pour variété
        random.shuffle(unique_terms)
        
        print(f"   🎯 Termes optimisés: {unique_terms[:10]}")
        return unique_terms[:10]

    def _get_category_terms(self, category: str) -> List[str]:
        """Retourne des termes spécifiques à la catégorie"""
        category_terms = {
            'technologie': ['technology', 'future', 'innovation', 'robot', 'AI', 'digital', 'tech', 'gadget'],
            'science': ['science', 'discovery', 'experiment', 'research', 'physics', 'chemistry', 'biology'],
            'psychologie': ['psychology', 'mind', 'brain', 'behavior', 'emotion', 'thought', 'psychology'],
            'argent_business': ['money', 'success', 'business', 'wealth', 'rich', 'profit', 'entrepreneur'],
            'sante_bienetre': ['health', 'fitness', 'medicine', 'body', 'wellness', 'nutrition', 'fitness']
        }
        return category_terms.get(category, ['amazing', 'interesting'])

    def _extract_emotional_terms(self, title: str, is_part1: bool) -> List[str]:
        """Extrait le ton émotionnel du titre"""
        title_lower = title.lower()
        
        emotional_terms = []
        
        # Détection du ton basé sur les mots-clés brainrot
        if any(word in title_lower for word in ['choc', 'choquant', 'explosif', 'incroyable', '🔥', '💥']):
            emotional_terms.extend(['shocking', 'mindblowing', 'epic', 'explosion', 'amazing'])
        
        if any(word in title_lower for word in ['secret', 'caché', 'mystère', 'révélation', '🚨']):
            emotional_terms.extend(['secret', 'mystery', 'reveal', 'hidden', 'confidential'])
        
        if any(word in title_lower for word in ['meilleur', 'ultime', 'final', 'suprême', '🎯']):
            emotional_terms.extend(['ultimate', 'best', 'final', 'top', 'perfect'])
        
        if any(word in title_lower for word in ['dangereux', 'interdit', 'extrême', '💀']):
            emotional_terms.extend(['dangerous', 'extreme', 'intense', 'action', 'warning'])
        
        # Termes spécifiques selon la partie
        if is_part1:
            emotional_terms.extend(['mystery', 'secret', 'intrigue', 'suspense'])
        else:
            emotional_terms.extend(['revelation', 'final', 'ultimate', 'conclusion', 'surprise'])
        
        return emotional_terms

    def get_brainrot_gifs(self, content_data: Dict, num_gifs: int = 6) -> List[str]:
        """Recherche intelligente de GIFs basée sur l'analyse du contenu"""
        
        print(f"🎯 RECHERCHE GIFs INTELLIGENTE")
        print(f"   📝 Titre: {content_data.get('title', '')[:60]}...")
        print(f"   📊 Catégorie: {content_data.get('category', 'N/A')}")
        
        # Étape 1: Extraction des mots-clés
        keywords = self.extract_keywords_from_content(content_data)
        
        # Étape 2: Optimisation des termes de recherche
        search_terms = self.optimize_search_terms(keywords, content_data)
        
        # Étape 3: Recherche avec les termes optimisés
        gif_urls = self._search_with_terms(search_terms, num_gifs, content_data)
        
        # Étape 4: Fallback si nécessaire
        if not gif_urls:
            print("   🔄 Fallback: recherche générique...")
            gif_urls = self._fallback_search(content_data, num_gifs)
        
        print(f"🎉 GIFs trouvés: {len(gif_urls)}")
        return gif_urls[:num_gifs]

    def _search_with_terms(self, search_terms: List[str], num_gifs: int, content_data: Dict) -> List[str]:
        """Recherche avec les termes optimisés"""
        gif_urls = []
        is_part1 = content_data.get('is_part1', True)
        
        # Prioriser les termes les plus prometteurs
        prioritized_terms = self._prioritize_terms(search_terms, is_part1)
        
        for search_term in prioritized_terms[:6]:  # Essayer les 6 premiers termes
            if len(gif_urls) >= num_gifs:
                break
                
            print(f"   🔍 Recherche: '{search_term}'")
            
            # Essayer plusieurs subreddits pour ce terme
            subreddits_to_try = random.sample(self.best_subreddits, min(4, len(self.best_subreddits)))
            
            for subreddit in subreddits_to_try:
                if len(gif_urls) >= num_gifs:
                    break
                    
                found_gifs = self._search_subreddit_optimized(subreddit, search_term, 2)
                if found_gifs:
                    gif_urls.extend(found_gifs)
                    print(f"      ✅ r/{subreddit}: {len(found_gifs)} GIFs")
                
                time.sleep(self.rate_limit_delay)
        
        return gif_urls

    def _prioritize_terms(self, terms: List[str], is_part1: bool) -> List[str]:
        """Priorise les termes de recherche"""
        # Termes émotionnels en premier (meilleurs pour GIFs)
        emotional_keywords = ['shocking', 'mindblowing', 'epic', 'amazing', 'awesome', 'incredible']
        
        prioritized = []
        
        # Ajouter d'abord les termes émotionnels présents
        for emotional in emotional_keywords:
            if emotional in terms:
                prioritized.append(emotional)
        
        # Ajouter les autres termes
        for term in terms:
            if term not in prioritized:
                prioritized.append(term)
        
        return prioritized

    def _search_subreddit_optimized(self, subreddit: str, search_term: str, limit: int) -> List[str]:
        """Recherche optimisée dans un subreddit"""
        try:
            url = f"https://www.reddit.com/r/{subreddit}/search.json"
            params = {
                'q': search_term,
                'restrict_sr': 'on',
                'sort': 'top',  # Top posts pour meilleure qualité
                't': 'month',   # Dernier mois pour contenu frais
                'limit': limit * 3  # Plus de résultats pour mieux filtrer
            }
            headers = {'User-Agent': self.user_agent}
            
            response = requests.get(url, params=params, headers=headers, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                return self._extract_quality_gifs_optimized(data)
            elif response.status_code == 429:
                print(f"      ⏳ Rate limit, attente...")
                time.sleep(2)
                
        except Exception as e:
            print(f"      ❌ Erreur r/{subreddit}: {e}")
        
        return []

    def _extract_quality_gifs_optimized(self, data: dict) -> List[str]:
        """Extraction de GIFs avec filtres optimisés"""
        gif_urls = []
        
        if 'data' not in data or 'children' not in data['data']:
            return gif_urls
        
        for post in data['data']['children']:
            post_data = post.get('data', {})
            
            # FILTRES OPTIMISÉS (beaucoup plus permissifs)
            score = post_data.get('score', 0)
            if score < 10:  # Seulement 10 upvotes minimum (au lieu de 50)
                continue
            
            url = post_data.get('url', '')
            
            # Accepter plus de types de contenu
            if (url.endswith('.gif') or 
                'gif' in url.lower() or 
                'redgifs' in url or
                'imgur' in url and any(ext in url for ext in ['.gif', '.gifv'])):
                
                # Éviter les URLs de preview basse qualité
                if 'preview' not in url and not url.endswith('.gifv'):
                    gif_urls.append(url)
        
        return gif_urls[:5]  # Limiter à 5 par recherche

    def _fallback_search(self, content_data: Dict, num_gifs: int) -> List[str]:
        """Recherche de fallback avec termes génériques"""
        category = content_data.get('category', 'general')
        is_part1 = content_data.get('is_part1', True)
        
        # Termes de fallback par catégorie
        fallback_terms = {
            'technologie': ['technology', 'future tech', 'innovation', 'digital'],
            'science': ['science', 'discovery', 'experiment', 'research'],
            'psychologie': ['psychology', 'mind', 'brain', 'emotion'],
            'general': ['amazing', 'interesting', 'cool', 'awesome']
        }
        
        terms = fallback_terms.get(category, fallback_terms['general'])
        
        # Adapter selon la partie
        if is_part1:
            terms.extend(['mystery', 'secret'])
        else:
            terms.extend(['revelation', 'final'])
        
        gif_urls = []
        for term in terms[:4]:
            if len(gif_urls) >= num_gifs:
                break
                
            subreddit = random.choice(self.best_subreddits)
            found_gifs = self._search_subreddit_optimized(subreddit, term, 2)
            gif_urls.extend(found_gifs)
        
        return gif_urls

# Instance globale
brainrot_gif_provider = BrainrotGIFProvider()

def get_brainrot_gifs(content_data: Dict, num_gifs: int = 6) -> List[str]:
    """Fonction principale pour récupérer des GIFs intelligents"""
    return brainrot_gif_provider.get_brainrot_gifs(content_data, num_gifs)
