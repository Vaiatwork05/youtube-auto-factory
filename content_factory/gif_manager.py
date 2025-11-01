# content_factory/gif_manager.py
import os
import requests
import random
import time
from typing import List, Dict, Any, Optional
from PIL import Image, ImageSequence
import json

from content_factory.utils import safe_path_join, ensure_directory
from content_factory.config_loader import ConfigLoader

class GifManager:
    """Gère la recherche et téléchargement de GIFs depuis GIPHY avec fallback intelligent."""
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.api_key = os.getenv('GIPHY_API_KEY', 'dc6zaTOxFJmzC')  # Clé publique de démo
        self.base_url = "https://api.giphy.com/v1/gifs"
        
        # Dossiers de sortie
        output_root = self.config.get('PATHS', {}).get('OUTPUT_ROOT', 'output')
        self.gif_dir = safe_path_join(output_root, 'gifs')
        self.cache_dir = safe_path_join(output_root, 'cache/gifs')
        ensure_directory(self.gif_dir)
        ensure_directory(self.cache_dir)
        
        # Cache pour éviter les appels API répétés
        self.search_cache = {}
        
        # Mapping thématique intelligent français → anglais
        self.theme_mapping = {
            # Psychologie & Comportement
            'psychologie': ['psychology', 'brain', 'mind', 'thinking', 'behavior analysis'],
            'mental': ['mental health', 'therapy', 'psychology', 'mind'],
            'cerveau': ['brain', 'neuroscience', 'intelligence', 'thinking'],
            
            # Langage Corporel
            'langage corporel': ['body language', 'nonverbal communication', 'gestures'],
            'geste': ['gesture', 'hand gesture', 'body movement'],
            'posture': ['posture', 'body posture', 'standing'],
            'expression faciale': ['facial expression', 'emotion face', 'reaction'],
            
            # Émotions & Réactions
            'émotion': ['emotion', 'feeling', 'emotional', 'mood'],
            'réaction': ['reaction', 'surprised', 'shocked', 'amazed'],
            'surprise': ['surprise', 'shock', 'amazement', 'wow'],
            'choquant': ['shocking', 'mind blowing', 'unbelievable', 'amazing'],
            
            # Communication
            'communication': ['communication', 'talking', 'speaking', 'conversation'],
            'parler': ['talking', 'speaking', 'communication', 'discussion'],
            'écouter': ['listening', 'active listening', 'attention'],
            
            # Révélations & Secrets
            'secret': ['secret', 'hidden', 'confidential', 'mystery'],
            'caché': ['hidden', 'secret', 'concealed', 'unknown'],
            'révélation': ['revelation', 'discovery', 'truth', 'expose'],
            'découverte': ['discovery', 'finding', 'breakthrough', 'reveal'],
            
            # Éducation & Apprentissage
            'éducation': ['education', 'learning', 'teaching', 'knowledge'],
            'apprentissage': ['learning', 'studying', 'education', 'knowledge'],
            'conseil': ['advice', 'tip', 'counseling', 'guidance'],
            'astuce': ['tip', 'trick', 'hack', 'advice'],
            
            # Viral & Tendance
            'viral': ['viral', 'trending', 'popular', 'internet'],
            'tendance': ['trend', 'popular', 'viral', 'hot'],
            'meme': ['meme', 'funny', 'internet', 'viral']
        }

    def search_gifs(self, content_data: Dict[str, Any], num_gifs: int = 8) -> List[str]:
        """Recherche des GIFs pertinents basés sur le contenu avec fallback robuste."""
        print("🎬 Recherche de GIFs GIPHY...")
        
        # Vérification API key
        if not self.api_key or self.api_key == 'dc6zaTOxFJmzC':
            print("⚠️  Clé GIPHY limitée (mode démo) - qualité réduite")
        
        try:
            # 1. Extraction mots-clés intelligents
            keywords = self._extract_smart_keywords(content_data)
            print(f"🔍 Mots-clés optimisés: {keywords}")
            
            if not keywords:
                print("❌ Aucun mot-clé valide - utilisation fallback")
                return self._get_fallback_gifs(content_data, num_gifs)
            
            # 2. Recherche par pertinence avec cache
            gif_urls = []
            for keyword in keywords[:4]:  # 4 meilleurs mots-clés max
                if len(gif_urls) >= num_gifs:
                    break
                    
                cached_urls = self._get_cached_search(keyword)
                if cached_urls:
                    gif_urls.extend(cached_urls[:3])
                    print(f"   💾 '{keyword}': {len(cached_urls)} GIFs (cache)")
                else:
                    urls = self._search_giphy(keyword, min(4, num_gifs - len(gif_urls)))
                    gif_urls.extend(urls)
                    self._cache_search(keyword, urls)
            
            # 3. Téléchargement avec gestion d'erreurs
            downloaded_gifs = []
            max_retries = 2
            
            for i, url in enumerate(gif_urls[:num_gifs]):
                for attempt in range(max_retries):
                    gif_path = self._download_gif(url, f"gif_{i+1}_{int(time.time())}")
                    if gif_path:
                        # Vérification que le GIF est valide
                        if self._validate_gif(gif_path):
                            downloaded_gifs.append(gif_path)
                            break
                        else:
                            os.remove(gif_path)  Supprimer GIF corrompu
                    time.sleep(0.5)  # Pause entre téléchargements
            
            # 4. Fallback si nécessaire
            if len(downloaded_gifs) < min(4, num_gifs):
                print(f"⚠️  Seulement {len(downloaded_gifs)} GIFs valides - complétion fallback")
                fallback_gifs = self._get_fallback_gifs(content_data, num_gifs - len(downloaded_gifs))
                downloaded_gifs.extend(fallback_gifs)
            
            print(f"✅ {len(downloaded_gifs)} GIFs téléchargés avec succès")
            return downloaded_gifs[:num_gifs]
            
        except Exception as e:
            print(f"❌ Erreur critique recherche GIFs: {e}")
            return self._get_fallback_gifs(content_data, num_gifs)

    def _extract_smart_keywords(self, content_data: Dict[str, Any]) -> List[str]:
        """Extrait des mots-clés optimisés pour la recherche GIF."""
        title = content_data.get('title', '').lower()
        category = content_data.get('category', '').lower()
        script = content_data.get('script', '').lower()
        original_keywords = [kw.lower() for kw in content_data.get('keywords', [])]
        
        print(f"   📝 Analyse: '{title}'")
        
        # 1. Mots-clés prioritaires selon le thème
        priority_keywords = []
        for french_term, english_terms in self.theme_mapping.items():
            if (french_term in title or 
                french_term in category or 
                any(french_term in kw for kw in original_keywords)):
                priority_keywords.extend(english_terms)
                print(f"   🎯 Thème '{french_term}' → {english_terms[:2]}")
        
        # 2. Mots-clés du titre (nettoyés et traduits)
        title_keywords = self._extract_from_title(title)
        
        # 3. Mots-clés du script (concepts principaux)
        script_keywords = self._extract_from_script(script)
        
        # 4. Combinaison intelligente avec déduplication
        all_keywords = list(set(
            priority_keywords + 
            title_keywords + 
            script_keywords + 
            [self._translate_keyword(kw) for kw in original_keywords[:3]]
        ))
        
        # 5. Filtrage qualité et pertinence
        filtered_keywords = self._filter_quality_keywords(all_keywords)
        
        print(f"   📊 Keywords: {len(priority_keywords)} priorité, {len(title_keywords)} titre, {len(script_keywords)} script → {len(filtered_keywords)} final")
        return filtered_keywords[:8]  # Maximum 8 mots-clés

    def _extract_from_title(self, title: str) -> List[str]:
        """Extrait les mots-clés les plus pertinents du titre."""
        # Supprimer les mots vides et caractères spéciaux
        stop_words = {'les', 'des', 'pour', 'dans', 'avec', 'quoi', 'qui', 'que', 'tout', 'tous'}
        words = [word for word in title.split() if len(word) > 3 and word not in stop_words]
        
        # Prioriser les mots significatifs
        significant_words = []
        for word in words:
            translated = self._translate_keyword(word)
            if translated and len(translated) > 2:
                significant_words.append(translated)
        
        return significant_words[:4]

    def _extract_from_script(self, script: str) -> List[str]:
        """Extrait les concepts principaux du script."""
        # Phrases indicatrices de concepts importants
        concept_indicators = [
            'le plus important', 'ce qu il faut savoir', 'la clé est',
            'je vais vous révéler', 'secret que', 'technique pour',
            'méthode efficace', 'astuce simple', 'conseil pratique'
        ]
        
        concepts = []
        lines = script.split('\n')
        
        for line in lines[:10]:  # Premières lignes seulement
            line_lower = line.lower()
            if any(indicator in line_lower for indicator in concept_indicators):
                # Extraire les mots significatifs de cette ligne
                words = [word for word in line_lower.split() if len(word) > 4]
                concepts.extend(words[:2])
        
        return [self._translate_keyword(c) for c in concepts[:3]]

    def _translate_keyword(self, french_word: str) -> str:
        """Traduit les mots-clés français vers anglais."""
        translation_map = {
            # Langage Corporel
            'langage': 'language', 'corps': 'body', 'corporel': 'body',
            'geste': 'gesture', 'posture': 'posture', 'attitude': 'attitude',
            'mains': 'hands', 'visage': 'face', 'yeux': 'eyes',
            'sourire': 'smile', 'regard': 'look', 'contact': 'contact',
            
            # Psychologie
            'psychologie': 'psychology', 'mental': 'mental', 'cerveau': 'brain',
            'comportement': 'behavior', 'personnalité': 'personality',
            'inconscient': 'unconscious', 'subconscient': 'subconscious',
            
            # Émotions
            'émotion': 'emotion', 'sentiment': 'feeling', 'réaction': 'reaction',
            'surprise': 'surprise', 'choquant': 'shocking', 'incroyable': 'amazing',
            'étonnant': 'astonishing', 'intéressant': 'interesting',
            
            # Communication
            'communication': 'communication', 'parler': 'talking',
            'écouter': 'listening', 'dialoguer': 'dialog', 'discuter': 'discuss',
            
            # Révélations
            'secret': 'secret', 'caché': 'hidden', 'révélation': 'revelation',
            'découverte': 'discovery', 'vérité': 'truth', 'réalité': 'reality',
            
            # Apprentissage
            'apprendre': 'learn', 'éducation': 'education', 'conseil': 'advice',
            'astuce': 'tip', 'technique': 'technique', 'méthode': 'method'
        }
        
        return translation_map.get(french_word, french_word)

    def _filter_quality_keywords(self, keywords: List[str]) -> List[str]:
        """Filtre les mots-clés pour garder les plus pertinents."""
        # Termes trop génériques à exclure
        generic_terms = {
            'video', 'youtube', 'shorts', 'tiktok', 'content', 'watch', 
            'see', 'look', 'get', 'make', 'create', 'how to', 'ways',
            'things', 'people', 'person', 'like'
        }
        
        # Termes prioritaires (excellente recherche)
        priority_terms = {
            'psychology', 'body language', 'mind', 'brain', 'mental health',
            'secret', 'hidden', 'revelation', 'shocking', 'surprising',
            'gesture', 'posture', 'facial expression', 'emotion'
        }
        
        filtered = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            if keyword_lower in priority_terms:
                filtered.insert(0, keyword)  # Priorité haute
            elif (keyword_lower not in generic_terms and 
                  len(keyword) > 2 and 
                  not keyword.isdigit()):
                filtered.append(keyword)
        
        return filtered[:10]  # Maximum 10 mots-clés

    def _search_giphy(self, query: str, limit: int = 5) -> List[str]:
        """Recherche sur l'API GIPHY avec gestion d'erreurs robuste."""
        try:
            # Nettoyer la requête
            clean_query = query.replace(' ', '+').strip()
            if not clean_query:
                return []
            
            # Recherche de GIFs tendance et pertinents
            url = f"{self.base_url}/search"
            params = {
                'api_key': self.api_key,
                'q': clean_query,
                'limit': limit,
                'lang': 'en',  # Meilleurs résultats en anglais
                'rating': 'g',  # Contenu familial
                'bundle': 'messaging_non_clips'
            }
            
            response = requests.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                gif_urls = []
                
                for gif in data.get('data', []):
                    # Prendre la version HD si disponible
                    original = gif.get('images', {}).get('original', {})
                    mp4_url = original.get('mp4')  # Préférer MP4 pour la qualité
                    gif_url = original.get('url')
                    
                    if mp4_url:
                        gif_urls.append(mp4_url)
                    elif gif_url:
                        gif_urls.append(gif_url)
                
                print(f"   ✅ '{query}': {len(gif_urls)} GIFs trouvés")
                return gif_urls
            else:
                print(f"   ❌ GIPHY API error {response.status_code}: {query}")
                return []
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Timeout recherche: {query}")
            return []
        except Exception as e:
            print(f"   ❌ Erreur recherche '{query}': {e}")
            return []

    def _download_gif(self, gif_url: str, filename: str) -> Optional[str]:
        """Télécharge un GIF/MP4 depuis une URL."""
        try:
            response = requests.get(gif_url, timeout=20, stream=True)
            if response.status_code == 200:
                # Déterminer l'extension
                extension = '.mp4' if gif_url.endswith('.mp4') else '.gif'
                filepath = safe_path_join(self.gif_dir, f"{filename}{extension}")
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                return filepath
        except Exception as e:
            print(f"   ❌ Erreur téléchargement: {e}")
        return None

    def _validate_gif(self, gif_path: str) -> bool:
        """Valide qu'un fichier GIF est valide et utilisable."""
        try:
            if gif_path.endswith('.gif'):
                with Image.open(gif_path) as img:
                    # Vérifier que c'est bien un GIF animé
                    if hasattr(img, 'is_animated') and img.is_animated:
                        frames = ImageSequence.Iterator(img)
                        frame_count = sum(1 for _ in frames)
                        return frame_count > 1  Au moins 2 frames
                    return False
            elif gif_path.endswith('.mp4'):
                # Pour MP4, vérifier juste que le fichier existe et a une taille correcte
                return os.path.getsize(gif_path) > 1000  # Au moins 1KB
            return True
        except Exception as e:
            print(f"   ❌ GIF invalide {gif_path}: {e}")
            return False

    def _get_cached_search(self, query: str) -> List[str]:
        """Récupère une recherche depuis le cache."""
        cache_file = safe_path_join(self.cache_dir, f"{hash(query)}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    # Vérifier que le cache n'est pas trop vieux (1 heure)
                    if time.time() - data.get('timestamp', 0) < 3600:
                        return data.get('urls', [])
            except:
                pass
        return []

    def _cache_search(self, query: str, urls: List[str]):
        """Cache une recherche."""
        try:
            cache_file = safe_path_join(self.cache_dir, f"{hash(query)}.json")
            with open(cache_file, 'w') as f:
                json.dump({
                    'timestamp': time.time(),
                    'query': query,
                    'urls': urls
                }, f)
        except:
            pass  # Échec cache silencieux

    def _get_fallback_gifs(self, content_data: Dict[str, Any], num_gifs: int) -> List[str]:
        """Système de fallback robuste quand GIPHY échoue."""
        print("🔄 Activation mode fallback...")
        
        try:
            # Essayer d'abord le image_manager existant
            from content_factory.image_manager import get_images
            fallback_images = get_images(content_data, num_gifs)
            print(f"   ✅ {len(fallback_images)} images fallback générées")
            return fallback_images
        except Exception as e:
            print(f"   ❌ Fallback images échoué: {e}")
            # Fallback ultime - images de base
            return self._create_emergency_gifs(num_gifs)

    def _create_emergency_gifs(self, num_gifs: int) -> List[str]:
        """Crée des GIFs d'urgence basiques."""
        try:
            emergency_paths = []
            colors = [(41, 128, 185), (39, 174, 96), (142, 68, 173)]
            
            for i in range(min(3, num_gifs)):
                # Créer une image simple animée (2 frames)
                frames = []
                for color_idx in [0, 1]:
                    color = colors[(i + color_idx) % len(colors)]
                    img = Image.new('RGB', (500, 500), color=color)
                    frames.append(img)
                
                gif_path = safe_path_join(self.gif_dir, f"emergency_{i}_{int(time.time())}.gif")
                frames[0].save(
                    gif_path,
                    format='GIF',
                    append_images=frames[1:],
                    save_all=True,
                    duration=500,
                    loop=0
                )
                emergency_paths.append(gif_path)
            
            print(f"   🆘 {len(emergency_paths)} GIFs d'urgence créés")
            return emergency_paths
            
        except Exception as e:
            print(f"   💥 Échec GIFs d'urgence: {e}")
            return []

# Fonction d'interface pour compatibilité
def get_gifs(content_data: Dict[str, Any], num_gifs: int = 8) -> List[str]:
    """Interface simplifiée pour récupérer des GIFs."""
    manager = GifManager()
    return manager.search_gifs(content_data, num_gifs)
