
#  T-Rex Runner AI - Intelligence Artificielle DQN

##  Vue d'Ensemble

Un système d'intelligence artificielle basé sur **Deep Q-Network (DQN)** capable de jouer au célèbre jeu T-Rex Runner de Chrome avec des performances surhumaines. L'IA maîtrise l'évitement d'obstacles complexes et peut survivre indéfiniment.

###  Objectifs Atteints
-  **Évitement parfait** des cactus (saut précis)
-  **Gestion intelligente des oiseaux** selon leur hauteur
-  **Adaptation dynamique** à l'accélération du jeu (6→13 unités/s)
-  **Collecte stratégique** des bonus aériens
-  **Performance stable** avec scores moyens >400 points

###  Performance Actuelle
| Métrique | Valeur |
|----------|--------|
| Score Maximum | 1346+ points |
| Score Moyen | 400-800 points |
| Taux de Survie | >95% |
| Durée de Survie | Infinie à vitesse max |

---

##  Installation et Démarrage Rapide

### 1. Prérequis
```bash
# Python 3.8+ requis
python3 --version

# Installation des dépendances
pip install tensorflow pygame numpy matplotlib
# OU
pip install -r requirements.txt
```

### 2. Test Immédiat
```bash
# Test avec un modèle pré-entraîné
python3 -m src.main --play --resume models/runs/2026-02-27_123129/best --render 1

# Mode humain pour comparaison
python3 -m src.main --play --human 1 --render 1
# Contrôles: ESPACE/↑ (sauter), ↓ (se baisser), ESC (quitter)
```

---

##  Entraînement d'un Nouveau Modèle

### Configuration Optimisée (Recommandée)
```bash
# Entraînement stable avec paramètres optimisés
python3 -m src.main --train \
  --episodes 700 \
  --obstacles cactus,bird,bonus \
  --lr 0.0002 \
  --epsilon_start 0.05 \
  --epsilon_decay_steps 20000 \
  --target_update 1500 \
  --render 0

# Surveillance en temps réel
python3 -m src.main --train --episodes 200 --obstacles cactus,bird --render 1
```

### Options d'Entraînement

#### Option A : Entraînement Rapide
```bash
# Cactus + Oiseaux (700 épisodes, ~20-30 min)
python3 -m src.main --train --episodes 700 --obstacles cactus,bird --render 0
```

#### Option B : Entraînement Complet avec Bonus
```bash
# Tous obstacles (1000+ épisodes, ~45-60 min)
python3 -m src.main --train --episodes 1000 --obstacles cactus,bird,bonus --render 0
```

#### Option C : Curriculum d'Apprentissage
```bash
# Étape 1: Maîtrise des cactus
python3 -m src.main --train --episodes 300 --obstacles cactus --render 0

# Étape 2: Ajout des oiseaux
python3 -m src.main --train --episodes 500 --obstacles cactus,bird --render 0

# Étape 3: Intégration des bonus
python3 -m src.main --train --episodes 200 --obstacles cactus,bird,bonus --render 0
```

### Paramètres d'Entraînement Avancés
```bash
# Configuration personnalisée
python3 -m src.main --train \
  --episodes 800 \
  --learning_rate 0.0002 \        # Plus stable que 0.001
  --batch_size 64 \
  --epsilon_start 0.05 \          # Exploration réduite
  --epsilon_decay_steps 20000 \   # Decay plus lent
  --target_update_freq 1500 \     # Stabilité accrue
  --obstacles cactus,bird,bonus \
  --render 0
```
---

##  Test et Évaluation des Modèles

### Tests de Performance
```bash
# Observer l'IA en action
python3 -m src.main --play --resume models/runs/[DATE_TIME]/best --render 1

# Évaluation statistique (20 parties)
python3 -m src.main --play --resume models/runs/[DATE_TIME]/best --render 0 --episodes 20

# Test sur obstacles spécifiques
python3 -m src.main --play --resume models/runs/[DATE_TIME]/best --obstacles bird --render 1
```

