import argparse


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("T-Rex AI (Pygame)")

    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--train", action="store_true", help="Entrainer l'agent")
    mode.add_argument("--play", action="store_true", help="Jouer (agent ou humain)")

    # Global
    p.add_argument("--render", type=int, default=0, choices=[0, 1], help="Activer le rendu Pygame")
    p.add_argument("--episodes", type=int, default=500)
    p.add_argument("--max_steps", type=int, default=5000, help="Max steps par episode")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--fps", type=int, default=60)

    # Game
    p.add_argument("--width", type=int, default=1100)
    p.add_argument("--height", type=int, default=600)

    # Obstacles
    p.add_argument("--spawn_mode", type=str, default="regular", choices=["regular", "random"])
    p.add_argument("--spawn_distance", type=int, default=600, help="Distance fixe (pixels) entre obstacles en mode regular")
    p.add_argument("--obstacles", type=str, default="cactus,bird,bonus", help="Types actifs: cactus ou cactus,bird et bonus")

    # Speed/difficulty (paramètres du jeu Chrome original)
    # Vitesse initiale ~6, max 13, accélération 0.001/frame
    p.add_argument("--base_speed", type=float, default=6.0)
    p.add_argument("--max_speed", type=float, default=13.0)

    # Physics
    p.add_argument("--gravity", type=float, default=0.8)
    p.add_argument("--jump_vel", type=float, default=-19.2)  # Saut plus haut
    p.add_argument("--acceleration", type=float, default=0.004, help="Accélération (par frame) du jeu, comme Chrome)")  # 4× plus rapide = ~30s pour max speed

    # Training / saving
    p.add_argument("--run_name", type=str, default=None)
    p.add_argument("--resume", type=str, default=None, help="Chemin vers models/runs/<run_id>/latest")
    p.add_argument("--save_every", type=int, default=50)
    p.add_argument("--models_dir", type=str, default="models")
    p.add_argument("--logs_dir", type=str, default="logs")

    # DQN
    p.add_argument("--gamma", type=float, default=0.99)
    p.add_argument("--lr", type=float, default=1e-3)
    p.add_argument("--batch_size", type=int, default=64)
    p.add_argument("--buffer_size", type=int, default=50000)
    p.add_argument("--train_start", type=int, default=1000, help="Nb transitions avant d'entrainer")
    p.add_argument("--target_update", type=int, default=1000, help="Steps entre updates du target network")
    p.add_argument("--train_freq", type=int, default=4, help="Entrainer tous les N steps (plus grand = plus rapide)")

    p.add_argument("--epsilon_start", type=float, default=1.0)
    p.add_argument("--epsilon_end", type=float, default=0.01)
    p.add_argument("--epsilon_decay_steps", type=int, default=10000)

    # Play
    p.add_argument("--model", type=str, default=None, help="Chemin vers un modèle (dossier best/latest) pour --play")
    p.add_argument("--human", type=int, default=0, choices=[0, 1], help="En mode play: contrôle humain (ESPACE)")

    return p
