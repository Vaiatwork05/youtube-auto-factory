Parfait 🙌
Voici une version complète et claire de ton README.md prête à coller sur
👉 https://github.com/Vaiatwork05/youtube-auto-factory/edit/main/README.md


---

# 🎬 YouTube Auto Factory

[![YouTube Auto Factory - 4x Daily](https://github.com/Vaiatwork05/youtube-auto-factory/actions/workflows/youtube_auto_factory.yml/badge.svg)](https://github.com/Vaiatwork05/youtube-auto-factory/actions/workflows/youtube_auto_factory.yml)

> Automatisation complète de la création de vidéos YouTube avec génération de scripts, d’audio, d’images et de montage automatique — jusqu’à **4 vidéos par jour**. 🚀

---

## 🧠 Description

**YouTube Auto Factory** est un système qui crée automatiquement des vidéos YouTube à partir d’un moteur de contenu Python.  
Il s’appuie sur des modèles de texte, d’audio et d’image pour produire des vidéos prêtes à être publiées.

### Fonctionnalités principales :
- 🤖 **Génération automatique de contenu** (texte, audio, image)
- 🧩 **Organisation modulaire** (`content_factory/`)
- ⏰ **4 créneaux quotidiens automatiques** via GitHub Actions
- 💾 **Système de cache intelligent** (modèles, assets, audio, images)
- 📈 **Résumé de production automatique** en fin de chaque run
- 🚨 **Notification automatique** en cas d’échec

---

## 🕒 Planification automatique (CRON)

| Heure (CEST) | Heure UTC | Description |
|---------------|------------|--------------|
| 08h00 | 06h00 UTC | Vidéo du matin |
| 12h00 | 10h00 UTC | Vidéo de midi |
| 16h00 | 14h00 UTC | Vidéo de l’après-midi |
| 20h00 | 18h00 UTC | Vidéo du soir |

Chaque créneau lance automatiquement le workflow GitHub pour générer une nouvelle vidéo.

---

## ⚙️ Structure du projet

youtube-auto-factory/ │ ├── content_factory/ │   ├── auto_content_engine.py   # Moteur principal (coordonne les étapes) │   ├── video_creator.py         # Montage vidéo automatique │   ├── audio_generator.py       # Synthèse vocale et audio │   ├── image_manager.py         # Génération et gestion d’images │ ├── output/ │   ├── videos/                  # Vidéos générées │   ├── audio/                   # Audios générés │   ├── images/                  # Images générées │   └── logs/                    # Logs de production │ ├── requirements_core.txt ├── requirements_extra.txt └── .github/ └── workflows/ └── youtube_auto_factory.yml

---

## 🚀 Lancer manuellement une production

Tu peux déclencher manuellement la génération dans l’onglet **Actions** de ton dépôt GitHub :

1. Va sur **Actions → YouTube Auto Factory - 4x Daily**  
2. Clique sur **Run workflow**
3. Coche ou non “Créer les 4 vidéos de la journée”
4. Lance 

🧠 Auteur

👤 Vaiatwork05

> Créateur du projet YouTube Auto Factory
Automatisation & contenu génératif pour la liberté financière et créative



📺 Chaîne YouTube (ajoute le lien ici)
🐙 GitHub


---

💚 Licence

Ce projet est publié sous licence MIT — tu es libre de l’utiliser, le modifier et le distribuer avec mention d’attribution.


---
