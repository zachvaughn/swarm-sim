import json
import numpy as np
from datetime import datetime
from pathlib import Path

from agent import Agent
from environment import Environment
from datalogger import DataLogger
from zone import Zone
from obstacle import Obstacle
from hazardzone import HazardZone

class SimulationController:
    def __init__(self):
        self.config: dict = {} # load configuration parameters
        self.agents: list[Agent] = [] # list of all agents in the simulation
        self.environment: Environment = None # the simulation environment
        self.logger: DataLogger = None # handles metric logging and export
        self.timestep: int = 0 # current simulation timestep
        self.output_path: Path = None

    def load_config(self, path: str) -> None:
        # load simulation parameters from the JSON config file
        with open(path, "r") as f:
            self.config = json.load(f)

    def initialize(self) -> None:
        # build the environment and spawn agents based on the loaded config
        destination = Zone(
            center=np.array(self.config["destination"]["center"], dtype=float),
            radius=self.config["destination"]["radius"]
        )
        self.environment = Environment(
            width=self.config["environment"]["width"],
            height=self.config["environment"]["height"],
            destination=destination
        )

        for obs in self.config["obstacles"]:
            self.environment.obstacles.append(
                Obstacle(position=np.array(obs["position"], dtype=float), size=obs["size"])
            )

        for hz in self.config["hazard_zones"]:
            self.environment.hazard_zones.append(
                HazardZone(
                    center=np.array(hz["center"], dtype=float),
                    radius=hz["radius"],
                    removal_prob=hz["removal_prob"]
                )
            )

        for i in range(self.config["swarm_size"]):
            spawn_pos = np.array(self.config["spawn_area"]["center"], dtype=float) + \
                        np.random.uniform(-1, 1, size=2) * self.config["spawn_area"]["radius"]
            agent = Agent(
                agent_id=i,
                position=spawn_pos,
                velocity=np.zeros(2),
                perception_radius=self.config["perception_radius"],
                max_speed=self.config["max_speed"]
            )
            self.agents.append(agent)

        self.logger = DataLogger(run_id=self._get_next_run_id())
        self.timestep = 0

        output_dir = Path("../outputs")
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.output_path = output_dir / f"output_{timestamp}.csv"

    def step(self) -> None:
        # advance the simulation by one timestep
        for agent in self.agents:
            if agent.status != "active":
                continue

            neighbors_data = agent.get_neighbor_data(self.agents)
            flock_force = agent.compute_flocking(
                neighbors_data,
                w_sep=self.config["weights"]["separation"],
                w_align=self.config["weights"]["alignment"],
                w_coh=self.config["weights"]["cohesion"]
            )
            field_force = agent.compute_potential_field(self.environment)
            total_force = flock_force + field_force

            agent.update(total_force)
            agent.check_arrival(self.environment.destination)

            for hz in self.environment.get_hazard_zones_at(agent.position):
                if hz.evaluate(agent):
                    agent.status = "removed"
                    break

        self.logger.log_step(self.timestep, self.agents)

        # print a progress update every 10 timesteps
        if self.timestep % 10 == 0:
            active = sum(1 for a in self.agents if a.status == "active")
            arrived = sum(1 for a in self.agents if a.status == "arrived")
            removed = sum(1 for a in self.agents if a.status == "removed")
            print(f"Timestep {self.timestep}: active={active}, arrived={arrived}, removed={removed}")

        self.timestep += 1

    def _get_next_run_id(self) -> int:
        # read the last used run id from a counter file, increment it, and save it back
        counter_path = Path("../run_counter.txt")
        if counter_path.exists():
            last_id = int(counter_path.read_text().strip())
        else:
            last_id = 0

        next_id = last_id + 1
        counter_path.write_text(str(next_id))
        return next_id

    def run(self) -> None:
        # run the simulation until completion
        while not self.is_done():
            self.step()
        self.logger.export_csv(self.output_path)

    def is_done(self) -> bool:
        # simulation ends when all agents are no longer active, or max steps reached
        all_inactive = all(a.status != "active" for a in self.agents)
        max_steps_reached = self.timestep >= self.config.get("max_steps", 1000)
        return all_inactive or max_steps_reached