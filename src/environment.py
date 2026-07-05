import numpy as np

from obstacle import Obstacle
from hazardzone import HazardZone
from zone import Zone

class Environment:
    def __init__(self, width: int, height: int, destination: Zone):
        self.width = width # width of the simulation grid
        self.height = height # height of the simulation grid
        self.obstacles: list[Obstacle] = [] # list of static obstacles
        self.hazard_zones: list[HazardZone] = [] # list of hazard zones
        self.destination = destination # the zone agents are trying to reach

    def get_nearest_obstacle(self, pos: np.ndarray):
        # returns (distance, obstacle) of the closest obstacle to a given position
        # returns (None, None) if there are no obstacles
        if not self.obstacles:
            return None, None

        nearest_obstacle = min(self.obstacles, key=lambda obs: obs.distance_to(pos))
        nearest_distance = nearest_obstacle.distance_to(pos)
        return nearest_distance, nearest_obstacle

    def get_obstacles_within(self, pos: np.ndarray, radius: float) -> list[Obstacle]:
        # returns all obstacles whose influence radius overlaps the given radius from pos
        return [obs for obs in self.obstacles if obs.distance_to(pos) <= radius]

    def get_hazard_zones_at(self, pos: np.ndarray) -> list[HazardZone]:
        # returns all hazard zones that contain the given position
        return [zone for zone in self.hazard_zones if zone.contains(pos)]

    def is_in_bounds(self, pos: np.ndarray) -> bool:
        # checks if a position is within the bounds of the environment
        return 0 <= pos[0] <= self.width and 0 <= pos[1] <= self.height