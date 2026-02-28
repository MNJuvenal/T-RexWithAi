import random
from .obstacles import make_cactus, make_bird
from dataclasses import dataclass
from typing import List

@dataclass
class SpawnConfig:
    mode: str
    spawn_distance_px: int
    obstacle_types: List[str]

class Spawner:
    def __init__(self, cfg: SpawnConfig):
        self.cfg = cfg
        self.last_spawn_distance = 0.0
        self.first = True

    def reset(self, world) -> None:
        self.last_spawn_distance = 0.0
        self.first = True
        self._reset_internal() # Hook pour les enfants

    def _reset_internal(self):
        pass

    def update(self, world) -> None:
        raise NotImplementedError

    def _spawn_one(self, world):
        """Logique de génération commune et centralisée"""
        x = world.width + 100
        active = self.cfg.obstacle_types

        # 1. Construire la liste des options possibles selon la config
        options = []
        if "cactus" in active:
            options.extend(["cactus_small", "cactus_large"])
        if "bird" in active:
            options.append("bird")
        if "bonus" in active:
            options.append("bonus")

        if not options:
            options = ["cactus_large"]

        choice = random.choice(options)

        if choice == "bird":
            hm = random.randint(0, 2)
            return make_bird(x=x, ground_y=world.ground_y, sprites=world.assets.birds, height_mode=hm)
        elif choice == "cactus_large":
            sprite = random.choice(world.assets.cacti[:3]) if len(world.assets.cacti) >= 3 else random.choice(world.assets.cacti)
            return make_cactus(x=x, ground_y=world.ground_y, sprite=sprite, is_large=True)
        elif choice == "cactus_small":
            sprite = random.choice(world.assets.cacti[3:6]) if len(world.assets.cacti) > 3 else random.choice(world.assets.cacti)
            return make_cactus(x=x, ground_y=world.ground_y, sprite=sprite, is_large=False)
        elif choice == "bonus": 
            # Bonus = obstacle spécial (rond doré) s
            import pygame
            class SimpleBonus:
                def __init__(self, x, y, size=32):
                    self.x = x
                    self.y = y
                    self.size = size
                    self.rect = pygame.Rect(self.x, self.y, self.size, self.size)
                    self.collected = False
                    self.kind = "bonus"
                def update(self, speed, dt):
                    k = min(1.0, dt * 60.0)  # Plafonne k pour stabilité
                    self.x -= speed * k
                    self.rect.x = int(self.x)
                def draw(self, surface):
                    color = (255, 215, 0)
                    center = (int(self.x + self.size // 2), int(self.y + self.size // 2))
                    radius = self.size // 2
                    pygame.draw.circle(surface, color, center, radius)
                def offscreen(self):
                    return self.x + self.rect.width < 0
            y = world.ground_y - 20 if random.random() < 0.5 else world.ground_y - 120
            return SimpleBonus(x, y)


class RegularSpawner(Spawner):
    """Intervalle fixe défini par spawn_distance_px"""
    
    def update(self, world) -> None:
        if self.first and len(world.obstacles) == 0:
            world.obstacles.append(self._spawn_one(world))
            self.last_spawn_distance = world.distance
            self.first = False
            return

        if (world.distance - self.last_spawn_distance) >= float(self.cfg.spawn_distance_px):
            world.obstacles.append(self._spawn_one(world))
            self.last_spawn_distance = world.distance


class RandomSpawner(Spawner):
    """Intervalle aléatoire entre min et max"""

    def _reset_internal(self):
        self.next_spawn_gap = random.uniform(400, 600)

    def update(self, world) -> None:
        # Initialisation du gap si premier run
        if not hasattr(self, 'next_spawn_gap'):
            self.next_spawn_gap = random.uniform(400, 600)

        if self.first and len(world.obstacles) == 0:
            world.obstacles.append(self._spawn_one(world))
            self.last_spawn_distance = world.distance
            self.first = False
            self.next_spawn_gap = random.uniform(400, 600)
            return

        if (world.distance - self.last_spawn_distance) >= self.next_spawn_gap:
            world.obstacles.append(self._spawn_one(world))
            self.last_spawn_distance = world.distance
            # On recadre le prochain spawn
            self.next_spawn_gap = random.uniform(400, 600)

# Factory inchangée...
def build_spawner(mode: str, spawn_distance_px: int, obstacles_str: str) -> Spawner:
    obstacle_types = [s.strip() for s in obstacles_str.split(",") if s.strip()]
    if not obstacle_types:
        obstacle_types = ["cactus"]

    cfg = SpawnConfig(mode=mode, spawn_distance_px=spawn_distance_px, obstacle_types=obstacle_types)

    if mode == "regular":
        return RegularSpawner(cfg)
    elif mode == "random":
        return RandomSpawner(cfg)
    return RegularSpawner(cfg)