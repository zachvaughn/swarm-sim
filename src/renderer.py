import pygame
import numpy as np


class Renderer:
    def __init__(self, width: int, height: int):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Swarm Simulation")
        self.clock = pygame.time.Clock()

        # color mapping for different agent statuses and environment
        self.colors = {
            "active": (50, 150, 255),
            "arrived": (50, 200, 50),
            "removed": (150, 150, 150),
            "obstacle": (100, 100, 100),
            "hazard_zone": (200, 50, 50),
            "destination": (50, 200, 50),
            "background": (20, 20, 20),
        }

    def draw(self, agents: list, environment) -> None:
        self.screen.fill(self.colors["background"])

        # draw destination zone
        self._draw_circle(environment.destination.center, environment.destination.radius,
                           self.colors["destination"], filled=False)

        # draw obstacles
        for obs in environment.obstacles:
            self._draw_circle(obs.position, obs.size, self.colors["obstacle"], filled=True)

        # draw hazard zones
        for hz in environment.hazard_zones:
            self._draw_circle(hz.center, hz.radius, self.colors["hazard_zone"], filled=False)

        # draw agents
        for agent in agents:
            color = self.colors.get(agent.status, (255, 255, 255))
            self._draw_circle(agent.position, 4, color, filled=True)

        pygame.display.flip()

    def _draw_circle(self, center: np.ndarray, radius: float, color: tuple, filled: bool, fill_alpha: int = 60) -> None:
        pos = (int(center[0]), int(center[1]))
        r = int(radius)

        if filled:
            # solid fill for agents/obstacles
            pygame.draw.circle(self.screen, color, pos, r, 0)
        else:
            # low opacity fill/solid outline for zones
            temp_surface = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, (*color, fill_alpha), (r, r), r)
            self.screen.blit(temp_surface, (pos[0] - r, pos[1] - r))
            pygame.draw.circle(self.screen, color, pos, r, 2)

    def tick(self, fps: int = 60) -> None:
        self.clock.tick(fps)

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def quit(self) -> None:
        pygame.quit()