# Multi-Agent Swarm Simulation for Autonomous Coordination

## Overview
A discrete-time, agent-based simulation modeling autonomous swarm coordination. 
Agents navigate a 2D environment toward a destination while avoiding obstacles 
and hazard zones.

### Features
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
- Configurable potential field weights (k_att, k_rep, rho_0) via baseline.json (or any configuration file preset)
- Random seed support for reproducible runs
- Agent position clamping to environment bounds
- Extra data collection (centroid velocity, hazard encounters)
- Parameter testing across multiple configurations

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
 
This loads parameters from the baseline configuration in `configs/`, runs the
simulation until all agents have arrived, been removed, or the max step
count is reached, then exports results to a CSV file.

### Configuration
All simulation parameters are set via JSON config files located in `configs/`. 
The `baseline` scenario runs by default as shown above, but any scenario can be selected by 
passing its name as a command-line argument:

    python src/main.py baseline
    python src/main.py high_swarm_size
    python src/main.py high_hazard
    python src/main.py tight_perception
    python src/main.py low_speed
    python src/main.py high_separation
    python src/main.py high_cohesion
    python src/main.py dense_obstacles
    python src/main.py combined_stress
    python src/main.py no_hazards

Each config includes:
- Swarm size and spawn area
- Perception radius and max speed
- Flocking weight constants (separation, alignment, cohesion)
- Potential field weights (attraction, repulsion, influence radius)
- Obstacle and hazard zone placement
- Max simulation steps and random seed

### Expected Output and Screenshot
Console output reporting the number of timesteps run and final agent status
counts (arrived, removed, still active), followed by a CSV file containing
per-timestep metrics. An example output can be found below (all outputs (CSV/JSON) are sent to the `outputs/` folder):
 
    Timestep 0: active=50, arrived=0, removed=0
    Timestep 10: active=50, arrived=0, removed=0
    Timestep 20: active=48, arrived=0, removed=2
    Timestep 30: active=47, arrived=0, removed=3
    Timestep 40: active=47, arrived=0, removed=3
    Timestep 50: active=47, arrived=0, removed=3
    Timestep 60: active=47, arrived=0, removed=3
    Timestep 70: active=47, arrived=0, removed=3
    Timestep 80: active=47, arrived=0, removed=3
    Timestep 90: active=47, arrived=0, removed=3
    Timestep 100: active=46, arrived=0, removed=4
    Timestep 110: active=46, arrived=0, removed=4
    Timestep 120: active=42, arrived=0, removed=8
    Timestep 130: active=42, arrived=0, removed=8
    Timestep 140: active=42, arrived=0, removed=8
    Timestep 150: active=40, arrived=0, removed=10
    Timestep 160: active=37, arrived=0, removed=13
    Timestep 170: active=37, arrived=0, removed=13
    Timestep 180: active=37, arrived=0, removed=13
    Timestep 190: active=35, arrived=0, removed=15
    Timestep 200: active=34, arrived=1, removed=15
    Timestep 210: active=33, arrived=2, removed=15
    Timestep 220: active=33, arrived=2, removed=15
    Timestep 230: active=33, arrived=2, removed=15
    Timestep 240: active=31, arrived=2, removed=17
    Timestep 250: active=31, arrived=2, removed=17
    Timestep 260: active=30, arrived=2, removed=18
    Timestep 270: active=29, arrived=2, removed=19
    Timestep 280: active=27, arrived=4, removed=19
    Timestep 290: active=24, arrived=7, removed=19
    Timestep 300: active=23, arrived=8, removed=19
    Timestep 310: active=21, arrived=10, removed=19
    Timestep 320: active=21, arrived=10, removed=19
    Timestep 330: active=21, arrived=10, removed=19
    Timestep 340: active=21, arrived=10, removed=19
    Timestep 350: active=21, arrived=10, removed=19
    Timestep 360: active=17, arrived=14, removed=19
    Timestep 370: active=1, arrived=30, removed=19
    Simulation finished after 376 timesteps.
    Execution time: 13.06 seconds
    Arrived: 31 | Removed: 19 | Still active: 0
    Results exported to output_2026-07-08_15-37-09.csv
    Summary exported to output_2026-07-08_15-37-09_summary.json

Visualization at timestep ~60:
<img width="912" height="744" alt="timestep 60" src="https://github.com/user-attachments/assets/add00715-3005-4869-bbae-1a9e5a1a5e10" />

## Architecture Overview
- **`SimulationController`** — owns the environment, agent list, and logger;
  runs the main simulation loop and checks for config validation
- **`Agent`** — represents an individual swarm member; computes flocking and
  potential field forces at each timestep
- **`Environment`** — holds obstacles, hazard zones, and the destination;
  provides spatial queries for agents
- **`Zone`** / **`Obstacle`** / **`HazardZone`** — environment
  objects
- **`DataLogger`** — tracks and exports simulation metrics
- **`Renderer`** -- renders pygame visualization window