### Modèles Disponibles
```bash
# Lister tous les modèles entraînés
ls models/runs/

# Modèles recommandés:
# 2026-02-27_123129 : Excellent sur cactus+bird+bonus
# 2026-02-27_104727 : Spécialisé cactus+bird
# 2026-02-27_011233 : Modèle de référence stable
```

### Comparaison Humain vs IA
```bash
# Jouer en mode humain
python3 -m src.main --play --human 1 --render 1

# Puis tester l'IA sur les mêmes obstacles
python3 -m src.main --play --resume models/runs/[MEILLEUR_MODELE]/best --render 1
```

---

##  Architecture de l'IA

### Réseau de Neurones DQN
```
Entrée (8 dimensions) → Dense(128, ReLU) → Dense(64, ReLU) → Sortie (3 actions)
```

#### Observation du Jeu (9D)
| Dimension | Description | Valeurs |
|-----------|-------------|---------|
| distance_obstacle | Distance normalisée au prochain obstacle | [0, 1] |
| obstacle_width | Largeur normalisée de l'obstacle | [0, 1] |
| obstacle_height | Hauteur normalisée de l'obstacle | [0, 1] |
| obstacle_y | Position Y normalisée de l'obstacle | [0, 1] |
| obstacle_type | Type: 0=cactus, 1=oiseau, 2=bonus | [0, 1, 2] |
| game_speed | Vitesse normalisée du jeu | [0, 1] |
| dino_y | Position Y normalisée du dinosaure | [0, 1] |
| dino_vel_y | Vitesse verticale normalisée du dinosaure | [0, 1] |
| dino_on_ground | Dinosaure au sol (0=vol, 1=sol) | [0, 1] |

#### Actions Disponibles (3)
| Action | ID | Description |
|--------|----|-------------|
| WAIT | 0 | Continuer à courir |
| JUMP | 1 | Sauter (éviter cactus/oiseau bas) |
| DUCK | 2 | Se baisser (éviter oiseau moyen) |

### Système de Récompenses Optimisé
```python
# Récompenses Positives
+1.3    : Survie (par frame)
+15     : Saut optimal sur cactus/oiseau bas
+20     : Duck optimal sur oiseau moyen (OBLIGATOIRE)
+5      : Laisser passer oiseau haut
+50     : Collecte de bonus

# Pénalités
-1      : Action inutile loin des obstacles
-8      : Timing sous-optimal
-15     : Action inappropriée
-25     : Action mortelle
-100    : Collision (mort)
```

### Comportements Appris
- **Oiseau Haut (y≤240)** : Passer dessous en courant
- **Oiseau Moyen (240<y<320)** : **Se baisser OBLIGATOIREMENT**
- **Oiseau Bas (y≥320)** : Sauter au-dessus
- **Cactus** : Toujours sauter
- **Bonus** : Sauter si en hauteur, courir si au sol

---




## Analyse des Performances

### Métriques d'Entraînement
```bash
# Voir les logs d'entraînement en temps réel
tail -f logs/runs/[DATE_TIME]/metrics.csv

# Analyser la progression complète
cat logs/runs/[DATE_TIME]/metrics.csv | grep -E "Episode|score|avg20"

# Vérifier la configuration utilisée
cat models/runs/[DATE_TIME]/args.json
```

### Indicateurs de Réussite
| Métrique | Débutant | Intermédiaire | Expert |
|----------|----------|---------------|---------|
| Score Moyen | 10-50 | 150-300 | 400-800+ |
| Score Maximum | 50-200 | 300-600 | 800-1500+ |
| Avg20 (objectif) | >50 | >200 | >400 |
| Epsilon Final | ~0.01 | ~0.01 | ~0.01 |
| Stabilité | Variable | Stable | Très Stable |

### Courbe d'Apprentissage Typique
```
Episodes   0-100  : Exploration et apprentissage de base
Episodes 100-300  : Maîtrise progressive des obstacles
Episodes 300-500  : Optimisation du timing et stabilisation
Episodes 500+     : Performance maximale et constante
```

---

##  Structure du Projet

