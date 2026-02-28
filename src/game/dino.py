from dataclasses import dataclass
from typing import Optional

import pygame


@dataclass
class DinoState:
    x: float
    y: float
    vy: float
    on_ground: bool


class Dino:
    # Positions Y comme le jeu original
    Y_POS = 310
    Y_POS_DUCK = 340
    
    def __init__(self, x: int, ground_y: int, jump_vel: float, gravity: float,
                 sprite_run1: pygame.Surface, sprite_run2: pygame.Surface, sprite_jump: pygame.Surface,
                 sprite_duck1: Optional[pygame.Surface] = None, sprite_duck2: Optional[pygame.Surface] = None):
        self.x = float(x)
        # ground_y est la position Y du dino au sol (comme Y_POS=310 dans le jeu original)
        self.ground_y = float(ground_y)
        self.ground_y_duck = float(ground_y + 30)  # Y_POS_DUCK = 340
        self.y = float(ground_y)
        self.vy = 0.0
        self.on_ground = True
        self.is_ducking = False
        self.jump_vel = float(jump_vel)
        self.gravity = float(gravity)
        self.sprite_run1 = sprite_run1
        self.sprite_run2 = sprite_run2
        self.sprite_jump = sprite_jump
        self.sprite_duck1 = sprite_duck1 if sprite_duck1 else sprite_run1
        self.sprite_duck2 = sprite_duck2 if sprite_duck2 else sprite_run2
        self.rect = sprite_run1.get_rect(topleft=(int(self.x), int(self.y)))
        
        # Animation de course
        self.anim_frame = 0
        self.anim_timer = 0.0
        self.anim_speed = 0.1  # secondes entre frames

    def jump(self) -> None:
        if self.on_ground and not self.is_ducking:
            self.vy = self.jump_vel
            self.on_ground = False

    def duck(self) -> None:
        """Se baisser - seulement au sol"""
        if self.on_ground:
            self.is_ducking = True
            self.y = self.ground_y_duck
    
    def stand(self) -> None:
        """Se relever"""
        if self.is_ducking:
            self.is_ducking = False
            if self.on_ground:
                self.y = self.ground_y

    def update(self, dt: float) -> None:
        # dt in seconds, but physics tuned for frame-ish values; use dt*60 factor
        k = min(1.0, dt * 60.0)  # Plafonne k pour stabilité
        if not self.on_ground:
            self.is_ducking = False  # Ne peut pas se baisser en l'air
            self.vy += self.gravity * k
            self.y += self.vy * k
            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.vy = 0.0
                self.on_ground = True
        
        # Animation de course/duck
        if self.on_ground:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0.0
                self.anim_frame = 1 - self.anim_frame  # Alterner entre 0 et 1
        
        # Mettre à jour le rect avec le bon sprite
        current_sprite = self.sprite()
        full_rect = current_sprite.get_rect(topleft=(int(self.x), int(self.y)))
        # Hitbox réduite (plus permissive) - shrink de 10 pixels de chaque côté
        self.rect = full_rect.inflate(-20, -10)
        self.rect.bottom = full_rect.bottom  # Garder le bas aligné

    def sprite(self) -> pygame.Surface:
        if not self.on_ground:
            return self.sprite_jump
        if self.is_ducking:
            return self.sprite_duck1 if self.anim_frame == 0 else self.sprite_duck2
        return self.sprite_run1 if self.anim_frame == 0 else self.sprite_run2

    def state(self) -> DinoState:
        return DinoState(x=self.x, y=self.y, vy=self.vy, on_ground=self.on_ground)
