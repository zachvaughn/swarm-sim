from __future__ import annotations
import numpy as np
import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent import Agent

class HazardZone:
    def __init__(self, center: np.ndarray, radius: float, removal_prob: float):
        self.center = center # center position of the hazard zone as a 2D numpy array
        self.radius = radius # radius of the hazard zone
        self.removal_prob = removal_prob  # probability of an agent being removed when inside the zone

    def contains(self, pos: np.ndarray) -> bool:
        # check if a given position is within the hazard zone
        return np.linalg.norm(pos - self.center) <= self.radius

    def evaluate(self, agent: Agent) -> bool:
        # if the agent is inside the zone, run a Bernoulli trial
        # returns True if the agent should be removed, False otherwise
        if self.contains(agent.position):
            return random.random() < self.removal_prob
        return False