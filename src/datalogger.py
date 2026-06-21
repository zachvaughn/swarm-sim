import csv
import numpy as np

class DataLogger:
    def __init__(self, run_id: int):
        self.records: list[dict] = [] # list of metric records, one per discrete time-step
        self.run_id = run_id # identifier per simulation run

    def log_step(self, timestep: int, agents: list) -> None:
        # record metrics for the current time-step
        active_count = sum(1 for a in agents if a.status == "active")
        arrived_count = sum(1 for a in agents if a.status == "arrived")
        removed_count = sum(1 for a in agents if a.status == "removed")

        record = {
            "run_id": self.run_id,
            "timestep": timestep,
            "active_count": active_count,
            "arrived_count": arrived_count,
            "removed_count": removed_count,
            "cohesion": self.compute_cohesion(agents),
            "coverage": self.compute_coverage(agents),
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

    def export_csv(self, path: str) -> None:
        # write all recorded metrics to a CSV file
        if not self.records:
            return

        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.records[0].keys())
            writer.writeheader()
            writer.writerows(self.records)