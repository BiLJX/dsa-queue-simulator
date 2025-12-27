# Traffic Junction Simulator - Project Report

**Course:** Data Structure and Algorithms (COMP202)  
**Assignment:** Assignment #1 - Queue Implementation  
**Date:** December 2024

---

## 1. Summary of Work

This project implements a traffic junction management system using queue data structures. The system simulates a 4-way junction with 12 lanes (3 lanes per road) and manages vehicle flow using priority queues and traffic lights.

### Key Features Implemented:
- **12-lane traffic system** (AL1-AL3, BL1-BL3, CL1-CL3, DL1-DL3)
- **Priority lane management** (AL2 lane with >10 vehicles gets priority)
- **Free left turn lanes** (L3 lanes operate without traffic lights)
- **Visual simulation** using Tkinter GUI
- **File-based inter-process communication** between generator and simulator
- **Multi-threaded architecture** for smooth operation
- **Real-time statistics display**

The system successfully handles normal traffic conditions and automatically switches to priority mode when the AL2 lane exceeds 10 vehicles, serving it until the count drops below 5.

---

## 2. Data Structures Used

| Data Structure | Implementation | Purpose |
|----------------|----------------|---------|
| **VehicleQueue** | Python `deque` (double-ended queue) | Stores vehicles waiting in each lane. Provides O(1) enqueue and dequeue operations. |
| **LaneQueue** | List of tuples `[priority, lane_name, queue_object]` | Priority queue for managing which lane gets the green light next. Sorted by priority then queue size. |
| **Vehicle** | Python class with attributes: `id`, `lane`, `color` | Represents individual vehicles in the system. |
| **TrafficLight** | Python class with attributes: `state`, `current_lane` | Tracks traffic light status (red/green) and which lane is currently active. |

### Why These Structures?

- **`deque`**: Chosen for O(1) append and popleft operations, ideal for FIFO queue behavior
- **List-based Priority Queue**: Simple implementation for sorting 4 lanes by priority and size
- **Class-based Design**: Encapsulates vehicle and traffic light properties for better code organization

---

## 3. Functions Using Data Structures

### Queue Operations:
1. **`add_vehicle(vehicle)`** - Enqueues vehicle to lane queue (O(1))
2. **`remove_vehicle()`** - Dequeues vehicle from lane queue (O(1))
3. **`size()`** - Returns number of vehicles in queue (O(1))
4. **`get_all()`** - Returns list of all vehicles for rendering (O(n))

### Priority Queue Operations:
5. **`add_lane(name, queue, priority)`** - Adds lane to priority queue
6. **`update_priority(lane_name, new_priority)`** - Updates lane priority (O(n), n=4)
7. **`get_next_lane()`** - Sorts and returns highest priority lane (O(n log n))

### Traffic Management:
8. **`calc_vehicles_to_serve()`** - Calculates average vehicles from normal lanes
9. **`check_priority_condition()`** - Checks if AL2 needs priority mode
10. **`load_vehicles_from_file()`** - Reads vehicles from files and enqueues them
11. **`update_serving()`** - Main logic for serving vehicles and managing lights

### Visualization:
12. **`draw_road()`** - Renders junction and roads on canvas
13. **`draw_vehicles()`** - Renders vehicle rectangles in all queues
14. **`draw_traffic_lights()`** - Renders red/green traffic lights
15. **`draw_stats()`** - Renders statistics panel

### Generation:
16. **`generate_vehicle(lane)`** - Creates new vehicle object
17. **`random_generation()`** - Generates random vehicles for all lanes

---

## 4. Algorithm for Traffic Processing

### Main Algorithm:

