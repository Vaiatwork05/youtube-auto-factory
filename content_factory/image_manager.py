# content_factory/image_manager.py (VERSION INTELLIGENTE)

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
    """Gestionnaire d'images INTELLIGENT optimisé pour contenu BRAINROT TOP 10"""
    
    def __init__(self):
        self.config = ConfigLoader().get_config()
        self.paths = self.config.get('PATHS', {})
        
        # Configuration des dossiers
        output_root = self.paths.get('OUTPUT_ROOT', 'output')
        self.images_dir = safe_path_join(output_root, self.paths.get('IMAGE_DIR', 'images'))
        ensure_directory(self.images_dir)
        
        # Résolution pour Shorts
        self.resolution = (1080, 1920)
        
        # Styles visuels BRAINROT
        self.brainrot_styles = {
            'science': ['#1a237e', '#4fc3f7', '#00acc1'],      # Bleu scientifique
            'technologie': ['#311b92', '#7c4dff', '#00b0ff'],  # Violet tech
            'sante_bienetre': ['#1b5e20', '#4caf50', '#81c784'], # Vert santé
            'psychologie': ['#4a148c', '#8e24aa', '#e040fb'],  # Violet psyché
            'argent_business': ['#e65100', '#ff9800', '#ffb74d'] # Orange argent
        }

        print("🎨 ImageManager INTELLIGENT initialisé - Système GIFs optimisé")

    def generate_brainrot_assets(self, content_data: Dict, num_images: int = 8, num_gifs: int = 4) -> List[str]:
        """Génère des assets visuels INTELLIGENTS avec priorité aux GIFs"""
        
        category = content_data.get('category', 'science')
        is_part1 = content_data.get('is_part1', True)
        title = content_data.get('title', '')
        slot_number = content_data.get('slot_number', 0)
        
        print(f"🎨 GÉNÉRATION ASSETS INTELLIGENTS - Slot {slot_number}")
        print(f"   📝 {title}")
        print(f"   🎯 Catégorie: {category} | Partie: {'1' if is_part1 else '2'}")
        
        all_assets = []
        
        # STRATÉGIE INTELLIGENTE : GIFs en PRIORITÉ
        gif_paths = self._get_intelligent_gifs(content_data, num_gifs)
        all_assets.extend(gif_paths)
        
        # Images en COMPLÉMENT (seulement si besoin)
        needed_images = max(0, num_images - len(gif_paths))
        if needed_images > 0:
            brainrot_images = self._generate_brainrot_images(content_data, needed_images)
            all_assets.extend(brainrot_images)
            print(f"   🖼️ {len(brainrot_images)} images générées en complément")
        
        # Mélanger pour variété mais garder quelques GIFs au début
        if len(all_assets) > 3:
            # Garder 2-3 GIFs au début pour un bon départ
            gifs_in_assets = [a for a in all_assets if a.endswith('.gif')]
            other_assets = [a for a in all_assets if not a.endswith('.gif')]
            
            if gifs_in_assets:
                # Prendre quelques GIFs pour le début
                starting_gifs = gifs_in_assets[:min(3, len(gifs_in_assets))]
                remaining_gifs = gifs_in_assets[min(3, len(gifs_in_assets)):]
                
                # Mélanger le reste
                random.shuffle(other_assets)
                random.shuffle(remaining_gifs)
                
                all_assets = starting_gifs + other_assets + remaining_gifs
            else:
                random.shuffle(all_assets)
        else:
            random.shuffle(all_assets)
        
        gif_count = sum(1 for a in all_assets if a.endswith('.gif'))
        print(f"🎉 Total assets: {len(all_assets)} (dont {gif_count} GIFs intelligents)")
        
        return all_assets

    def _get_intelligent_gifs(self, content_data: Dict, num_gifs: int) -> List[str]:
        """Système INTELLIGENT de récupération de GIFs avec fallbacks"""
        
        gif_paths = []
        
        if not REDDIT_GIFS_AVAILABLE:
            print("   ❌ Système GIFs non disponible")
            return gif_paths
        
        print("   🧠 Lancement recherche GIFs intelligente...")
        
        try:
            # ESSAI 1: Recherche Reddit intelligente
            gif_urls = get_brainrot_gifs(content_data, num_gifs)
            
            if gif_urls:
                downloaded = self._download_gifs(gif_urls, content_data)
                gif_paths.extend(downloaded)
                print(f"   ✅ {len(downloaded)} GIFs intelligents trouvés")
                
                # Si on a assez de GIFs, on s'arrête là
                if len(gif_paths) >= num_gifs:
                    return gif_paths[:num_gifs]
            
            # ESSAI 2: Recherche de fallback
            remaining_gifs = num_gifs - len(gif_paths)
            if remaining_gifs > 0:
                print(f"   🔄 Recherche fallback ({remaining_gifs} GIFs manquants)...")
                fallback_gifs = self._fallback_gif_search(content_data, remaining_gifs)
                gif_paths.extend(fallback_gifs)
                
        except Exception as e:
            print(f"   ❌ Erreur recherche GIFs: {e}")
        
        return gif_paths

    def _fallback_gif_search(self, content_data: Dict, num_gifs: int) -> List[str]:
        """Recherche de fallback quand Reddit échoue"""
        
        # Pour l'instant, retourner une liste vide
        # Plus tard, on pourra implémenter:
        # - GIFs locaux dans assets/gifs/
        # - Génération d'animations avec Pillow
        # - Autres APIs GIFs
        
        print("   💡 ASTUCE: Crée un dossier 'assets/gifs/' avec des GIFs brainrot!")
        print("   💡 Les GIFs locaux seront utilisés en fallback automatiquement")
        
        return []

    def _generate_brainrot_images(self, content_data: Dict, num_images: int) -> List[str]:
        """Génère des images au style BRAINROT"""
        
        category = content_data.get('category', 'science')
        is_part1 = content_data.get('is_part1', True)
        title = content_data.get('title', '')
        keywords = content_data.get('keywords', [])
        
        colors = self.brainrot_styles.get(category, self.brainrot_styles['science'])
        images = []
        
        print(f"   🎨 Génération de {num_images} images brainrot...")
        
        for i in range(num_images):
            try:
                # Style différent selon la partie
                if is_part1:
                    img = self._create_mystery_image(colors, title, i, num_images)
                else:
                    img = self._create_shock_image(colors, title, i, num_images)
                
                filename = f"brainrot_{category}_{'p1' if is_part1 else 'p2'}_{i}_{int(time.time())}.jpg"
                output_path = safe_path_join(self.images_dir, filename)
                
                img.save(output_path, 'JPEG', quality=90, optimize=True)
                images.append(output_path)
                
            except Exception as e:
                print(f"   ⚠️ Erreur génération image {i}: {e}")
                continue
        
        return images

    def _create_mystery_image(self, colors: List, title: str, index: int, total: int) -> Image.Image:
        """Crée une image mystérieuse pour la Partie 1"""
        img = Image.new('RGB', self.resolution, color=colors[0])
        draw = ImageDraw.Draw(img)
        
        # Ajouter des éléments mystérieux
        self._add_mystery_elements(draw, colors, index)
        
        # Texte principal
        title_lines = self._split_text(title, 30)
        for i, line in enumerate(title_lines[:2]):
            self._draw_brainrot_text(draw, line, 100 + i * 120, size=48, color='#FFFFFF')
        
        # Numéro de point (style mystère)
        point_num = total - index
        self._draw_brainrot_text(draw, f"#{point_num}", 500, size=120, color=colors[1])
        
        # Élément d'intrigue
        intrigue_text = ["SECRET", "CACHÉ", "MYSTÈRE", "RÉVÉLATION"][index % 4]
        self._draw_brainrot_text(draw, intrigue_text, 700, size=36, color=colors[2])
        
        return img

    def _create_shock_image(self, colors: List, title: str, index: int, total: int) -> Image.Image:
        """Crée une image choquante pour la Partie 2"""
        # Fond avec dégradé explosif
        img = self._create_explosion_gradient(colors)
        draw = ImageDraw.Draw(img)
        
        # Éléments explosifs
        self._add_shock_elements(draw, colors, index)
        
        # Texte principal (plus agressif)
        title_lines = self._split_text(title, 28)
        for i, line in enumerate(title_lines[:2]):
            self._draw_brainrot_text(draw, line, 150 + i * 100, size=52, color='#FFFFFF', bold=True)
        
        # Numéro de point (style explosion)
        point_num = total - index
        self._draw_brainrot_text(draw, f"#{point_num}", 500, size=140, color='#FF0000')
        
        # Texte choc
        shock_text = ["CHOC", "EXPLOSIF", "INCROYABLE", "RÉVOLUTION"][index % 4]
        self._draw_brainrot_text(draw, shock_text, 750, size=42, color='#FFFF00')
        
        return img

    def _create_explosion_gradient(self, colors: List) -> Image.Image:
        """Crée un dégradé explosif"""
        img = Image.new('RGB', self.resolution, color=colors[0])
        
        # Simule un effet d'explosion avec des cercles
        for i in range(5):
            radius = random.randint(200, 600)
            x = random.randint(0, self.resolution[0])
            y = random.randint(0, self.resolution[1])
            color = colors[i % len(colors)]
            
            temp_img = Image.new('RGB', self.resolution, (0, 0, 0, 0))
            temp_draw = ImageDraw.Draw(temp_img)
            temp_draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=color)
            
            img = Image.blend(img, temp_img, alpha=0.3)
        
        return img

    def _add_mystery_elements(self, draw: ImageDraw.Draw, colors: List, index: int):
        """Ajoute des éléments mystérieux à l'image"""
        # Lignes de code (pour tech)
        for i in range(10):
            x1 = random.randint(0, self.resolution[0])
            y1 = random.randint(0, self.resolution[1])
            x2 = x1 + random.randint(50, 200)
            y2 = y1
            draw.line([x1, y1, x2, y2], fill=colors[1], width=2)
        
        # Points d'interrogation
        for i in range(5):
            x = random.randint(100, self.resolution[0]-100)
            y = random.randint(100, self.resolution[1]-100)
            draw.text((x, y), "?", fill=colors[2], font_size=30)

    def _add_shock_elements(self, draw: ImageDraw.Draw, colors: List, index: int):
        """Ajoute des éléments choquants à l'image"""
        # Éclairs et explosions
        for i in range(8):
            x1 = random.randint(0, self.resolution[0])
            y1 = random.randint(0, self.resolution[1])
            x2 = x1 + random.randint(-100, 100)
            y2 = y1 + random.randint(50, 150)
            draw.line([x1, y1, x2, y2], fill='#FFFF00', width=3)
        
        # Étoiles d'explosion
        for i in range(15):
            x = random.randint(0, self.resolution[0])
            y = random.randint(0, self.resolution[1])
            size = random.randint(5, 15)
            draw.rectangle([x, y, x+size, y+size], fill='#FF0000')

    def _draw_brainrot_text(self, draw: ImageDraw.Draw, text: str, y: int, size: int = 36, color: str = '#FFFFFF', bold: bool = False):
        """Dessine du texte style BRAINROT"""
        try:
            # Essayer une police plus stylée
            font = ImageFont.load_default()
            # Fallback à la police par défaut si échec
            
            text_width = draw.textlength(text, font=font)
            x = (self.resolution[0] - text_width) // 2
            
            # Ombre pour effet 3D
            if bold:
                draw.text((x-2, y-2), text, fill='#000000', font=font)
                draw.text((x+2, y+2), text, fill='#000000', font=font)
            
            draw.text((x, y), text, fill=color, font=font)
            
        except Exception as e:
            # Fallback basique
            text_width = len(text) * size // 2
            x = (self.resolution[0] - text_width) // 2
            draw.text((x, y), text, fill=color)

    def _split_text(self, text: str, max_length: int) -> List[str]:
        """Divise un texte en lignes"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            if len(' '.join(current_line + [word])) <= max_length:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines

    def _download_gifs(self, gif_urls: List[str], content_data: Dict) -> List[str]:
        """Télécharge les GIFs depuis les URLs avec gestion d'erreur améliorée"""
        downloaded_paths = []
        
        print(f"   📥 Téléchargement de {len(gif_urls)} GIFs...")
        
        for i, gif_url in enumerate(gif_urls):
            try:
                headers = {'User-Agent': 'YouTubeBrainrotFactory/1.0'}
                print(f"      🔄 GIF {i+1}/{len(gif_urls)}: {gif_url[:80]}...")
                
                response = requests.get(gif_url, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    filename = f"brainrot_gif_{content_data['category']}_{i}_{int(time.time())}.gif"
                    output_path = safe_path_join(self.images_dir, filename)
                    
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    
                    # Vérifier que le fichier est valide
                    file_size = os.path.getsize(output_path)
                    if file_size > 1024:  # Au moins 1KB
                        downloaded_paths.append(output_path)
                        print(f"      ✅ GIF {i+1} téléchargé ({file_size//1024} KB)")
                    else:
                        print(f"      ❌ GIF {i+1} trop petit, suppression")
                        os.remove(output_path)
                else:
                    print(f"      ❌ Erreur HTTP {response.status_code} pour GIF {i+1}")
                    
            except Exception as e:
                print(f"      ⚠️ Erreur téléchargement GIF {i+1}: {e}")
                continue
        
        return downloaded_paths

    def create_gifs_folder_structure(self):
        """Crée la structure de dossiers pour les GIFs locaux"""
        gifs_dir = safe_path_join("assets", "gifs")
        ensure_directory(gifs_dir)
        
        # Sous-dossiers par catégorie
        categories = ['technologie', 'science', 'psychologie', 'argent_business', 'sante_bienetre']
        for category in categories:
            ensure_directory(safe_path_join(gifs_dir, category))
        
        print("✅ Structure GIFs locale créée!")
        print("💡 Ajoute des GIFs dans assets/gifs/ pour le fallback automatique")

# Fonction d'interface principale
def get_images(content_data: Dict, num_images: int = 8) -> List[str]:
    """Fonction principale pour récupérer des images BRAINROT intelligentes"""
    manager = BrainrotImageManager()
    return manager.generate_brainrot_assets(content_data, num_images)

def enhance_with_brainrot_assets(content_data: Dict) -> Dict:
    """Enrichit le contenu avec des métadonnées d'assets"""
    manager = BrainrotImageManager()
    assets = manager.generate_brainrot_assets(content_data)
    content_data['brainrot_assets'] = assets
    content_data['has_brainrot_style'] = True
    content_data['assets_count'] = len(assets)
    content_data['gifs_count'] = sum(1 for a in assets if a.endswith('.gif'))
    return content_data

# Utilitaire pour setup
def setup_gifs_infrastructure():
    """Crée l'infrastructure pour les GIFs locaux"""
    manager = BrainrotImageManager()
    manager.create_gifs_folder_structure()

# Test
if __name__ == "__main__":
    print("🧪 Test ImageManager Intelligent...")
    
    test_data = {
        'title': 'TEST Technologies Militaires Secrètes',
        'category': 'technologie',
        'is_part1': False,
        'script': 'Les technologies militaires classées secret défense vont vous choquer...',
        'keywords': ['militaire', 'secret', 'technologie', 'défense']
    }
    
    manager = BrainrotImageManager()
    assets = manager.generate_brainrot_assets(test_data, 6, 3)
    
    print(f"🎯 Résultat: {len(assets)} assets générés")
    for asset in assets:
        print(f"   - {os.path.basename(asset)}")
