# Traffic Junction Simulator

A traffic management system using queue data structures. Simulates a 4-way junction with 12 lanes and traffic lights.

## Features

- 12 lanes (3 per road: incoming, main, free left turn)
- Priority lane (AL2) - gets priority when >10 vehicles
- Visual simulation with Tkinter
- Real-time statistics

## How to Run

**Step 1:** Start the vehicle generator
```bash
python traffic_generator.py
```

**Step 2:** Start the simulator (in another terminal)
```bash
python simulator.py
```

**Stop:** Press `Ctrl+C` in generator terminal, close simulator window

## Requirements

- Python 3.x
- No external libraries needed (uses Tkinter)

## Project Structure

```
simulator.py           # Main program with GUI
traffic_generator.py   # Generates random vehicles
README.md             # This file
PROJECT_REPORT.md     # Detailed report
```

## Lane System

Each road (A, B, C, D) has 3 lanes:
- **L1** - Incoming lane
- **L2** - Main lane (needs traffic light)
- **L3** - Free left turn (no light needed)

**AL2 is the priority lane** - when it has more than 10 vehicles, it gets served first.

## Data Structures

- **VehicleQueue** - Uses Python deque for O(1) enqueue/dequeue
- **LaneQueue** - Priority queue for lane management
- **Vehicle** - Stores vehicle id, lane, color
- **TrafficLight** - Tracks light state and active lane

## Algorithm

1. Load vehicles from files every 2 seconds
2. Check if AL2 needs priority (>10 vehicles)
3. Sort lanes by priority and size
4. Serve vehicles from selected lane
5. L3 lanes process freely without lights
6. Repeat

## Screenshots

Run the program to see:
- Colored vehicles queuing in lanes
- Traffic lights turning red/green
- Real-time statistics panel
- Priority mode indicator