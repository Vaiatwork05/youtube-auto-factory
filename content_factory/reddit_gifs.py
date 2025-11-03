# content_factory/reddit_gifs.py (VERSION ULTIME - CHASSEUR DE GIFS)

import os
import re
import time
import random
import requests
import json
from typing import List, Dict, Optional
from urllib.parse import quote

class UltimateGIFHunter:
    """Chasseur de GIFs ultime avec recherche persistante et sources multiples."""
    
    def __init__(self):
        # SUBREDDITS GARANTIS avec contenu GIF actif
        self.guaranteed_subreddits = [
            "gifs", "reactiongifs", "highqualitygifs", "perfectloops",
            "interestingasfuck", "beamazed", "nextfuckinglevel", "woahdude",
            "blackmagicfuckery", "educationalgifs", "chemicalreactiongifs"
        ]
        
        self.user_agent = "YouTubeBrainrotFactory/2.0"
        self.rate_limit_delay = 0.5
        self.max_attempts_per_term = 3
        
        # Sources alternatives
        self.gif_sources = [
            self._search_reddit_aggressive,
            self._search_giphy_fallback,
            self._search_tenor_fallback,
            self._get_local_fallback_gifs
        ]
        
        # Cache pour éviter les recherches répétées
        self.search_cache = {}
        
        print("🎯 UltimateGIFHunter initialisé - Recherche persistante activée")

    def hunt_gifs_persistently(self, content_data: Dict, target_count: int = 8, max_total_attempts: int = 20) -> List[str]:
        """
        Recherche PERSISTANTE de GIFs jusqu'à atteindre la cible ou épuiser les tentatives.
        """
        print(f"\n🎯 DÉBUT CHASSE AUX GIFS PERSISTANTE")
        print(f"   📝 Titre: {content_data.get('title', '')[:50]}...")
        print(f"   🎯 Cible: {target_count} GIFs | Max tentatives: {max_total_attempts}")
        
        all_gifs = []
        total_attempts = 0
        consecutive_failures = 0
        
        # Étape 1: Générer les termes de recherche
        search_terms = self._generate_search_terms(content_data)
        print(f"   🔍 Termes de recherche: {search_terms}")
        
        # Étape 2: Recherche PERSISTANTE avec toutes les sources
        while len(all_gifs) < target_count and total_attempts < max_total_attempts:
            term = random.choice(search_terms)
            source = random.choice(self.gif_sources)
            
            print(f"   🎯 Tentative {total_attempts + 1}: '{term}' avec {source.__name__}")
            
            try:
                found_gifs = source(term, content_data)
                
                if found_gifs:
                    new_gifs = [g for g in found_gifs if g not in all_gifs]
                    all_gifs.extend(new_gifs)
                    consecutive_failures = 0
                    print(f"      ✅ Trouvé {len(new_gifs)} nouveaux GIFs (total: {len(all_gifs)})")
                else:
                    consecutive_failures += 1
                    print(f"      ❌ Aucun GIF trouvé (échecs consécutifs: {consecutive_failures})")
                
            except Exception as e:
                print(f"      ⚠️ Erreur: {e}")
                consecutive_failures += 1
            
            total_attempts += 1
            
            # Pause stratégique
            time.sleep(self.rate_limit_delay)
            
            # Si trop d'échecs consécutifs, changer de stratégie
            if consecutive_failures >= 5:
                print("      🔄 Trop d'échecs, changement de stratégie...")
                search_terms = self._get_emergency_terms(content_data)
                consecutive_failures = 0
        
        # Étape 3: Résultat final
        final_gifs = all_gifs[:target_count]
        print(f"\n🎉 CHASSE TERMINÉE: {len(final_gifs)} GIFs trouvés après {total_attempts} tentatives")
        
        return final_gifs

    def _generate_search_terms(self, content_data: Dict) -> List[str]:
        """Génère une large gamme de termes de recherche"""
        title = content_data.get('title', '').lower()
        category = content_data.get('category', 'general')
        is_part1 = content_data.get('is_part1', True)
        
        terms = []
        
        # Termes basés sur le titre (extraction agressive)
        words = re.findall(r'\b[a-zA-ZÀ-ÿ]{4,}\b', title)
        terms.extend(words[:8])  # Prendre plus de mots
        
        # Termes de catégorie étendus
        category_terms = self._get_extended_category_terms(category)
        terms.extend(category_terms)
        
        # Termes émotionnels brainrot
        emotional_terms = self._get_emotional_terms(title, is_part1)
        terms.extend(emotional_terms)
        
        # Termes génériques garantis
        generic_terms = ['amazing', 'awesome', 'cool', 'interesting', 'mindblowing', 'epic']
        terms.extend(generic_terms)
        
        # Dédupliquer et mélanger
        unique_terms = list(dict.fromkeys(terms))
        random.shuffle(unique_terms)
        
        return unique_terms[:15]  # Retourner plus de termes

    def _get_extended_category_terms(self, category: str) -> List[str]:
        """Termes de catégorie très étendus"""
        extended_terms = {
            'technologie': [
                'technology', 'future', 'innovation', 'robot', 'AI', 'digital', 'tech', 
                'gadget', 'computer', 'software', 'hardware', 'internet', 'smartphone',
                'virtual reality', 'augmented reality', 'cyber', 'code', 'programming'
            ],
            'science': [
                'science', 'discovery', 'experiment', 'research', 'physics', 'chemistry',
                'biology', 'space', 'universe', 'planet', 'laboratory', 'microscope',
                'invention', 'breakthrough', 'scientist', 'theory', 'hypothesis'
            ],
            'psychologie': [
                'psychology', 'mind', 'brain', 'behavior', 'emotion', 'thought', 'cognitive',
                'psychology', 'mental', 'intelligence', 'memory', 'learning', 'perception',
                'consciousness', 'subconscious', 'behavioral', 'therapy'
            ],
            'histoire': [
                'history', 'ancient', 'medieval', 'renaissance', 'revolution', 'war',
                'empire', 'civilization', 'archeology', 'artifact', 'monument',
                'pyramid', 'castle', 'knight', 'explorer', 'discovery'
            ]
        }
        return extended_terms.get(category, ['amazing', 'interesting', 'cool'])

    def _get_emotional_terms(self, title: str, is_part1: bool) -> List[str]:
        """Termes émotionnels très étendus"""
        terms = []
        
        # Détection large d'émotions
        emotional_patterns = {
            'shock': ['shocking', 'mindblowing', 'epic', 'explosive', 'jawdropping'],
            'mystery': ['mystery', 'secret', 'hidden', 'confidential', 'classified'],
            'success': ['success', 'achievement', 'victory', 'triumph', 'winning'],
            'danger': ['dangerous', 'extreme', 'intense', 'thrilling', 'adventure'],
            'future': ['future', 'futuristic', 'advanced', 'cutting edge', 'innovative']
        }
        
        title_lower = title.lower()
        for emotion, emotion_terms in emotional_patterns.items():
            if any(word in title_lower for word in [emotion] + emotion_terms[:2]):
                terms.extend(emotion_terms)
        
        # Ajouter tous les termes émotionnels de base
        terms.extend(['amazing', 'awesome', 'incredible', 'unbelievable', 'fantastic'])
        
        return terms

    def _search_reddit_aggressive(self, search_term: str, content_data: Dict) -> List[str]:
        """Recherche Reddit AGGRESSIVE avec nombreux subreddits"""
        gif_urls = []
        
        # Essayer plusieurs subreddits pour le même terme
        subreddits_to_try = random.sample(self.guaranteed_subreddits, 
                                        min(6, len(self.guaranteed_subreddits)))
        
        for subreddit in subreddits_to_try:
            if len(gif_urls) >= 5:  # Limite par terme
                break
                
            try:
                found_gifs = self._search_single_subreddit(subreddit, search_term)
                if found_gifs:
                    gif_urls.extend(found_gifs)
                    print(f"      ✅ r/{subreddit}: {len(found_gifs)} GIFs")
                
            except Exception as e:
                print(f"      ❌ r/{subreddit} échoué: {e}")
            
            time.sleep(self.rate_limit_delay)
        
        return gif_urls

    def _search_single_subreddit(self, subreddit: str, search_term: str) -> List[str]:
        """Recherche dans un seul subreddit avec filtres MINIMAUX"""
        try:
            url = f"https://www.reddit.com/r/{subreddit}/search.json"
            params = {
                'q': search_term,
                'restrict_sr': 'on',
                'sort': 'relevance',  # Relevance pour meilleurs résultats
                't': 'year',         # Année entière pour plus de contenu
                'limit': 25          # Beaucoup de résultats
            }
            headers = {'User-Agent': self.user_agent}
            
            response = requests.get(url, params=params, headers=headers, timeout=25)
            
            if response.status_code == 200:
                return self._extract_gifs_aggressive(response.json())
            elif response.status_code == 429:
                print("      ⏳ Rate limit Reddit, pause...")
                time.sleep(3)
                
        except Exception as e:
            print(f"      🌐 Erreur réseau: {e}")
        
        return []

    def _extract_gifs_aggressive(self, data: dict) -> List[str]:
        """Extraction AGGRESSIVE de GIFs - filtres MINIMAUX"""
        gif_urls = []
        
        if 'data' not in data or 'children' not in data['data']:
            return gif_urls
        
        for post in data['data']['children']:
            post_data = post.get('data', {})
            
            # FILTRES TRÈS PERMISSIFS
            score = post_data.get('score', 0)
            if score < 5:  # Seulement 5 upvotes minimum !
                continue
            
            url = post_data.get('url', '')
            
            # Accepter TOUS les types de GIFs possibles
            if (url.endswith('.gif') or 
                '.gif?' in url or
                'gif' in url.lower() or 
                'redgifs' in url or
                'imgur' in url or
                'gfycat' in url):
                
                # Nettoyer l'URL si nécessaire
                clean_url = self._clean_gif_url(url)
                if clean_url and clean_url not in gif_urls:
                    gif_urls.append(clean_url)
        
        return gif_urls[:8]  # Retourner plus de résultats

    def _clean_gif_url(self, url: str) -> str:
        """Nettoie et normalise l'URL GIF"""
        # Convertir GIFV en GIF
        if url.endswith('.gifv'):
            return url.replace('.gifv', '.gif')
        
        # Nettoyer les URLs Imgur
        if 'imgur.com' in url and not url.endswith('.gif'):
            if '/gallery/' not in url:  # Éviter les galleries
                return url + '.gif'
        
        return url

    def _search_giphy_fallback(self, search_term: str, content_data: Dict) -> List[str]:
        """Fallback Giphy (sans API key - utilisation publique)"""
        try:
            print(f"      🎭 Essai Giphy: '{search_term}'")
            
            # Utiliser l'API publique Giphy
            url = "https://api.giphy.com/v1/gifs/search"
            params = {
                'q': search_term,
                'limit': 10,
                'rating': 'pg-13',
                'api_key': 'dc6zaTOxFJmzC'  # Clé publique beta
            }
            
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                gif_urls = []
                
                for gif in data.get('data', [])[:5]:
                    original_url = gif.get('images', {}).get('original', {}).get('url')
                    if original_url:
                        gif_urls.append(original_url)
                
                return gif_urls
                
        except Exception as e:
            print(f"      ❌ Giphy échoué: {e}")
        
        return []

    def _search_tenor_fallback(self, search_term: str, content_data: Dict) -> List[str]:
        """Fallback Tenor (sans API key)"""
        try:
            print(f"      🎵 Essai Tenor: '{search_term}'")
            
            # Recherche via page publique (fallback basique)
            search_url = f"https://tenor.com/search/{quote(search_term)}-gifs"
            headers = {'User-Agent': self.user_agent}
            
            response = requests.get(search_url, headers=headers, timeout=15)
            if response.status_code == 200:
                # Extraction basique des URLs GIF (méthode simplifiée)
                gif_pattern = r'https://[^"\']*\.gif[^"\']*'
                gif_urls = re.findall(gif_pattern, response.text)
                return gif_urls[:5]
                
        except Exception as e:
            print(f"      ❌ Tenor échoué: {e}")
        
        return []

    def _get_local_fallback_gifs(self, search_term: str, content_data: Dict) -> List[str]:
        """Fallback local avec GIFs de qualité pré-téléchargés"""
        print(f"      🏠 Fallback local activé")
        
        # URLs de GIFs de qualité libre de droits (remplacer par tes propres URLs)
        quality_fallback_gifs = [
            "https://media.giphy.com/media/26uf759LlDftqZNVm/giphy.gif",  # Science
            "https://media.giphy.com/media/l0HlN3i2mR8XqlPDK/giphy.gif",  # Technology
            "https://media.giphy.com/media/3o7abKhOpu0NwenH3O/giphy.gif", # Brain
            "https://media.giphy.com/media/xULW8N9O5WDQYgKk6A/giphy.gif", # Digital
            "https://media.giphy.com/media/26AHPxxnSw1L9T1rW/giphy.gif",  # Innovation
            "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",  # Future
            "https://media.giphy.com/media/3o72FfM5HJydzafgUE/giphy.gif", # Discovery
            "https://media.giphy.com/media/26uf2ZNnL7bN4xZLW/giphy.gif",  # Success
        ]
        
        # Mélanger et retourner quelques GIFs
        random.shuffle(quality_fallback_gifs)
        return quality_fallback_gifs[:4]

    def _get_emergency_terms(self, content_data: Dict) -> List[str]:
        """Termes d'urgence quand tout échoue"""
        emergency_terms = [
            'amazing', 'awesome', 'cool', 'interesting', 'mindblowing',
            'epic', 'fantastic', 'incredible', 'unbelievable', 'wow',
            'great', 'perfect', 'best', 'top', 'quality'
        ]
        
        # Ajouter quelques termes aléatoires
        random.shuffle(emergency_terms)
        return emergency_terms[:10]

