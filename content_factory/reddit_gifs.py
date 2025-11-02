# content_factory/reddit_gifs.py

import requests
import random
import time
import re
from typing import List, Dict, Optional

class BrainrotGIFProvider:
    """Fournisseur de GIFs Reddit optimisé pour contenu BRAINROT TOP 10"""
    
    def __init__(self):
        # SUBREDDITS SPÉCIALISÉS POUR CONTENU BRAINROT
        self.subreddits_by_category = {
            "science": [
                "educationalgifs", "physicsgifs", "chemicalreactiongifs",
                "sciencegifs", "spacegifs", "biologygifs", "astronomygifs"
            ],
            "technologie": [
                "technologygifs", "programming", "futurology", "cyberpunk",
                "artificial", "roboticsgifs", "techsupportgore", "softwaregore"
            ],
            "sante_bienetre": [
                "medicalgifs", "fitgifs", "workoutgifs", "nutritiongifs",
                "medicine", "healthygifs", "fitnessgifs"
            ],
            "psychologie": [
                "psychology", "mindfulness", "cognitivegifs", "behaviorgifs",
                "neurosciencegifs", "brainygifs"
            ],
            "argent_business": [
                "businessgifs", "successgifs", "moneygifs", "entrepreneurgifs",
                "investinggifs", "marketinggifs", "productivitygifs"
            ],
            "reactions": [
                "reactiongifs", "perfectreactiongifs", "surprisedgifs",
                "shockedgifs", "mindblowngifs", "wtfgifs", "holyshitgifs"
            ],
            "brainrot_specials": [
                "interestingasfuck", "beamazed", "nextfuckinglevel",
                "blackmagicfuckery", "blackmagic", "illusionporn",
                "woahdude", "trippy", "fascinating"
            ]
        }
        
        self.user_agent = "YouTubeBrainrotFactory/1.0"
        self.rate_limit_delay = 0.7

    def get_brainrot_gifs(self, content_data: Dict, num_gifs: int = 6) -> List[str]:
        """Récupère des GIFs parfaitement adaptés au contenu BRAINROT"""
        
        category = content_data.get('category', 'science')
        is_part1 = content_data.get('is_part1', True)
        keywords = content_data.get('keywords', [])
        title = content_data.get('title', '')
        
        print(f"🎯 BRAINROT GIFs pour: {title}")
        print(f"   📊 Catégorie: {category} | Partie: {'1' if is_part1 else '2'}")
        
        # Stratégie différente selon la partie
        if is_part1:
            # Partie 1: GIFs intrigants et mystérieux
            gif_urls = self._get_intrigue_gifs(category, num_gifs)
        else:
            # Partie 2: GIFs explosifs et choquants
            gif_urls = self._get_shock_gifs(category, num_gifs)
        
        # Fallback: GIFs de réactions si pas assez
        if len(gif_urls) < num_gifs:
            reaction_gifs = self._get_reaction_gifs(num_gifs - len(gif_urls))
            gif_urls.extend(reaction_gifs)
            print(f"   😄 Ajout {len(reaction_gifs)} GIFs réactions")
        
        print(f"🎉 Total GIFs BRAINROT: {len(gif_urls)}")
        return gif_urls[:num_gifs]

    def _get_intrigue_gifs(self, category: str, limit: int) -> List[str]:
        """GIFs pour créer du mystère et de l'intrigue (Partie 1)"""
        search_terms = [
            "mystery", "secret", "hidden", "discovery", "reveal",
            "illusion", "magic", "unexplained", "paradox", "enigma"
        ]
        
        gif_urls = []
        
        # Recherche dans les subreddits brainrot spéciaux
        for subreddit in self.subreddits_by_category['brainrot_specials']:
            if len(gif_urls) >= limit:
                break
                
            term = random.choice(search_terms)
            gifs = self._search_subreddit(subreddit, term, 2)
            gif_urls.extend(gifs)
            print(f"   🔍 r/{subreddit} '{term}': {len(gifs)} GIFs")
            time.sleep(self.rate_limit_delay)
        
        return gif_urls[:limit]

    def _get_shock_gifs(self, category: str, limit: int) -> List[str]:
        """GIFs pour créer du choc et de la surprise (Partie 2)"""
        search_terms = [
            "shocking", "explosion", "surprise", "mindblowing", "unbelievable",
            "impossible", "shock", "revelation", "breakthrough", "revolution"
        ]
        
        gif_urls = []
        
        # Recherche dans la catégorie + brainrot
        subreddits = self.subreddits_by_category.get(category, []) + \
                    self.subreddits_by_category['brainrot_specials']
        
        for subreddit in subreddits[:4]:  # Top 4 subreddits
            if len(gif_urls) >= limit:
                break
                
            term = random.choice(search_terms)
            gifs = self._search_subreddit(subreddit, term, 2)
            gif_urls.extend(gifs)
            print(f"   💥 r/{subreddit} '{term}': {len(gifs)} GIFs")
            time.sleep(self.rate_limit_delay)
        
        return gif_urls[:limit]

    def _get_reaction_gifs(self, limit: int) -> List[str]:
        """GIFs de réactions émotionnelles pour renforcer l'impact"""
        try:
            subreddits = self.subreddits_by_category['reactions']
            all_gifs = []
            
            for subreddit in subreddits[:3]:
                url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=15"
                headers = {'User-Agent': self.user_agent}
                
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    gifs = self._extract_gifs_from_data(data)
                    all_gifs.extend(gifs)
                    print(f"   😲 r/{subreddit}: {len(gifs)} réactions")
                
                time.sleep(self.rate_limit_delay)
            
            return random.sample(all_gifs, min(limit, len(all_gifs)))
            
        except Exception as e:
            print(f"   ⚠️ Erreur réactions: {e}")
            return []

    def _search_subreddit(self, subreddit: str, search_term: str, limit: int) -> List[str]:
        """Recherche dans un subreddit spécifique"""
        try:
            url = f"https://www.reddit.com/r/{subreddit}/search.json"
            params = {
                'q': search_term,
                'restrict_sr': 'on',
                'sort': 'top',
                't': 'month',
                'limit': limit * 3
            }
            headers = {'User-Agent': self.user_agent}
            
            response = requests.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                return self._extract_quality_gifs(data)
            elif response.status_code == 429:
                time.sleep(2)
                
        except Exception as e:
            print(f"      ⚠️ Erreur r/{subreddit}: {e}")
        
        return []

    def _extract_quality_gifs(self, data: dict) -> List[str]:
        """Extrait les GIFs de qualité avec filtres BRAINROT"""
        gif_urls = []
        
        if 'data' not in data or 'children' not in data['data']:
            return gif_urls
        
        for post in data['data']['children']:
            post_data = post.get('data', {})
            
            # Filtre de qualité BRAINROT
            score = post_data.get('score', 0)
            if score < 50:  # Seulement le contenu populaire
                continue
            
            url = post_data.get('url', '')
            
            # Accepte les GIFs et certaines images animées
            if (url.endswith('.gif') or 
                'gif' in url.lower() or 
                'redgifs' in url or
                self._is_animated_content(post_data)):
                
                # Évite les URLs de preview basse qualité
                if 'preview' not in url and not url.endswith('.gifv'):
                    gif_urls.append(url)
        
        return gif_urls[:5]  # Max 5 par recherche

    def _extract_gifs_from_data(self, data: dict) -> List[str]:
        """Extraction simple pour les flux hot"""
        gif_urls = []
        
        if 'data' not in data or 'children' not in data['data']:
            return gif_urls
        
        for post in data['data']['children']:
            post_data = post.get('data', {})
            url = post_data.get('url', '')
            
            if url.endswith('.gif') and post_data.get('score', 0) > 20:
                gif_urls.append(url)
        
        return gif_urls

    def _is_animated_content(self, post_data: dict) -> bool:
        """Détecte le contenu animé"""
        url = post_data.get('url', '').lower()
        post_hint = post_data.get('post_hint', '')
        
        return (post_hint in ['image', 'rich:video'] or
                'giphy' in url or
                'tenor' in url or
                'imgur' in url and '.gif' in url)

# Instance globale
brainrot_gif_provider = BrainrotGIFProvider()

def get_brainrot_gifs(content_data: Dict, num_gifs: int = 6) -> List[str]:
    """Fonction principale pour récupérer des GIFs BRAINROT"""
    return brainrot_gif_provider.get_brainrot_gifs(content_data, num_gifs)
