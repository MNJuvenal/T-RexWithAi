from dataclasses import dataclass
from typing import List, Optional
import random

from .constants import GROUND_Y
from .dino import Dino
from .obstacles import Obstacle
from .spawner import Spawner


@dataclass
class WorldInfo:
    score: float
    speed: float
    distance: float
    bonus_collected: bool = False


class Cloud:
    """Nuage décoratif qui se déplace en arrière-plan"""
    def __init__(self, x: float, y: float, image):
        self.x = x
        self.y = y
        self.image = image
        self.width = image.get_width()
    
    def update(self, speed: float, dt: float) -> None:
        k = min(1.0, dt * 60.0)  # Plafonne k pour stabilité
        self.x -= speed * k * 0.5  # Les nuages bougent plus lentement
    
    def offscreen(self) -> bool:
        return self.x < -self.width


class World:
    def __init__(self, width: int, height: int, assets, spawner: Spawner,
                 base_speed: float, max_speed: float,
                 gravity: float, jump_vel: float, acceleration: float = 0.001):
        self.width = width
        self.height = height
        self.assets = assets
        self.spawner = spawner

        self.base_speed = float(base_speed)
        self.max_speed = float(max_speed)
        # Acceleration per frame (units of speed per frame). Chrome uses 0.001
        self.acceleration = float(acceleration)

        self.gravity = float(gravity)
        self.jump_vel = float(jump_vel)

        self.ground_y = GROUND_Y

        self.dino: Dino
        self.obstacles: List[Obstacle]

        self.score = 0.0
        self.speed = self.base_speed
        self.distance = 0.0

        self.reset()

    def reset(self, seed: Optional[int] = None) -> None:
        # seed handled upstream (utils.set_seed)
        self.score = 0.0
        self.speed = self.base_speed
        self.distance = 0.0

        self.dino = Dino(
            x=80,
            ground_y=self.ground_y,
            jump_vel=self.jump_vel,
            gravity=self.gravity,
            sprite_run1=self.assets.dino_run1,
            sprite_run2=self.assets.dino_run2,
            sprite_jump=self.assets.dino_jump,
            sprite_duck1=self.assets.dino_duck1,
            sprite_duck2=self.assets.dino_duck2,
        )
        self.obstacles = []
        self.clouds: List[Cloud] = []
        # Créer quelques nuages initiaux
        self._spawn_initial_clouds()
        self.spawner.reset(self)

    def _spawn_initial_clouds(self) -> None:
        """Créer quelques nuages au démarrage"""
        for i in range(3):
            x = random.randint(200, self.width) + i * 400
            y = random.randint(50, 120)
            self.clouds.append(Cloud(x, y, self.assets.cloud))
    
    def _update_clouds(self, dt: float) -> None:
        """Mettre à jour et spawner des nuages"""
        for cloud in self.clouds:
            cloud.update(self.speed, dt)
        
        # Retirer les nuages hors écran
        self.clouds = [c for c in self.clouds if not c.offscreen()]
        
        # Spawner un nouveau nuage aléatoirement
        if len(self.clouds) < 5 and random.random() < 0.01:
            x = self.width + random.randint(100, 300)
            y = random.randint(50, 120)
            self.clouds.append(Cloud(x, y, self.assets.cloud))

    def _update_speed(self, dt: float) -> None:
        """
        Update the world speed by applying per-frame acceleration (Chrome-like).
        We scale the per-frame increment by dt*60 so the behaviour is stable
        whether the environment uses fixed or variable dt.
        """
        k = min(1.0, dt * 60.0)  # PLAFONNER k pour éviter accélération due aux FPS bas
        self.speed = min(self.max_speed, self.speed + (self.acceleration * k))

    def step(self, action: int, dt: float) -> tuple[bool, WorldInfo]:
        # action: 0 nothing, 1 jump, 2 duck
        if action == 1:
            self.dino.jump()
        elif action == 2:
            self.dino.duck()
        else:
            self.dino.stand()

        self._update_speed(dt)

        # Move world
        k = min(1.0, dt * 60.0)  # PLAFONNER k ici aussi pour cohérence
        self.distance += self.speed * k
        
        # Score comme le jeu Chrome: distance × 0.025, arrondi
        self.score = round(self.distance * 0.025)

        self.dino.update(dt)
        self.spawner.update(self)
        self._update_clouds(dt)

        for ob in self.obstacles:
            ob.update(self.speed, dt)

        # Marquer les obstacles passés (pour le système de récompense)
        for ob in self.obstacles:
            if ob.x + ob.rect.width < self.dino.x and not getattr(ob, 'passed', False):
                ob.passed = True




        # Remove collected bonus obstacles so they disappear
        self.obstacles = [ob for ob in self.obstacles if not ob.offscreen() and not getattr(ob, 'collected', False)]


        # Gestion des bonus comme obstacles (plus besoin de liste séparée)
        for ob in self.obstacles:
            if getattr(ob, 'collected', None) is not None and not ob.collected and self.dino.rect.colliderect(ob.rect):
                ob.collected = True
                self.score += 10
                self.last_bonus_collected = True
                break
        else:
            self.last_bonus_collected = False


        done = any(self.dino.rect.colliderect(ob.rect) for ob in self.obstacles if not getattr(ob, 'collected', False))
        info = WorldInfo(score=self.score, speed=self.speed, distance=self.distance, bonus_collected=self.last_bonus_collected)
        return done, info
