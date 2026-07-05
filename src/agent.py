from __future__ import annotations
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from environment import Environment

class Agent:
    def __init__(self, agent_id: int, position: np.ndarray, velocity: np.ndarray,
                 perception_radius: float, max_speed: float):
        self.id = agent_id
        self.position = position # current position as a 2D numpy array
        self.velocity = velocity # current velocity as a 2D numpy array
        self.perception_radius_sq = perception_radius ** 2 # how far the agent can perceive neighbors
        self.max_speed = max_speed # maximum speed the agent can travel
        self.status = "active" # active, removed, or arrived

    def get_neighbor_data(self, agents: list[Agent]) -> list[tuple[Agent, np.ndarray, float]]:
        # find all other active agents within perception radius
        neighbors = []
        for other in agents:
            if other.id == self.id or other.status != "active":
                continue
            diff = self.position - other.position
            dist_sq = np.dot(diff, diff)
            if dist_sq <= self.perception_radius_sq:
                neighbors.append((other, diff, dist_sq))
        return neighbors

    def compute_flocking(self, neighbor_data: list[tuple[Agent, np.ndarray, float]],
                          w_sep: float = 1.0, w_align: float = 1.0, w_coh: float = 1.0) -> np.ndarray:
        # separation, alignment, cohesion
        if not neighbor_data:
            return np.zeros(2)

        # separation steer away from neighbors that are too close
        sep_force = np.zeros(2)
        avg_velocity = np.zeros(2)
        avg_position = np.zeros(2)

        for other, diff, dist_sq in neighbor_data:
            if dist_sq > 0:
                sep_force += diff / dist_sq
            avg_velocity += other.velocity
            avg_position += other.position

        count = len(neighbor_data)
        align_force = (avg_velocity / count) - self.velocity
        coh_force = (avg_position / count) - self.position

        return w_sep * sep_force + w_align * align_force + w_coh * coh_force

    def compute_potential_field(self, env: Environment,
                                k_att: float = 1.0, k_rep: float = 100.0, rho_0: float = 50.0) -> np.ndarray:
        # attractive force pulls the agent toward the destination
        att_force = k_att * (env.destination.center - self.position)

        # repulsive force pushes the agent away from every obstacle within influence range
        rep_force = np.zeros(2)
        nearby_obstacles = env.get_obstacles_within(self.position, rho_0)
        for obstacle in nearby_obstacles:
            dist = obstacle.distance_to(self.position)
            if dist <= 0:
                continue
            direction = (self.position - obstacle.position) / np.linalg.norm(self.position - obstacle.position)
            rep_force += k_rep * (1.0 / dist - 1.0 / rho_0) * (1.0 / dist ** 2) * direction

        return att_force + rep_force

    def update(self, force: np.ndarray, env: Environment, dt: float = 1.0):
        # update velocity and position based on combined force
        self.velocity += force * dt
        speed = np.linalg.norm(self.velocity)
        if speed > self.max_speed:
            self.velocity = (self.velocity / speed) * self.max_speed
        self.position += self.velocity * dt

        # clamp position to stay within environment bounds
        self.position[0] = np.clip(self.position[0], 0, env.width)
        self.position[1] = np.clip(self.position[1], 0, env.height)

    def check_arrival(self, destination) -> None:
        if destination.contains(self.position):
            self.status = "arrived"