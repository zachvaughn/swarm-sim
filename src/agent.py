import numpy as np

from environment import Environment


class Agent:
    def __init__(self, agent_id: int, position: np.ndarray, velocity: np.ndarray,
                 perception_radius: float, max_speed: float):
        self.id = agent_id
        self.position = position # current position as a 2D numpy array
        self.velocity = velocity # current velocity as a 2D numpy array
        self.perception_radius = perception_radius  # how far the agent can sense neighbors
        self.max_speed = max_speed # maximum speed the agent can travel
        self.status = "active" # active, removed, or arrived

    def get_neighbors(self, agents: list["Agent"]) -> list["Agent"]:
        # find all other active agents within perception radius
        neighbors = []
        for other in agents:
            if other.id == self.id or other.status != "active":
                continue
            distance = np.linalg.norm(other.position - self.position)
            if distance <= self.perception_radius:
                neighbors.append(other)
        return neighbors

    def compute_flocking(self, neighbors: list["Agent"],
                          w_sep: float = 1.0, w_align: float = 1.0, w_coh: float = 1.0) -> np.ndarray:
        # separation, alignment, cohesion
        if not neighbors:
            return np.zeros(2)

        # separation steer away from neighbors that are too close
        sep_force = np.zeros(2)
        for other in neighbors:
            diff = self.position - other.position
            dist_sq = np.dot(diff, diff)
            if dist_sq > 0:
                sep_force += diff / dist_sq

        # alignment steer towards the average heading of neighbors
        avg_velocity = np.mean([other.velocity for other in neighbors], axis=0)
        align_force = avg_velocity - self.velocity

        # cohesion steer towards the average position of neighbors
        avg_position = np.mean([other.position for other in neighbors], axis=0)
        coh_force = avg_position - self.position

        return w_sep * sep_force + w_align * align_force + w_coh * coh_force

    def compute_potential_field(self, env: Environment,
                                k_att: float = 1.0, k_rep: float = 100.0, rho_0: float = 50.0) -> np.ndarray:
        # attractive force pulls the agent toward the destination
        att_force = k_att * (env.destination.center - self.position)

        # repulsive force pushes the agent away from the nearest obstacle
        rep_force = np.zeros(2)
        nearest_dist, nearest_obstacle = env.get_nearest_obstacle(self.position)
        if nearest_obstacle is not None and 0 < nearest_dist <= rho_0:
            direction = (self.position - nearest_obstacle.position) / np.linalg.norm(
                self.position - nearest_obstacle.position)
            rep_force = k_rep * (1.0 / nearest_dist - 1.0 / rho_0) * (1.0 / nearest_dist ** 2) * direction

        return att_force + rep_force

    def update(self, force: np.ndarray, dt: float = 1.0):
        # update velocity and position based on combined force
        self.velocity += force * dt
        speed = np.linalg.norm(self.velocity)
        if speed > self.max_speed:
            self.velocity = (self.velocity / speed) * self.max_speed
        self.position += self.velocity * dt

    def check_arrival(self, destination) -> None:
        # mark the agent as arrived if it has reached the destination zone
        if destination.contains(self.position):
            self.status = "arrived"