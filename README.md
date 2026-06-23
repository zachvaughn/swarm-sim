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
- CSV export of  metrics
- Verified that agents successfully navigate to destination

### Still to come
- Pygame visualization of the simulation running in real time
- Extra data collection (centroid velocity, hazard encounters)
- Parameter testing across multiple configurations (currently testing)
- Statistical analysis and validation

### Changes from original project foundation
- CSV export currently uses Python's built-in `csv` module instead of `pandas` 
  as it works fine for this project. `pandas` may still be used later on.
- `Environment.get_nearest_obstacle()` returns a tuple `(distance, obstacle)` 
  instead of just a float as referenced in the UML Diagram, since the agent's potential field calculation needs 
  a reference to the obstacle itself to compute repulsion direction.

## Installation
### Dependencies
- Python 3.14.5
- numpy
- pygame (planned for visualization)

### Setup
**1. Clone the repository in your IDE**
 
    git clone https://github.com/zachvaughn/swarm-sim.git
    cd swarm-sim
 
**2. Create a virtual environment**
 
    python -m venv .venv
    source .venv/bin/activate
 
**3. Install dependencies**
 
    pip install -r requirements.txt

## Usage
Run the simulation from the `src/` directory:
 
    python main.py
 
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

### Expected Output
Console output reporting the number of timesteps run and final agent status
counts (arrived, removed, still active), followed by a CSV file containing
per-timestep metrics. An example output can be found below:
 
    Timestep 0: active=20, arrived=0, removed=0
    Timestep 10: active=20, arrived=0, removed=0
    Timestep 20: active=20, arrived=0, removed=0
    Timestep 30: active=20, arrived=0, removed=0
    Timestep 40: active=20, arrived=0, removed=0
    Timestep 50: active=20, arrived=0, removed=0
    Timestep 60: active=20, arrived=0, removed=0
    Timestep 70: active=20, arrived=0, removed=0
    Timestep 80: active=20, arrived=0, removed=0
    Timestep 90: active=20, arrived=0, removed=0
    Timestep 100: active=20, arrived=0, removed=0
    Timestep 110: active=18, arrived=0, removed=2
    Timestep 120: active=18, arrived=0, removed=2
    Timestep 130: active=13, arrived=4, removed=3
    Timestep 140: active=2, arrived=15, removed=3
    Timestep 150: active=1, arrived=16, removed=3
    Simulation finished after 159 timesteps.
    Arrived: 17 | Removed: 3 | Still active: 0
    Results exported to ../outputs/output_2026-06-23_06-50-23.csv

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
