import os
import sys
from simulationcontroller import SimulationController
from renderer import Renderer

def main():
    if len(sys.argv) > 1:
        config_name = sys.argv[1]
    else:
        config_name = "baseline"

    config_path = os.path.join(os.path.dirname(__file__), "..", "configs", f"{config_name}.json")

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

    execution_time = controller.get_elapsed_time()

    print(f"Simulation finished after {controller.timestep} timesteps.")
    print(f"Execution time: {execution_time:.2f} seconds")
    print(f"Arrived: {arrived} | Removed: {removed} | Still active: {active}")
    print(f"Results exported to {controller.output_path}")

    controller.logger.export_csv(controller.output_path)

    summary_path = str(controller.output_path).replace(".csv", "_summary.json")
    controller.logger.export_summary(
        summary_path,
        execution_time=execution_time,
        config=controller.config,
        final_counts={"active": active, "arrived": arrived, "removed": removed}
    )
    print(f"Summary exported to {summary_path}")

if __name__ == "__main__":
    main()