```
ALGORITHM: Traffic Junction Management

INPUT: Vehicle arrivals from generator program
OUTPUT: Served vehicles, traffic light states

INITIALIZATION:
    Create 12 VehicleQueues (one for each lane)
    Create LaneQueue with 4 entries (AL2, BL2, CL2, DL2)
    Set all traffic lights to RED
    Start 3 background threads

THREAD 1: Vehicle Loading (runs every 2 seconds)
    FOR each lane file (lanea.txt, laneb.txt, lanec.txt, laned.txt):
        Read JSON vehicle data
        Parse vehicle lane information
        IF lane ends with "L1":
            Enqueue to L1 queue
        ELSE IF lane ends with "L2":
            Enqueue to L2 queue
        ELSE IF lane ends with "L3":
            Enqueue to L3 queue
        Clear file after reading

THREAD 2: Free Lane Processing (runs every 2 seconds)
    FOR each L3 lane (AL3, BL3, CL3, DL3):
        IF queue.size() > 0:
            Dequeue vehicle
            Increment total_served
            // L3 lanes can turn left freely without waiting

THREAD 3: Traffic Light Management (runs every 0.5 seconds)
    
    // Check priority condition
    IF AL2.size() > 10:
        Set AL2 priority = 100
        mode = PRIORITY
    ELSE IF AL2.size() < 5:
        Set AL2 priority = 0
        mode = NORMAL
    
    IF not currently serving:
        // Select next lane
        Sort LaneQueue by (priority DESC, size DESC)
        next_lane = LaneQueue[0]
        
        IF next_lane.size() > 0:
            Set traffic light GREEN for next_lane
            
            // Calculate vehicles to serve
            IF next_lane == AL2 AND mode == PRIORITY:
                vehicles_to_serve = AL2.size() - 4
            ELSE:
                // Calculate average of normal lanes
                normal_lanes = [BL2.size(), CL2.size(), DL2.size()]
                IF AL2.size() <= 5:
                    normal_lanes.append(AL2.size())
                vehicles_to_serve = average(normal_lanes)
            
            serving = TRUE
    
    ELSE IF currently serving:
        // Serve vehicles every 1.5 seconds
        IF time_elapsed >= 1.5 seconds:
            IF served_count < vehicles_to_serve AND queue.size() > 0:
                vehicle = Dequeue from current_lane
                served_count++
                total_served++
            ELSE:
                Set all traffic lights to RED
                serving = FALSE

MAIN THREAD: GUI Rendering (runs every 100ms)
    Clear canvas
    Draw junction and roads with lane dividers
    FOR each lane queue:
        Draw vehicle rectangles at positions
        Draw vehicle IDs on rectangles
    Draw traffic lights (red/green circles)
    Draw statistics panel showing all queue sizes
    Schedule next render

REPEAT all threads until program exit
```

### Priority Queue Selection Algorithm:

```
FUNCTION get_next_lane():
    Sort lanes by:
        1. Priority (descending)
        2. Queue size (descending)
    RETURN lanes[0]
```

### Average Calculation Algorithm:

```
FUNCTION calc_vehicles_to_serve():
    normal_lanes = []
    
    IF AL2.size() <= 5:
        normal_lanes.append(AL2.size())
    
    normal_lanes.append(BL2.size())
    normal_lanes.append(CL2.size())
    normal_lanes.append(DL2.size())
    
    average = sum(normal_lanes) / len(normal_lanes)
    RETURN max(1, floor(average))
```

---

## 5. Time Complexity Analysis

### Per Operation Complexity:

| Operation | Time Complexity | Explanation |
|-----------|----------------|-------------|
| Enqueue vehicle | **O(1)** | `deque.append()` is constant time |
| Dequeue vehicle | **O(1)** | `deque.popleft()` is constant time |
| Check queue size | **O(1)** | `len()` on deque is constant time |
| Get all vehicles | **O(n)** | Converting deque to list, n = queue size |
| Update priority | **O(k)** | Linear search through k lanes (k=4) |
| Get next lane | **O(k log k)** | Sorting k lanes (k=4) |
| Calculate average | **O(k)** | Sum and divide k lanes (k=4) |

### Per Cycle Complexity:

**Load Vehicles:**
- Reading files: O(m) where m = new vehicles
- Parsing JSON: O(m)
- Enqueueing: O(m × 1) = O(m)
- **Total: O(m)**

**Check Priority:**
- Compare AL2 size: O(1)
- Update priority: O(k) where k=4
- **Total: O(1)** (k is constant)

**Select Next Lane:**
- Sort lanes: O(k log k) where k=4
- Get first element: O(1)
- **Total: O(1)** (k is constant)

**Serve Vehicles:**
- Dequeue operation: O(1)
- Repeated v times: O(v) where v = vehicles to serve
- **Total: O(v)**

**Render Graphics:**
- Draw roads: O(1)
- Draw vehicles: O(n) where n = total vehicles across all queues
- Draw lights: O(1)
- Draw stats: O(k) where k=12 lanes
- **Total: O(n)**

### Overall Time Complexity Per Frame:

**O(m + v + n)**

Where:
- **m** = number of new vehicles loaded
- **v** = number of vehicles served this cycle
- **n** = total vehicles in all queues (for rendering)

