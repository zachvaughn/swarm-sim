import numpy as np


class Obstacle:
    def __init__(self, position: np.ndarray, size: float):
        self.position = position # center position of the obstacle as a 2D numpy array
        self.size = size # radius/size of the obstacle

    def distance_to(self, pos: np.ndarray) -> float:
        # calculate the distance from a given position to the edge of the obstacle
        return np.linalg.norm(pos - self.position) - self.size