import json
import random
import time
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
        self.config: dict = {} # load the configuration parameters
        self.agents: list[Agent] = [] # list of all agents in the simulation
        self.environment: Environment = None # the simulation environment
        self.logger: DataLogger = None # handles metric logging and export
        self.timestep: int = 0 # current simulation timestep
        self.output_path: Path = None

    def load_config(self, path: str) -> None:
        # load simulation parameters from the JSON config file
        with open(path, "r") as f:
            self.config = json.load(f)

        self._validate_config()

    def _validate_config(self) -> None:
        # check that required fields exist
        required_fields = [
            "environment", "destination", "spawn_area", "swarm_size",
            "perception_radius", "max_speed", "weights", "potential_field",
            "obstacles", "hazard_zones", "max_steps"
        ]
        missing = [field for field in required_fields if field not in self.config]
        if missing:
            raise ValueError(f"Config file is missing required field(s): {', '.join(missing)}")

        # validate numeric ranges
        if self.config["swarm_size"] <= 0:
            raise ValueError(f"swarm_size must be positive, got {self.config['swarm_size']}")

        if self.config["max_speed"] <= 0:
            raise ValueError(f"max_speed must be positive, got {self.config['max_speed']}")

        if self.config["perception_radius"] <= 0:
            raise ValueError(f"perception_radius must be positive, got {self.config['perception_radius']}")

        if self.config["max_steps"] <= 0:
            raise ValueError(f"max_steps must be positive, got {self.config['max_steps']}")

        # validate environment bounds
        env = self.config["environment"]
        if env["width"] <= 0 or env["height"] <= 0:
            raise ValueError(f"environment width/height must be positive, got {env['width']}x{env['height']}")

        # validate destination and spawn area are within bounds
        dest = self.config["destination"]
        if not (0 <= dest["center"][0] <= env["width"] and 0 <= dest["center"][1] <= env["height"]):
            raise ValueError(f"destination center {dest['center']} is outside environment bounds")

        # validate hazard zone probabilities
        for hz in self.config["hazard_zones"]:
            if not (0 <= hz["removal_prob"] <= 1):
                raise ValueError(f"hazard zone removal_prob must be between 0 and 1, got {hz['removal_prob']}")

        # validate flocking weights are non-negative
        for key, value in self.config["weights"].items():
            if value < 0:
                raise ValueError(f"weight '{key}' must be non-negative, got {value}")

    def initialize(self) -> None:
        self.start_time = time.perf_counter()

        # set up RNG
        seed = self.config.get("seed")
        self.rng = np.random.default_rng(seed)
        random.seed(seed)

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
                        self.rng.uniform(-1, 1, size=2) * self.config["spawn_area"]["radius"]
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

        project_root = Path(__file__).resolve().parent.parent
        output_dir = project_root / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.output_path = output_dir / f"output_{timestamp}.csv"

    def get_elapsed_time(self) -> float:
        # returns elapsed time in seconds
        return time.perf_counter() - self.start_time

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
            field_force = agent.compute_potential_field(
                self.environment,
                k_att=self.config["potential_field"]["k_att"],
                k_rep=self.config["potential_field"]["k_rep"],
                rho_0=self.config["potential_field"]["rho_0"]
            )
            total_force = flock_force + field_force

            agent.update(total_force, self.environment)
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
        project_root = Path(__file__).resolve().parent.parent
        counter_path = project_root / "run_counter.txt"
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