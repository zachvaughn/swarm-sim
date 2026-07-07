import csv
import json
import numpy as np
from pathlib import Path

class DataLogger:
    def __init__(self, run_id: int):
        self.records: list[dict] = [] # list of metric records, one per discrete time-step
        self.run_id = run_id # identifier per simulation run
        self.prev_centroid = None # tracks previous timestep's centroid velocity calculation

    def log_step(self, timestep: int, agents: list, environment=None) -> None:
        # record metrics for the current time-step
        active_count = sum(1 for a in agents if a.status == "active")
        arrived_count = sum(1 for a in agents if a.status == "arrived")
        removed_count = sum(1 for a in agents if a.status == "removed")

        centroid_velocity = self._compute_centroid_velocity(agents)
        hazard_encounters = self._compute_hazard_encounters(agents, environment) if environment else 0

        record = {
            "run_id": self.run_id,
            "timestep": timestep,
            "active_count": active_count,
            "arrived_count": arrived_count,
            "removed_count": removed_count,
            "cohesion": self.compute_cohesion(agents),
            "coverage": self.compute_coverage(agents),
            "centroid_velocity": centroid_velocity,
            "hazard_encounters": hazard_encounters,
        }
        self.records.append(record)

    def compute_cohesion(self, agents: list) -> float:
        # average pair distance between all active agents
        active_agents = [a for a in agents if a.status == "active"]
        if len(active_agents) < 2:
            return 0.0

        total_distance = 0.0
        pair_count = 0
        for i in range(len(active_agents)):
            for j in range(i + 1, len(active_agents)):
                dist = np.linalg.norm(active_agents[i].position - active_agents[j].position)
                total_distance += dist
                pair_count += 1

        return total_distance / pair_count if pair_count > 0 else 0.0

    def compute_coverage(self, agents: list) -> float:
        # area of the bounding box containing all active agents
        active_agents = [a for a in agents if a.status == "active"]
        if not active_agents:
            return 0.0

        xs = [a.position[0] for a in active_agents]
        ys = [a.position[1] for a in active_agents]
        width = max(xs) - min(xs)
        height = max(ys) - min(ys)
        return width * height

    def _compute_centroid_velocity(self, agents: list) -> float:
        # speed of the swarm's center of mass between this timestep and the last
        active_agents = [a for a in agents if a.status == "active"]
        if not active_agents:
            return 0.0

        centroid = np.mean([a.position for a in active_agents], axis=0)

        if self.prev_centroid is None:
            self.prev_centroid = centroid
            return 0.0

        velocity = np.linalg.norm(centroid - self.prev_centroid)
        self.prev_centroid = centroid
        return velocity

    def _compute_hazard_encounters(self, agents: list, environment) -> int:
        # count how many active agents are currently inside any hazard zone
        active_agents = [a for a in agents if a.status == "active"]
        count = 0
        for agent in active_agents:
            if environment.get_hazard_zones_at(agent.position):
                count += 1
        return count

    def export_csv(self, path):
        # write all recorded metrics to a CSV file
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.records[0].keys())
            writer.writeheader()
            writer.writerows(self.records)

    def export_summary(self, path, execution_time: float, config: dict, final_counts: dict) -> None:
        # write a summary JSON file with run metadata and results
        summary = {
            "run_id": self.run_id,
            "execution_time_seconds": round(execution_time, 3),
            "seed": config.get("seed"),
            "swarm_size": config.get("swarm_size"),
            "max_steps": config.get("max_steps"),
            "total_timesteps": self.records[-1]["timestep"] if self.records else 0,
            "final_active": final_counts.get("active", 0),
            "final_arrived": final_counts.get("arrived", 0),
            "final_removed": final_counts.get("removed", 0),
            "avg_cohesion": sum(r["cohesion"] for r in self.records) / len(self.records) if self.records else 0.0,
            "avg_coverage": sum(r["coverage"] for r in self.records) / len(self.records) if self.records else 0.0,
            "avg_centroid_velocity": sum(r["centroid_velocity"] for r in self.records) / len(self.records) if self.records else 0.0,
            "total_hazard_encounters": sum(r["hazard_encounters"] for r in self.records) if self.records else 0,
        }

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(summary, f, indent=2)