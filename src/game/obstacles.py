from dataclasses import dataclass
from typing import List, Literal, Optional

import pygame


ObstacleKind = Literal["cactus", "bird", "bonus"]


@dataclass
class ObstacleState:
    x: float
    y: float
    w: int
    h: int
    kind: int  # 0 cactus, 1 bird, 2 bonus


class Obstacle:
    def __init__(self, x: float, y: float, sprite: pygame.Surface, kind: ObstacleKind, 
                 sprites: Optional[List[pygame.Surface]] = None, shrink_hitbox: int = 0):
        self.x = float(x)
        self.y = float(y)
        self.sprite = sprite
        self.sprites = sprites if sprites else [sprite]
        self.kind = kind
        self.shrink = shrink_hitbox
        self.passed = False  # Pour tracker si l'obstacle a été passé (score)
        # Hitbox réduite pour les cactus
        full_rect = sprite.get_rect(topleft=(int(self.x), int(self.y)))
        self.rect = full_rect.inflate(-shrink_hitbox * 2, -shrink_hitbox)  # réduit largeur et hauteur
        self.rect.bottom = full_rect.bottom  # garde le bas aligné
        
        # Animation
        self.anim_frame = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.15  # secondes entre frames 

    def update(self, speed: float, dt: float) -> None:
        k = min(1.0, dt * 60.0)  # Plafonne k pour stabilité
        self.x -= speed * k
        full_rect = self.sprite.get_rect(topleft=(int(self.x), int(self.y)))
        self.rect = full_rect.inflate(-self.shrink * 2, -self.shrink)
        self.rect.bottom = full_rect.bottom
        
        # Animation pour les oiseaux
        if self.kind == "bird" and len(self.sprites) > 1:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0.0
                self.anim_frame = (self.anim_frame + 1) % len(self.sprites)
                self.sprite = self.sprites[self.anim_frame]

    def offscreen(self) -> bool:
        return self.x + self.rect.width < 0

    def state(self) -> ObstacleState:
        kind_id = 0 if self.kind == "cactus" else 1 if self.kind == "bird" else 2
        return ObstacleState(x=self.x, y=self.y, w=self.rect.width, h=self.rect.height, kind=kind_id)


def make_cactus(x: float, ground_y: int, sprite: pygame.Surface, is_large: bool = True) -> Obstacle:
    # Positions comme le jeu original: LargeCactus Y=300, SmallCactus Y=325
    if is_large:
        y = 300
        # Si le sprite est le plus large (3 segments), shrink plus fort
        if sprite.get_width() >= 75:
            shrink = 30  # Très permissif pour les grands cactus à 3 segments
        else:
            shrink = 13  # Légère réduction pour les autres gros cactus
    else:
        y = 325
        shrink = 0  # Pas de réduction pour les petits cactus (déjà étroits)
    return Obstacle(x=x, y=y, sprite=sprite, kind="cactus", shrink_hitbox=shrink)


def make_bird(x: float, ground_y: int, sprites: List[pygame.Surface], height_mode: int = 0) -> Obstacle:
    # Hauteurs des oiseaux comme le jeu Chrome:
    # - Haut (mode 0): y=200 - Passer dessous, impossible à sauter
    # - Moyen (mode 1): y=280 - Se baisser ou passer dessous
    # - Bas (mode 2): y=340 - SAUTER par-dessus (vole au niveau du sol)
    bird_heights = [200, 280, 340]
    y = bird_heights[height_mode % 3]
    return Obstacle(x=x, y=y, sprite=sprites[0], kind="bird", sprites=sprites, shrink_hitbox=20)
