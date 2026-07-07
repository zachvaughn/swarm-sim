# Multi-Agent Swarm Simulation for Autonomous Coordination

## Overview
A discrete-time, agent-based simulation modeling autonomous swarm coordination. 
Agents navigate a 2D environment toward a destination while avoiding obstacles 
and hazard zones.

### Implemented so far
- `Zone`, `Obstacle`, and `HazardZone` classes
- `Agent` class with Reynolds' flocking rules (separation, alignment, cohesion)
- `Agent` class with artificial potential field navigation (attraction/repulsion)
- Probabilistic hazard zone evaluation (Bernoulli-based trial)
- `Environment` class with obstacle and hazard zone queries
- `DataLogger` class with cohesion, coverage, and status tracking
- `SimulationController` tying together the full simulation loop
- JSON-based configuration system
- CSV export of metrics
- Verified that agents successfully navigate to destination
- `Renderer` class for real-time pygame visualization
- Multi-obstacle repulsion in potential field calculation
- Configurable potential field weights (k_att, k_rep, rho_0) via config.json
- Random seed support for reproducible runs
- Agent position clamping to environment bounds
- Extra data collection (centroid velocity, hazard encounters)
- Parameter testing across multiple configurations

### Still to come
- Statistical analysis and validation

### Changes from original project foundation
- CSV export currently uses Python's built-in `csv` module instead of `pandas` 
  as it works fine for this project. `pandas` may still be used later on.
- `Environment.get_nearest_obstacle()` returns a tuple `(distance, obstacle)` 
  instead of just a float as referenced in the UML Diagram, since the agent's potential field calculation needs 
  a reference to the obstacle itself to compute repulsion direction.
- Added a `Renderer` class (not in the original UML) to separate visualization 
  logic from simulation logic.
- `Environment.get_obstacles_within()` was added to support summing repulsion 
  across all nearby obstacles, rather than only the single nearest one.
- Added a `seed` field to `config.json` and random number generation 
  onto  `np.random.Generator` so simulation runs are reproducible.

## Installation
### Dependencies
- Python 3.14.5
- numpy
- pygame

### Setup
**1. Clone the repository in your IDE**
 
    git clone https://github.com/zachvaughn/swarm-sim.git
    cd swarm-sim
 
**2. Create a virtual environment**

macOS / Linux:
 
    python -m venv .venv
    source .venv/bin/activate

Windows (PowerShell):

    python -m venv .venv
    .venv\Scripts\Activate.ps1
 
**3. Install dependencies**
 
    pip install -r requirements.txt

## Usage
To run the simulation, open the project directly once it has been cloned and run `main.py` from the `src` directory, or run it via terminal:

    python src/main.py

This runs the `baseline` configuration by default. You can also run one of the other named scenarios in the `configs/` folder by passing its name as an argument:

    python src/main.py high_swarm_size
    python src/main.py high_hazard
    python src/main.py tight_perception
 
This loads parameters from `config.json` at the project root, runs the
simulation until all agents have arrived, been removed, or the max step
count is reached, then exports results to a CSV file.

### Configuration
All simulation parameters are set in `config.json`, including:
- Swarm size and spawn area
- Perception radius and max speed
- Flocking weight constants (separation, alignment, cohesion)
- Obstacle and hazard zone placement
- Max simulation steps and output file path

### Expected Output and Screenshot
Console output reporting the number of timesteps run and final agent status
counts (arrived, removed, still active), followed by a CSV file containing
per-timestep metrics. An example output can be found below:
 
    Timestep 0: active=20, arrived=0, removed=0
    Timestep 10: active=20, arrived=0, removed=0
    Timestep 20: active=20, arrived=0, removed=0
    Timestep 30: active=20, arrived=0, removed=0
    Timestep 40: active=20, arrived=0, removed=0
    Timestep 50: active=19, arrived=0, removed=1
    Timestep 60: active=17, arrived=0, removed=3
    Timestep 70: active=16, arrived=0, removed=4
    Timestep 80: active=13, arrived=0, removed=7
    Timestep 90: active=12, arrived=0, removed=8
    Timestep 100: active=11, arrived=0, removed=9
    Timestep 110: active=11, arrived=0, removed=9
    Timestep 120: active=7, arrived=4, removed=9
    Timestep 130: active=7, arrived=4, removed=9
    Timestep 140: active=7, arrived=4, removed=9
    Timestep 150: active=2, arrived=9, removed=9
    Simulation finished after 155 timesteps.
    Arrived: 11 | Removed: 9 | Still active: 0
    Results exported to outputs/output_2026-07-07_19-00-26.csv

At Timestep ~50:
<img width="912" height="744" alt="timestep 50" src="https://github.com/user-attachments/assets/e564187f-3e4c-4e94-9feb-1ff0c5512d14" />

At Timestep ~140
<img width="912" height="744" alt="timestep 140" src="https://github.com/user-attachments/assets/83d862c8-373c-451a-ad65-6ead6d776430" />



## Architecture Overview
- **`SimulationController`** — owns the environment, agent list, and logger;
  runs the main simulation loop
- **`Agent`** — represents an individual swarm member; computes flocking and
  potential field forces at each timestep
- **`Environment`** — holds obstacles, hazard zones, and the destination;
  provides spatial queries for agents
- **`Zone`** / **`Obstacle`** / **`HazardZone`** — environment
  objects
- **`DataLogger`** — tracks and exports simulation metrics
