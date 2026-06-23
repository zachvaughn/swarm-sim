import os
from simulationcontroller import SimulationController


def main():
    # path to the config file at the project root
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")

    controller = SimulationController()
    controller.load_config(config_path)
    controller.initialize()
    controller.run()

    arrived = sum(1 for a in controller.agents if a.status == "arrived")
    removed = sum(1 for a in controller.agents if a.status == "removed")
    active = sum(1 for a in controller.agents if a.status == "active")

    print(f"Simulation finished after {controller.timestep} timesteps.")
    print(f"Arrived: {arrived} | Removed: {removed} | Still active: {active}")
    print(f"Results exported to {controller.output_path}")


if __name__ == "__main__":
    main()