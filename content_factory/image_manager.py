# content_factory/image_manager.py (VERSION CORRIGÉE - Unsplash + IA)

import os
import random
import requests
from typing import List, Dict, Optional
from PIL import Image, ImageDraw, ImageFont
import time

from content_factory.utils import ensure_directory, safe_path_join
from content_factory.config_loader import ConfigLoader

try:
    from content_factory.reddit_gifs import get_brainrot_gifs
    REDDIT_GIFS_AVAILABLE = True
except ImportError as e:
    REDDIT_GIFS_AVAILABLE = False
    print(f"⚠️ Reddit GIFs non disponible: {e}")

class BrainrotImageManager:
    """Gestionnaire d'images INTELLIGENT avec IA + Unsplash - VERSION CORRIGÉE"""
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.paths = self.config.get('PATHS', {})
        
        # Configuration des dossiers
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        self.images_dir = safe_path_join(output_root, self.paths.get('IMAGE_DIR', 'images'))
        ensure_directory(self.images_dir)
        
        # Résolution pour Shorts (dimensions paires)
        self.resolution = (1080, 1920)
        
        # 🔥 CORRECTION : Utiliser UNSPLASH_API_KEY au lieu de UNSPLASH_ACCESS_KEY
        self.unsplash_access_key = os.getenv('UNSPLASH_API_KEY')
        self.unsplash_enabled = bool(self.unsplash_access_key)
        
        if self.unsplash_enabled:
            print("🎨 ImageManager INTELLIGENT initialisé - Unsplash ACTIVÉ")
        else:
            print("🎨 ImageManager INTELLIGENT initialisé - Unsplash DÉSACTIVÉ")
        
        # Styles visuels BRAINROT
        self.brainrot_styles = {
            'science': ['#1a237e', '#4fc3f7', '#00acc1'],
            'technologie': ['#311b92', '#7c4dff', '#00b0ff'],
            'sante_bienetre': ['#1b5e20', '#4caf50', '#81c784'],
            'psychologie': ['#4a148c', '#8e24aa', '#e040fb'],
            'argent_business': ['#e65100', '#ff9800', '#ffb74d']
        }

    def _ensure_unique_gifs(self, gif_urls: List[str]) -> List[str]:
        """Garantit que les GIFs sont uniques"""
        if not gif_urls:
            return []
        
        seen = set()
        unique_urls = []
        
        for url in gif_urls:
            if 'tenor.com' in url:
                parts = url.split('/')
                gif_id = url
                for part in parts:
                    if part.endswith('AAAAC') and len(part) > 10:
                        gif_id = part
                        break
            else:
                gif_id = url
            
            if gif_id not in seen:
                seen.add(gif_id)
                unique_urls.append(url)
        
        print(f"   🔍 Déduplication: {len(gif_urls)} → {len(unique_urls)} GIFs uniques")
        return unique_urls

    def generate_brainrot_assets(self, content_data: Dict, num_images: int = 8, num_gifs: int = 4) -> List[str]:
        """Génère des assets visuels INTELLIGENTS avec IA + Unsplash"""
        
        category = content_data.get('category', 'science')
        is_part1 = content_data.get('is_part1', True)
        title = content_data.get('title', '')
        slot_number = content_data.get('slot_number', 0)
        
        print(f"🎨 GÉNÉRATION ASSETS INTELLIGENTS - Slot {slot_number}")
        print(f"   📝 {title[:60]}..." if len(title) > 60 else f"   📝 {title}")
        print(f"   🎯 Catégorie: {category} | Partie: {'1' if is_part1 else '2'}")
        
        all_assets = []
        
        # STRATÉGIE INTELLIGENTE : GIFs en PRIORITÉ
        gif_paths = self._get_intelligent_gifs(content_data, num_gifs)
        all_assets.extend(gif_paths)
        
        # Images en COMPLÉMENT avec IA + Unsplash
        needed_images = max(0, num_images - len(gif_paths))
        if needed_images > 0:
            print(f"   🖼️ Génération de {needed_images} images en complément...")
            
            # 🎯 STRATÉGIE AMÉLIORÉE : Unsplash avec mots-clés IA
            unsplash_images = self._get_ai_enhanced_unsplash(content_data, needed_images)
            if unsplash_images:
                all_assets.extend(unsplash_images)
                print(f"   📸 {len(unsplash_images)} images Unsplash IA récupérées")
            
            # Fallback : Génération automatique
            remaining_images = needed_images - len(unsplash_images)
            if remaining_images > 0:
                brainrot_images = self._generate_brainrot_images(content_data, remaining_images)
                all_assets.extend(brainrot_images)
                print(f"   🎨 {len(brainrot_images)} images brainrot générées")
        
        # Mélanger intelligemment
        final_assets = self._smart_shuffle_assets(all_assets)
        
        gif_count = sum(1 for a in final_assets if a.endswith('.gif'))
        image_count = len(final_assets) - gif_count
        print(f"🎉 Total assets: {len(final_assets)} (dont {gif_count} GIFs, {image_count} images)")
        
        return final_assets

    def _get_ai_enhanced_unsplash(self, content_data: Dict, num_images: int) -> List[str]:
        """Utilise les mots-clés IA pour des images hyper-pertinentes"""
        
        if not self.unsplash_enabled:
            print("   ⚠️ Unsplash désactivé - clé API manquante")
            return []
        
        # Récupérer les mots-clés générés par l'IA
        ai_keywords = content_data.get('keywords', [])
        ai_title = content_data.get('title', '')
        category = content_data.get('category', 'default')
        
        print(f"   🤖 Mots-clés IA détectés: {ai_keywords}")
        
        # 🎯 STRATÉGIE DE RECHERCHE INTELLIGENTE
        search_terms = self._build_ai_search_terms(ai_keywords, ai_title, category)
        
        if not search_terms:
            print("   ⚠️ Aucun terme de recherche valide")
            return []
        
        # Choisir le terme le plus pertinent
        query = search_terms[0]
        alternative_queries = search_terms[1:3]
        
        print(f"   🎯 Recherche Unsplash IA: '{query}'")
        print(f"   🔄 Alternatives: {alternative_queries}")
        
        downloaded_images = []
        
        for i in range(num_images):
            try:
                # Alterner entre les termes pour la variété
                current_query = query if i % 3 == 0 else random.choice(alternative_queries) if alternative_queries else query
                
                api_url = "https://api.unsplash.com/photos/random"
                params = {
                    'query': current_query,
                    'orientation': 'portrait',
                    'client_id': self.unsplash_access_key
                }
                
                response = requests.get(api_url, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    image_url = data['urls']['regular']
                    
                    img_response = requests.get(image_url, timeout=15)
                    if img_response.status_code == 200:
                        filename = f"unsplash_ai_{category}_{i}_{int(time.time())}.jpg"
                        output_path = safe_path_join(self.images_dir, filename)
                        
                        with open(output_path, 'wb') as f:
                            f.write(img_response.content)
                        
                        # Redimensionner pour compatibilité H.264
                        self._resize_unsplash_image(output_path)
                        downloaded_images.append(output_path)
                        
                        alt_text = data.get('alt_description', 'sans description')
                        print(f"      ✅ Unsplash {i+1}: '{alt_text[:30]}...' (terme: '{current_query}')")
                
                time.sleep(0.3)
                
            except Exception as e:
                print(f"      ⚠️ Erreur Unsplash {i+1}: {e}")
        
        return downloaded_images

    def _build_ai_search_terms(self, ai_keywords: List[str], title: str, category: str) -> List[str]:
        """Construit des termes de recherche intelligents basés sur l'IA"""
        
        search_terms = []
        
        # 1. 🥇 MOTS-CLÉS EXPLICITES DE L'IA
        if ai_keywords:
            clean_keywords = [kw.strip().lower() for kw in ai_keywords if kw and len(kw) > 2]
            search_terms.extend(clean_keywords[:6])
        
        # 2. 🥈 TERMES DU TITRE
        clean_title = title.replace('💀', '').replace('🚨', '').replace('🧠', '').replace('📹', '')
        title_words = [word.lower() for word in clean_title.split() if len(word) > 4]
        search_terms.extend(title_words[:4])
        
        # 3. 🥉 CATÉGORIE
        category_terms = {
            'science': ['science', 'laboratory', 'research', 'physics', 'chemistry'],
            'technologie': ['technology', 'computer', 'code', 'programming', 'ai'],
            'sante_bienetre': ['health', 'fitness', 'wellness', 'medicine', 'nature'],
            'psychologie': ['psychology', 'mind', 'brain', 'thinking', 'meditation'],
            'argent_business': ['money', 'business', 'finance', 'success', 'wealth']
        }
        
        category_terms_list = category_terms.get(category, ['abstract', 'concept', 'future'])
        search_terms.extend(category_terms_list[:3])
        
        # Nettoyer et dédupliquer
        final_terms = []
        seen_terms = set()
        
        for term in search_terms:
            if term and term not in seen_terms and len(term) > 2:
                seen_terms.add(term)
                final_terms.append(term)
        
        print(f"      🎯 Termes de recherche finals: {final_terms[:8]}")
        return final_terms

    def _smart_shuffle_assets(self, assets: List[str]) -> List[str]:
        """Mélange les assets intelligemment"""
        if len(assets) <= 3:
            random.shuffle(assets)
            return assets
        
        gifs = [a for a in assets if a.endswith('.gif')]
        images = [a for a in assets if not a.endswith('.gif')]
        
        if not gifs:
            random.shuffle(images)
            return images
        
        if not images:
            random.shuffle(gifs)
            return gifs
        
        starting_gifs = gifs[:min(2, len(gifs))]
        remaining_gifs = gifs[min(2, len(gifs)):]
        
        random.shuffle(images)
        random.shuffle(remaining_gifs)
        
        final_assets = starting_gifs + images + remaining_gifs
        
        if len(final_assets) > 12:
            final_assets = final_assets[:12]
        
        return final_assets

    def _resize_unsplash_image(self, image_path: str):
        """Redimensionne une image Unsplash aux dimensions requises"""
        try:
            with Image.open(image_path) as img:
                target_width, target_height = self.resolution
                target_width = target_width if target_width % 2 == 0 else target_width - 1
                target_height = target_height if target_height % 2 == 0 else target_height - 1
                
                img_ratio = img.width / img.height
                target_ratio = target_width / target_height
                
                if img_ratio > target_ratio:
                    new_height = target_height
                    new_width = int(img.width * (target_height / img.height))
                else:
                    new_width = target_width
                    new_height = int(img.height * (target_width / img.width))
                
                new_width = new_width if new_width % 2 == 0 else new_width - 1
                new_height = new_height if new_height % 2 == 0 else new_height - 1
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                left = (new_width - target_width) // 2
                top = (new_height - target_height) // 2
                right = left + target_width
                bottom = top + target_height
                
                img_cropped = img.crop((left, top, right, bottom))
                img_cropped.save(image_path, 'JPEG', quality=85, optimize=True)
                
        except Exception as e:
            print(f"      ⚠️ Redimensionnement Unsplash échoué: {e}")

    def _get_intelligent_gifs(self, content_data: Dict, num_gifs: int) -> List[str]:
        """Système INTELLIGENT de récupération de GIFs"""
        gif_paths = []
        
        if not REDDIT_GIFS_AVAILABLE:
            return gif_paths
        
        print("   🧠 Lancement recherche GIFs intelligente...")
        
        try:
            gif_urls = get_brainrot_gifs(content_data, num_gifs)
            if gif_urls:
                gif_urls = self._ensure_unique_gifs(gif_urls)
                downloaded = self._download_gifs(gif_urls, content_data)
                gif_paths.extend(downloaded)
                
                if downloaded:
                    print(f"   ✅ {len(downloaded)} GIFs intelligents trouvés")
                
                if len(gif_paths) >= num_gifs:
                    return gif_paths[:num_gifs]
            
        except Exception as e:
            print(f"   ❌ Erreur recherche GIFs: {e}")
        
        return gif_paths

    def _download_gifs(self, gif_urls: List[str], content_data: Dict) -> List[str]:
        """Télécharge les GIFs depuis les URLs"""
        downloaded_paths = []
        
        if not gif_urls:
            return []
        
        print(f"   📥 Téléchargement de {len(gif_urls)} GIFs...")
        
        for i, gif_url in enumerate(gif_urls):
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = requests.get(gif_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    filename = f"brainrot_gif_{content_data.get('category', 'general')}_{i}_{int(time.time())}.gif"
                    output_path = safe_path_join(self.images_dir, filename)
                    
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    
                    file_size = os.path.getsize(output_path)
                    if file_size > 2048:
                        downloaded_paths.append(output_path)
                        print(f"      ✅ GIF {i+1} téléchargé ({file_size//1024} KB)")
                    
            except Exception as e:
                print(f"      ⚠️ Erreur téléchargement GIF {i+1}: {e}")
        
        return downloaded_paths

    def _get_local_gifs(self, content_data: Dict, num_gifs: int) -> List[str]:
        """Récupère des GIFs locaux"""
        category = content_data.get('category', 'science')
        local_gifs_dir = safe_path_join("assets", "gifs", category)
        
        if not os.path.exists(local_gifs_dir):
            local_gifs_dir = safe_path_join("assets", "gifs")
            if not os.path.exists(local_gifs_dir):
                return []
        
        try:
            all_gifs = []
            for file in os.listdir(local_gifs_dir):
                if file.lower().endswith(('.gif', '.mp4', '.mov')):
                    full_path = safe_path_join(local_gifs_dir, file)
                    all_gifs.append(full_path)
            
            if all_gifs:
                return random.sample(all_gifs, min(num_gifs, len(all_gifs)))
            
        except Exception as e:
            print(f"   ⚠️ Erreur chargement GIFs locaux: {e}")
        
        return []

    def _generate_brainrot_images(self, content_data: Dict, num_images: int) -> List[str]:
        """Génère des images brainrot de fallback"""
        category = content_data.get('category', 'science')
        is_part1 = content_data.get('is_part1', True)
        title = content_data.get('title', 'Titre mystère')
        
        colors = self.brainrot_styles.get(category, self.brainrot_styles['science'])
        images = []
        
        for i in range(num_images):
            try:
                if is_part1:
                    img = self._create_mystery_image(colors, title, i, num_images)
                else:
                    img = self._create_shock_image(colors, title, i, num_images)
                
                filename = f"brainrot_{category}_{'p1' if is_part1 else 'p2'}_{i}_{int(time.time())}.jpg"
                output_path = safe_path_join(self.images_dir, filename)
                img.save(output_path, 'JPEG', quality=85, optimize=True)
                images.append(output_path)
                
            except Exception as e:
                print(f"   ⚠️ Erreur génération image {i}: {e}")
        
        return images

    def _create_mystery_image(self, colors: List, title: str, index: int, total: int) -> Image.Image:
        img = Image.new('RGB', self.resolution, color=colors[0])
        draw = ImageDraw.Draw(img)
        
        point_num = total - index
        self._draw_centered_text(draw, f"#{point_num}", self.resolution[1] // 2 - 50, size=120, color=colors[1], bold=True)
        
        title_short = title[:40] + "..." if len(title) > 40 else title
        self._draw_centered_text(draw, title_short, self.resolution[1] // 2 + 50, size=36, color='#FFFFFF')
        
        return img

    def _create_shock_image(self, colors: List, title: str, index: int, total: int) -> Image.Image:
        img = Image.new('RGB', self.resolution, color=colors[0])
        draw = ImageDraw.Draw(img)
        
        point_num = total - index
        self._draw_centered_text(draw, f"#{point_num}", self.resolution[1] // 2 - 80, size=140, color='#FF0000', bold=True)
        
        title_short = title[:35] + "!" * min(3, index + 1) if len(title) > 35 else title + "!" * min(2, index + 1)
        self._draw_centered_text(draw, title_short, self.resolution[1] // 2 + 40, size=40, color='#FFFFFF', bold=True)
        
        return img

    def _draw_centered_text(self, draw: ImageDraw.Draw, text: str, y: int, size: int = 36, color: str = '#FFFFFF', bold: bool = False):
        try:
            font = ImageFont.load_default()
            text_width = draw.textlength(text, font=font)
            x = (self.resolution[0] - text_width) // 2
            
            if bold:
                draw.text((x-1, y-1), text, fill='#000000', font=font)
                draw.text((x+1, y+1), text, fill='#000000', font=font)
            
            draw.text((x, y), text, fill=color, font=font)
            
        except Exception:
            text_width = len(text) * (size // 2)
            x = (self.resolution[0] - text_width) // 2
            draw.text((x, y), text, fill=color)

# Fonctions d'interface
def get_images(content_data: Dict, num_images: int = 8) -> List[str]:
    try:
        manager = BrainrotImageManager()
        return manager.generate_brainrot_assets(content_data, num_images)
    except Exception as e:
        print(f"❌ Erreur ImageManager: {e}")
        return []

def enhance_with_brainrot_assets(content_data: Dict) -> Dict:
    try:
        manager = BrainrotImageManager()
        assets = manager.generate_brainrot_assets(content_data)
        content_data['brainrot_assets'] = assets
        content_data['has_brainrot_style'] = True
        content_data['assets_count'] = len(assets)
        content_data['gifs_count'] = sum(1 for a in assets if a.endswith('.gif'))
        return content_data
    except Exception as e:
        print(f"❌ Erreur enhancement assets: {e}")
        return content_data
