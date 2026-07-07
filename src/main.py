import os
from simulationcontroller import SimulationController
from renderer import Renderer

def main():
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")

    controller = SimulationController()
    controller.load_config(config_path)
    controller.initialize()

    renderer = Renderer(controller.environment.width, controller.environment.height)

    running = True
    while running and not controller.is_done():
        running = renderer.handle_events()
        if not running:
            break

        controller.step()
        renderer.draw(controller.agents, controller.environment)
        renderer.tick(30)

    renderer.quit()

    arrived = sum(1 for a in controller.agents if a.status == "arrived")
    removed = sum(1 for a in controller.agents if a.status == "removed")
    active = sum(1 for a in controller.agents if a.status == "active")

    print(f"Simulation finished after {controller.timestep} timesteps.")
    print(f"Arrived: {arrived} | Removed: {removed} | Still active: {active}")
    print(f"Results exported to {controller.output_path}")

    controller.logger.export_csv(controller.output_path)

if __name__ == "__main__":
    main()