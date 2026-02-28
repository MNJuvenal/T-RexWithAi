import os
from dataclasses import dataclass
from typing import Dict, List

import pygame


@dataclass
class GameAssets:
    dino_run1: pygame.Surface
    dino_run2: pygame.Surface
    dino_jump: pygame.Surface
    dino_duck1: pygame.Surface
    dino_duck2: pygame.Surface
    cacti: List[pygame.Surface]
    birds: List[pygame.Surface]
    track: pygame.Surface
    cloud: pygame.Surface
    game_over: pygame.Surface
    reset: pygame.Surface


def _load_image(path: str) -> pygame.Surface:
    img = pygame.image.load(path).convert_alpha()
    return img


def _scale_image(img: pygame.Surface, scale: float) -> pygame.Surface:
    """Redimensionne une image par un facteur de scale"""
    new_width = int(img.get_width() * scale)
    new_height = int(img.get_height() * scale)
    return pygame.transform.scale(img, (new_width, new_height))


def load_assets(assets_dir: str) -> GameAssets:
    # pygame must be initialized before calling (for convert_alpha)
    
    # Sprites du dino (taille originale comme le jeu Chrome)
    dino_run1 = _load_image(os.path.join(assets_dir, "DinoRun1.png"))
    dino_run2 = _load_image(os.path.join(assets_dir, "DinoRun2.png"))
    dino_jump = _load_image(os.path.join(assets_dir, "DinoJump.png"))
    dino_duck1 = _load_image(os.path.join(assets_dir, "DinoDuck1.png"))
    dino_duck2 = _load_image(os.path.join(assets_dir, "DinoDuck2.png"))

    # Cactus (taille originale) - LargeCactus d'abord, puis SmallCactus
    cacti = [
        _load_image(os.path.join(assets_dir, "LargeCactus1.png")),
        _load_image(os.path.join(assets_dir, "LargeCactus2.png")),
        _load_image(os.path.join(assets_dir, "LargeCactus3.png")),
        _load_image(os.path.join(assets_dir, "SmallCactus1.png")),
        _load_image(os.path.join(assets_dir, "SmallCactus2.png")),
        _load_image(os.path.join(assets_dir, "SmallCactus3.png")),
    ]

    # Oiseaux (taille originale)
    birds = [
        _load_image(os.path.join(assets_dir, "Bird1.png")),
        _load_image(os.path.join(assets_dir, "Bird2.png")),
    ]

    track = _load_image(os.path.join(assets_dir, "Track.png"))
    cloud = _load_image(os.path.join(assets_dir, "Cloud.png"))
    game_over = _load_image(os.path.join(assets_dir, "GameOver.png"))
    reset = _load_image(os.path.join(assets_dir, "Reset.png"))

    return GameAssets(
        dino_run1=dino_run1,
        dino_run2=dino_run2,
        dino_jump=dino_jump,
        dino_duck1=dino_duck1,
        dino_duck2=dino_duck2,
        cacti=cacti,
        birds=birds,
        track=track,
        cloud=cloud,
        game_over=game_over,
        reset=reset,
    )