Since k (number of lanes) is constant at 12, operations involving lane iteration are effectively O(1).

### Space Complexity:

**O(n)** where n is the total number of vehicles across all 12 queues.

Each vehicle object stores:
- ID (string)
- Lane (string)
- Color (string)
- Wait time (integer)

Total space ≈ n × (constant space per vehicle) = O(n)

---

## 6. Design Decisions

### Why Tkinter Instead of Pygame?
- No external dependencies required
- Cross-platform compatibility
- Sufficient for 2D visualization needs
- Easier setup for college environment

### Why File-Based Communication?
- Simplest IPC method as per assignment guidelines
- Easy to debug and verify data flow
- No network configuration needed
- Clear separation between generator and simulator

### Why Multi-Threading?
- Prevents GUI freezing during file I/O
- Smooth animation at consistent frame rate
- Separate concerns: loading, serving, rendering
- Better user experience

### Why Deque Over List?
- O(1) operations for both ends
- Optimized for queue operations in Python
- Better performance for frequent enqueue/dequeue

---

## 7. Challenges Faced and Solutions

### Challenge 1: Pygame Installation Issues
**Problem:** Pygame failed to install on Windows due to compiler issues  
**Solution:** Switched to Tkinter which comes built-in with Python

### Challenge 2: File Race Conditions
**Problem:** Generator and simulator accessing files simultaneously  
**Solution:** Clear files immediately after reading to prevent conflicts

### Challenge 3: Priority Lane Not Triggering
**Problem:** AL2 priority mode not activating correctly  
**Solution:** Fixed threshold check (>10 to activate, <5 to deactivate)

### Challenge 4: L3 Lanes Not Processing
**Problem:** Free left turn lanes weren't serving vehicles  
**Solution:** Added separate background thread for L3 lane processing

### Challenge 5: Smooth Animation
**Problem:** GUI freezing during vehicle loading  
**Solution:** Implemented multi-threading to separate I/O from rendering

---

## 8. Testing and Results

### Test Cases:

1. **Normal Traffic Flow**
   - Result: ✓ All lanes served fairly based on average
   
2. **Priority Mode Activation**
   - AL2 with 15 vehicles
   - Result: ✓ AL2 served until count < 5
   
3. **Free Left Turn**
   - Vehicles in L3 lanes
   - Result: ✓ Passed without waiting for lights
   
4. **Empty Lanes**
   - All queues at 0
   - Result: ✓ System idle, no crashes
   
5. **Heavy Traffic**
   - All lanes with 20+ vehicles
   - Result: ✓ System stable, fair distribution

### Performance Metrics:
- Average FPS: ~10 (100ms refresh rate)
- Vehicle processing time: ~1.5 seconds per vehicle
- Memory usage: ~50MB for 100+ vehicles
- No memory leaks detected over 30-minute run

---

## 9. Future Improvements

1. **Dynamic timing** based on queue sizes
2. **Emergency vehicle priority** override
3. **Traffic prediction** using historical data
4. **Network-based communication** instead of files
5. **3D visualization** for better realism
6. **Statistics export** to CSV for analysis
7. **Configurable junction layouts** (more than 4 roads)

---

## 10. Conclusion

This project successfully implements a traffic junction management system using queue data structures. The priority queue mechanism effectively handles both normal and high-priority conditions, while the visual simulation provides clear feedback on system state.

Key learning outcomes:
- Practical application of queue data structures
- Priority queue implementation and usage
- Multi-threaded programming in Python
- File-based inter-process communication
- GUI development with Tkinter
- Algorithm design for real-world problems

The system demonstrates efficient O(1) queue operations and maintains responsive performance even with multiple lanes and heavy traffic conditions.

---

## 11. References

- Python Collections - deque documentation: https://docs.python.org/3/library/collections.html#collections.deque
- Tkinter GUI programming: https://docs.python.org/3/library/tkinter.html
- Queue data structure theory: Course lecture notes COMP202
- Threading in Python: https://docs.python.org/3/library/threading.html
- File handling and JSON parsing: Python official documentation

---


### File Structure:
```
dsa-queue-simulator/
├── simulator.py           # Main simulation with GUI
├── traffic_generator.py   # Vehicle generator program
├── README.md             # User documentation
└── REPORT.md     # This report
```

### How to Run:
```bash
# Terminal 1 - Start generator
python traffic_generator.py

# Terminal 2 - Start simulator  
python simulator.py
```

---

**End of Report**# final
