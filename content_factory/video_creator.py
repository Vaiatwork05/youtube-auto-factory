def create_simple_video(self, script_data, output_dir="output"):
    """Crée une vidéo simple sans ImageMagick"""
    
    # Créer le dossier de sortie
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎥 Création vidéo avec méthode simple...")
    
    # Créer une image avec du texte
    img = Image.new('RGB', self.resolution, color=(30, 30, 60))
    draw = ImageDraw.Draw(img)
    
    # Utiliser une police basique
    try:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    except:
        font = None
        title_font = None
    
    # Nettoyer le texte
    clean_title = script_data["title"].replace('·', '-').replace('•', '-').replace('→', '->')
    clean_script = script_data["script"].replace('·', '-').replace('•', '-').replace('→', '->')
    
    # Diviser le texte en lignes
    words = clean_script.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        if len(test_line) < 40:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    
    # Dessiner le titre
    try:
        draw.text((100, 100), clean_title, fill=(255, 255, 0), font=title_font)
    except:
        draw.text((100, 100), "Science Discovery", fill=(255, 255, 0), font=title_font)
    
    # Dessiner le texte
    y_position = 200
    for line in lines[:6]:
        if y_position < 600:
            try:
                draw.text((100, y_position), line, fill=(255, 255, 255), font=font)
                y_position += 40
            except:
                continue
    
    # Footer
    try:
        draw.text((100, 650), "Science Auto Daily - Abonnez-vous !", fill=(200, 200, 200), font=font)
    except:
        draw.text((100, 650), "Science Auto Daily", fill=(200, 200, 200), font=font)
    
    # Sauvegarder l'image temporaire
    temp_image_path = os.path.join(output_dir, "temp_frame.png")
    img.save(temp_image_path)
    
    # Créer une vidéo à partir de l'image
    image_clip = ImageClip(temp_image_path, duration=self.video_duration)
    
    # ⭐⭐ CORRECTION ICI : Nettoyer le nom de fichier ⭐⭐
    clean_filename = clean_title.replace(' ', '_').replace('/', '_').replace('?', '').replace('!', '').replace(':', '')
    output_path = os.path.join(output_dir, f"video_{clean_filename}.mp4")
    
    try:
        image_clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )
    except Exception as e:
        print(f"⚠️  Erreur lors de l'export vidéo: {e}")
        from moviepy.editor import ColorClip
        color_clip = ColorClip(size=(1280, 720), color=(30, 30, 60), duration=10)
        color_clip.write_videofile(output_path, fps=24, verbose=False, logger=None)
    
    # Nettoyer
    if os.path.exists(temp_image_path):
        os.remove(temp_image_path)
    
    print(f"✅ Vidéo créée: {output_path}")
    return output_path        return output_path

    def create_video(self, script_data, output_dir="output"):
        """Alias pour create_simple_video - garde la compatibilité avec l'ancien code"""
        return self.create_simple_video(script_data, output_dir)

# Test
if __name__ == "__main__":
    creator = VideoCreator()
    test_script = {
        "title": "Test Video",
        "script": "Ceci est un test de création vidéo automatique sans ImageMagick! La science nous entoure et ces vidéos automatiques vous l'expliquent simplement."
    }
    creator.create_simple_video(test_script)
