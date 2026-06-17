import numpy as np


class Zone:
    def __init__(self, center: np.ndarray, radius: float):
        self.center = center  # center position of the zone as a 2D numpy array
        self.radius = radius  # radius of the zone

    def contains(self, pos: np.ndarray) -> bool:
        # check if position is within the zone
        return np.linalg.norm(pos - self.center) <= self.radius