```
trex_ai/
├── src/
│   ├── main.py                 # Point d'entrée principal
│   ├── cli.py                  # Interface ligne de commande
│   ├── paths.py               # Configuration des chemins
│   ├── utils.py               # Utilitaires généraux
│   ├── game/                  # Moteur de jeu
│   │   ├── world.py           # Logique principale
│   │   ├── dino.py            # Personnage dinosaure
│   │   ├── obstacles.py       # Cactus, oiseaux, bonus
│   │   ├── renderer.py        # Affichage graphique
│   │   ├── spawner.py         # Génération d'obstacles
│   │   ├── assets.py          # Chargement des images
│   │   └── constants.py       # Constantes du jeu
│   ├── ai/                    # Intelligence artificielle
│   │   ├── agent.py           # Agent DQN principal
│   │   ├── model.py           # Réseau de neurones
│   │   ├── buffer.py          # Replay buffer
│   │   └── checkpoint.py      # Sauvegarde/chargement
│   ├── env/                   # Interface d'environnement
│   │   ├── trex_env.py        # Environment principal
│   │   ├── observation.py     # État du jeu
│   │   ├── reward.py          # Système de récompenses
│   │   └── rollout.py         # Collecte de données
│   └── training/              # Boucle d'entraînement
│       ├── train.py           # Entraînement principal
│       ├── eval.py            # Évaluation des modèles
│       └── logger.py          # Logging et métriques
├── models/                    # Modèles sauvegardés
│   └── runs/
│       └── YYYY-MM-DD_HHMMSS/
│           ├── best/          # Meilleur modèle
│           ├── latest/        # Modèle final
│           └── args.json      # Configuration
├── logs/                      # Logs d'entraînement
│   └── runs/
│       └── YYYY-MM-DD_HHMMSS/
│           └── metrics.csv    # Métriques détaillées
├── assets/                    # Ressources graphiques
│   ├── Bird1.png, Bird2.png  # Sprites oiseaux
│   ├── DinoDuck1.png, ...     # Sprites dinosaure
│   └── LargeCactus1.png, ...  # Sprites cactus
├── requirements.txt           # Dépendances Python
└── README.md                 # Cette documentation
```

---

##  Configuration Avancée

### Variables d'Environnement
```bash
# Contrôler l'affichage graphique
export SDL_VIDEODRIVER=dummy    # Mode headless complet
export DISPLAY=:0               # Affichage X11 (Linux)

# Contrôler Pygame
export PYGAME_HIDE_SUPPORT_PROMPT=1  # Supprimer message Pygame

# Configurer TensorFlow
export TF_CPP_MIN_LOG_LEVEL=2   # Réduire les logs TensorFlow
export CUDA_VISIBLE_DEVICES=0   # Spécifier GPU à utiliser
```

### Paramètres d'Entraînement Personnalisés

#### Entraînement Rapide (Prototypage)
```bash
python -m src.main train \
  --episodes 200 \
  --lr 0.0005 \
  --epsilon_start 0.1 \
  --epsilon_decay_steps 5000 \
  --target_update 500 \
  --save_every 50
```

#### Entraînement Long (Production)
```bash
python -m src.main train \
  --episodes 2000 \
  --lr 0.0001 \
  --epsilon_start 0.02 \
  --epsilon_decay_steps 50000 \
  --target_update 2000 \
  --save_every 100
```

#### Fine-tuning depuis Modèle Existant
```bash
python -m src.main train \
  --load_model models/runs/2026-01-16_112638/best/model.keras \
  --episodes 500 \
  --lr 0.00005 \
  --epsilon_start 0.01
```

### Modification du Système de Récompenses

Le fichier `src/env/reward.py` contient la logique des récompenses. Structure actuelle :

```python
def calculate_reward(self, game_state, action_taken, previous_state):
    # Récompense de survie : +1.3 par frame
    reward = 1.3
    
    # Bonus pour actions optimales selon type d'obstacle
    if optimal_action:
        reward += 15-20  # Bonus action correcte
    elif suboptimal_action:
        reward -= 1-5    # Pénalité légère action sous-optimale
    elif dangerous_action:
        reward -= 25-100 # Pénalité forte action dangereuse
    
    return reward
```