# Instance globale
ultimate_gif_hunter = UltimateGIFHunter()

def get_brainrot_gifs(content_data: Dict, num_gifs: int = 8) -> List[str]:
    """
    Fonction principale - Recherche PERSISTANTE de GIFs.
    Continue jusqu'à trouver ou épuiser 25 tentatives.
    """
    return ultimate_gif_hunter.hunt_gifs_persistently(
        content_data, 
        target_count=num_gifs,
        max_total_attempts=25  # Beaucoup de tentatives !
    )

# Test de la fonction
if __name__ == "__main__":
    print("🧪 TEST ULTIMATE GIF HUNTER")
    
    test_content = {
        'title': 'LES 10 SECRETS TECHNOLOGIQUES QUE LES GÉANTS CACHENT (PARTIE 1)',
        'script': 'Découvrez les révélations choquantes sur la technologie moderne...',
        'category': 'technologie',
        'is_part1': True
    }
    
    start_time = time.time()
    gifs = get_brainrot_gifs(test_content, 6)
    end_time = time.time()
    
    print(f"\n🎉 RÉSULTAT TEST:")
    print(f"⏱️ Temps: {end_time - start_time:.1f}s")
    print(f"📊 GIFs trouvés: {len(gifs)}")
    
    for i, gif_url in enumerate(gifs, 1):
        print(f"   {i}. {gif_url[:80]}...")
