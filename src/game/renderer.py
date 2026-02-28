from dataclasses import dataclass
from typing import Optional
import os

import pygame

from .constants import BG_COLOR, FG_COLOR


@dataclass
class RenderState:
    quit: bool = False


class Renderer:
    def __init__(self, width: int, height: int, fps: int):
        pygame.init()
        # Centrer la fenêtre sur l'écran
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("T-Rex AI (Pygame)")
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.font = pygame.font.SysFont("arial", 20)

    def tick(self) -> float:
        # dt seconds
        return self.clock.tick(self.fps) / 1000.0

    def handle_events(self) -> RenderState:
        rs = RenderState(quit=False)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rs.quit = True
        return rs

    def draw(self, world, human_hint: Optional[str] = None, game_over: bool = False) -> None:
        self.screen.fill(BG_COLOR)

        # Nuages (arrière-plan)
        for cloud in world.clouds:
            self.screen.blit(cloud.image, (int(cloud.x), int(cloud.y)))

        # Track (sol) à y=380 comme le jeu original
        track = world.assets.track
        track_y = 380
        track_width = track.get_width()
        for tx in range(0, world.width + track_width, track_width):
            self.screen.blit(track, (tx, track_y))

        # dino
        self.screen.blit(world.dino.sprite(), (int(world.dino.x), int(world.dino.y)))

        # obstacles
        for ob in world.obstacles:
            if hasattr(ob, "sprite"):
                self.screen.blit(ob.sprite, (int(ob.x), int(ob.y)))
            elif hasattr(ob, "draw"):
                ob.draw(self.screen)

        # HUD
        txt = self.font.render(f"Score: {int(world.score)}  Speed: {world.speed:.2f}", True, FG_COLOR)
        self.screen.blit(txt, (10, 10))
        if human_hint and not game_over:
            hint = self.font.render(human_hint, True, FG_COLOR)
            self.screen.blit(hint, (10, 35))

        # Écran Game Over
        if game_over:
            # Image "Game Over"
            go_img = world.assets.game_over
            go_x = (world.width - go_img.get_width()) // 2
            go_y = world.height // 3
            self.screen.blit(go_img, (go_x, go_y))
            
            # Bouton Reset
            reset_img = world.assets.reset
            reset_x = (world.width - reset_img.get_width()) // 2
            reset_y = go_y + go_img.get_height() + 20
            self.screen.blit(reset_img, (reset_x, reset_y))
            
            # Texte "Appuyez sur ESPACE pour recommencer"
            restart_text = self.font.render("Appuyez sur ESPACE pour recommencer", True, FG_COLOR)
            text_x = (world.width - restart_text.get_width()) // 2
            text_y = reset_y + reset_img.get_height() + 20
            self.screen.blit(restart_text, (text_x, text_y))

        pygame.display.flip()

    def close(self) -> None:
        pygame.quit()