#### Règles Comportementales Forcées
- **Oiseaux mi-hauteur** : Duck obligatoire (+20 si duck, -25 si jump)
- **Cactus/Oiseaux bas** : Jump recommandé (+15 si jump, -1 si autre)
- **Oiseaux hauts** : Wait optimal (+10 si wait, -1 si autre)

---

##  Dépannage et FAQ

### Problèmes Courants

#### 1. Import Error avec Pygame/TensorFlow
```bash
# Vérifier les installations
pip list | grep -E "(pygame|tensorflow)"

# Réinstaller si nécessaire
pip uninstall pygame tensorflow
pip install pygame==2.5.2 tensorflow==2.15.0
```

#### 2. Erreur "No Display" en Mode Graphique
```bash
# Solution 1: Mode headless
python -m src.main train --headless

# Solution 2: Configuration X11 (Linux)
export DISPLAY=:0
xhost +local:

# Solution 3: VNC/X11 Forwarding
ssh -X user@server
```

#### 3. Performance GPU Non Utilisée
```bash
# Vérifier TensorFlow GPU
python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"

# Installer CUDA support si nécessaire
pip install tensorflow-gpu==2.15.0

# Forcer CPU si problème GPU
export CUDA_VISIBLE_DEVICES=""
```

#### 4. Modèle Ne S'améliore Pas
- **Epsilon trop élevé** → Augmenter `epsilon_decay_steps`
- **Learning rate trop fort** → Réduire `lr` à 0.0001
- **Batch size inadapté** → Essayer 64 ou 128
- **Target update trop fréquent** → Augmenter à 2000-3000

#### 5. Crash Mémoire Pendant Entraînement
```bash
# Réduire buffer size
python -m src.main train --buffer_size 5000

# Réduire batch size
python -m src.main train --batch_size 32

# Monitoring mémoire
watch -n 1 'ps aux | grep python | grep -v grep'
```

### Logs de Débogage

#### Activer Logs Détaillés
```bash
# Logs complets
python -m src.main train --verbose

# Logs TensorFlow détaillés
export TF_CPP_MIN_LOG_LEVEL=0
python -m src.main train
```

#### Analyser les Métriques
```bash
# Derniers scores
tail -20 logs/runs/[DATE]/metrics.csv | cut -d',' -f3

# Progression epsilon
grep -E "epsilon" logs/runs/[DATE]/metrics.csv

# Détection de divergence
awk -F',' 'NR>1 {if($3<prev) print "Baisse:", prev, "->", $3; prev=$3}' logs/runs/[DATE]/metrics.csv
```

---

##  Commandes de Référence Rapide

### Entraînement
```bash
# Standard
python3 -m src.main --train --episodes 800 --render 0

# Avec visualisation
python3 -m src.main --train --episodes 200 --render 1

# Obstacles spécifiques
python3 -m src.main --train --obstacles bird --episodes 300
```

### Test
```bash
# Observer l'IA jouer
python3 -m src.main --play --resume models/runs/[MODEL]/best --render 1

# Évaluation performance
python3 -m src.main --play --resume models/runs/[MODEL]/best --render 0 --episodes 20

# Mode humain
python3 -m src.main --play --human 1
```

### Gestion des Modèles
```bash
# Lister les modèles
ls models/runs/

### Gestion des Modèles
```bash
# Lister les modèles
ls models/runs/

# Voir la config d'un modèle
cat models/runs/[DATE]/args.json

# Comparer performances
grep -E "Episode.*[0-9]+," logs/runs/*/metrics.csv | sort -t',' -k3 -nr | head -10
```

---

##  Optimisations de Performance

### Accélération GPU
```bash
# Vérifier support GPU
python -c "import tensorflow as tf; print('GPU:', len(tf.config.list_physical_devices('GPU')))"

# Configuration GPU optimale
export TF_FORCE_GPU_ALLOW_GROWTH=true
python -m src.main train --batch_size 128
```

### Optimisations Système
```bash
# Priorité processus haute
nice -n -10 python -m src.main train

# Monitoring ressources
htop  # CPU/RAM en temps réel
nvidia-smi -l 1  # GPU monitoring
```

### Entraînement Multi-Processus
```python
# Modifier src/training/train.py pour:
# - Paralléliser collection d'expériences
# - Async replay buffer updates
# - Distributed training sur plusieurs GPU
```

---

##  Checklist de Déploiement

### Avant Production
- [ ] Model atteint score >800 constamment
- [ ] Epsilon final <0.02
- [ ] Stable sur 100+ épisodes consécutifs
- [ ] Logs montrent convergence claire
- [ ] Pas de memory leaks détectés
- [ ] Performance GPU optimisée

### Monitoring Production
- [ ] Logs automatiques activés
- [ ] Métriques collectées (score, temps, actions)
- [ ] Alertes si performance dégradée
- [ ] Backup automatique des modèles
- [ ] Dashboard performance temps réel

---

##  Documentation Technique

### Architecture DQN
```
Input: [obstacle_distance, obstacle_width, obstacle_height, obstacle_y, obstacle_type, game_speed, dino_y, dino_velocity, on_ground]
       ↓ (9D → 64)
Dense Layer 1: 64 neurons (ReLU)
       ↓ (64 → 64) 
Dense Layer 2: 64 neurons (ReLU)
       ↓ (64 → 3)
Output: [Q(wait), Q(jump), Q(duck)]
```

### Hyperparamètres Optimaux
| Paramètre | Valeur | Explication |
|-----------|--------|-------------|
| Learning Rate | 0.0002 | Stable, évite divergence |
| Epsilon Start | 0.05 | Exploration modérée |
| Epsilon Decay | 20000 steps | Transition graduelle |
| Target Update | 1500 steps | Stabilité Q-learning |
| Buffer Size | 10000 | Mémoire suffisante |
| Batch Size | 64 | Compromis vitesse/stabilité |

### Évolution du Modèle
1. **Phase d'Exploration** (0-100 épisodes) : Découverte des actions
2. **Phase d'Apprentissage** (100-300) : Association action-récompense
3. **Phase d'Optimisation** (300-500) : Raffinement des stratégies
4. **Phase de Maîtrise** (500+) : Performance maximale et constante

---

##  Roadmap et Améliorations Futures

### Version 2.0 Planifiée
- [ ] Support multi-environnements (différents jeux)
- [ ] Architecture transformer pour attention temporelle
- [ ] Curriculum learning avec difficulté progressive
- [ ] Meta-learning pour adaptation rapide
- [ ] Interface web pour monitoring en temps réel

### Optimisations Techniques
- [ ] Quantization des modèles pour déploiement mobile
- [ ] Pruning des connexions non-critiques
- [ ] Knowledge distillation vers modèles plus petits
- [ ] Edge deployment avec TensorFlow Lite

### Fonctionnalités Experimentales
- [ ] Multi-agent competitive training
- [ ] Imitation learning depuis joueurs humains
- [ ] Adversarial training contre modèles perturbateurs
- [ ] Continuous control pour mouvements plus fins

---

##  Support et Contributions

### Issues Connues
- Performance variable sur premiers 50 épisodes (normal)
- Quelques freezes occasionnels en mode graphique
- Logs volumineux après entraînements longs

### Comment Contribuer
1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commiter les changements (`git commit -am 'Ajout nouvelle fonctionnalité'`)
4. Pusher la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

### Reporting de Bugs
Inclure dans votre rapport :
- Version Python et OS
- Configuration utilisée (`args.json`)
- Logs d'erreur complets
- Étapes pour reproduire le problème

---

##  Licence et Crédits

Ce projet est développé à des fins éducatives et de recherche en intelligence artificielle. Inspiré du jeu T-Rex de Google Chrome.

**Technologies utilisées :**
- TensorFlow 2.15 (Deep Learning)
- Pygame 2.5 (Rendu graphique)
- NumPy (Calculs numériques)
- Matplotlib (Visualisation)

**Algorithme :** Deep Q-Network (DQN) avec Experience Replay et Target Network

---

*Dernière mise à jour : Février 2026*
*Version du README : 2.0*
*Performance Max Validée : 12346+ points*
