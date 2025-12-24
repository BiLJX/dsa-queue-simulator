import tkinter as tk
from tkinter import font
import random
import json
import os
from collections import deque
import threading
import time

# vehicle class
class Vehicle:
    def __init__(self, vid, lane):
        self.id = vid
        self.lane = lane
        self.wait_time = 0
        self.color = random.choice(['red', 'blue', 'green', 'yellow', 'orange', 'purple'])
    
    def to_dict(self):
        return {'id': self.id, 'lane': self.lane}

# queue for vehicles
class VehicleQueue:
    def __init__(self, lane_name):
        self.lane = lane_name
        self.q = deque()
    
    def add_vehicle(self, v):
        self.q.append(v)
    
    def remove_vehicle(self):
        if len(self.q) > 0:
            return self.q.popleft()
        return None
    
    def size(self):
        return len(self.q)
    
    def get_all(self):
        return list(self.q)

# priority queue for lanes
class LaneQueue:
    def __init__(self):
        self.lanes = []
    
    def add_lane(self, lane_name, q, priority=0):
        self.lanes.append([priority, lane_name, q])
    
    def update_priority(self, lane_name, new_priority):
        for lane_data in self.lanes:
            if lane_data[1] == lane_name:
                lane_data[0] = new_priority
                break
    
    def get_next_lane(self):
        # sort by priority then size
        self.lanes.sort(key=lambda x: (-x[0], -x[2].size()))
        if len(self.lanes) > 0:
            return self.lanes[0]
        return None

# traffic light
class TrafficLight:
    def __init__(self):
        self.state = 1  # 1=red, 2=green
        self.current_lane = None
    
    def set_green(self, lane):
        self.state = 2
        self.current_lane = lane
    
    def set_red(self):
        self.state = 1
        self.current_lane = None

class TrafficSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Junction Simulator - 12 Lanes")
        self.root.geometry("1400x900")
        self.root.configure(bg='black')
        
        # canvas for drawing
        self.canvas = tk.Canvas(root, width=1400, height=850, bg='black', highlightthickness=0)
        self.canvas.pack()
        
        # 12 queues - 3 lanes per road (only lane 2 matters for traffic lights)
        # Road A (top)
        self.al1_queue = VehicleQueue("AL1")  # incoming
        self.al2_queue = VehicleQueue("AL2")  # priority lane - needs light
        self.al3_queue = VehicleQueue("AL3")  # free left turn lane
        
        # Road B (left)
        self.bl1_queue = VehicleQueue("BL1")  # incoming
        self.bl2_queue = VehicleQueue("BL2")  # needs light
        self.bl3_queue = VehicleQueue("BL3")  # free left turn
        
        # Road C (bottom)
        self.cl1_queue = VehicleQueue("CL1")  # incoming
        self.cl2_queue = VehicleQueue("CL2")  # needs light
        self.cl3_queue = VehicleQueue("CL3")  # free left turn
        
        # Road D (right)
        self.dl1_queue = VehicleQueue("DL1")  # incoming
        self.dl2_queue = VehicleQueue("DL2")  # needs light
        self.dl3_queue = VehicleQueue("DL3")  # free left turn
        
        # lane priority queue - only for lane 2s that need traffic lights
        self.lane_q = LaneQueue()
        self.lane_q.add_lane("AL2", self.al2_queue, priority=0)  # priority lane
        self.lane_q.add_lane("BL2", self.bl2_queue, priority=0)
        self.lane_q.add_lane("CL2", self.cl2_queue, priority=0)
        self.lane_q.add_lane("DL2", self.dl2_queue, priority=0)
        
        self.lights = TrafficLight()
        self.running = True
        
        # timing stuff
        self.last_load_time = time.time()
        self.last_serve_time = time.time()
        self.serving = False
        self.serve_count = 0
        self.vehicles_to_serve = 0
        self.current_serving_lane = None
        
        self.is_priority_mode = False
        self.total_served = 0
        
        # start background threads
        self.start_background_tasks()
        
        # start drawing loop
        self.draw()
        
    def start_background_tasks(self):
        # thread for loading vehicles
        def load_loop():
            while self.running:
                self.load_vehicles_from_file()
                time.sleep(2)
        
        # thread for serving vehicles
        def serve_loop():
            while self.running:
                self.update_serving()
                time.sleep(0.5)
        
        # thread for free lanes (L3s can go anytime)
        def free_lane_loop():
            while self.running:
                # AL3, BL3, CL3, DL3 can turn left freely without waiting
                for q in [self.al3_queue, self.bl3_queue, self.cl3_queue, self.dl3_queue]:
                    if q.size() > 0:
                        v = q.remove_vehicle()
                        if v:
                            self.total_served += 1
                            print(f"Free left turn: {v.id} from {q.lane}")
                time.sleep(2)
        
        load_thread = threading.Thread(target=load_loop, daemon=True)
        serve_thread = threading.Thread(target=serve_loop, daemon=True)
        free_thread = threading.Thread(target=free_lane_loop, daemon=True)
        
        load_thread.start()
        serve_thread.start()
        free_thread.start()
        
    def load_vehicles_from_file(self):
        # read vehicle data from files
        files = {
            "lanea.txt": [self.al1_queue, self.al2_queue, self.al3_queue],
            "laneb.txt": [self.bl1_queue, self.bl2_queue, self.bl3_queue],
            "lanec.txt": [self.cl1_queue, self.cl2_queue, self.cl3_queue],
            "laned.txt": [self.dl1_queue, self.dl2_queue, self.dl3_queue]
        }
        
        for fname, queues in files.items():
            if os.path.exists(fname):
                try:
                    with open(fname, 'r') as f:
                        lines = f.readlines()
                        for line in lines:
                            line = line.strip()
                            if line:
                                data = json.loads(line)
                                v = Vehicle(data['id'], data['lane'])
                                # distribute to the appropriate lane queue
                                if 'L1' in data['lane']:
                                    queues[0].add_vehicle(v)
                                elif 'L2' in data['lane']:
                                    queues[1].add_vehicle(v)
                                elif 'L3' in data['lane']:
                                    queues[2].add_vehicle(v)
                    # clear file
                    open(fname, 'w').close()
                except:
                    pass
    
    def calc_vehicles_to_serve(self):
        # calculate average based on normal lanes (excluding AL2 if priority)
        normal_lanes = []
        
        al2_size = self.al2_queue.size()
        if al2_size <= 5:
            normal_lanes.append(al2_size)
        
        normal_lanes.append(self.bl2_queue.size())
        normal_lanes.append(self.cl2_queue.size())
        normal_lanes.append(self.dl2_queue.size())
        
        if len(normal_lanes) > 0:
            avg = sum(normal_lanes) / len(normal_lanes)
            return max(1, int(avg))
        return 1
    
    def check_priority_condition(self):
        al2_size = self.al2_queue.size()
        if al2_size > 10:
            self.lane_q.update_priority("AL2", 100)
            self.is_priority_mode = True
            return True
        elif al2_size < 5:
            self.lane_q.update_priority("AL2", 0)
            self.is_priority_mode = False
            return False
        return self.is_priority_mode
    
    def update_serving(self):
        current_time = time.time()
        
        if not self.serving:
            # check priority
            self.check_priority_condition()
            
            # get next lane to serve
            next_lane_data = self.lane_q.get_next_lane()
            
            if next_lane_data and next_lane_data[2].size() > 0:
                lane_name = next_lane_data[1]
                priority = next_lane_data[0]
                
                # set green light
                self.lights.set_green(lane_name)
                self.current_serving_lane = next_lane_data
                
                # calc how many to serve
                if lane_name == "AL2" and priority > 0:
                    self.vehicles_to_serve = max(0, next_lane_data[2].size() - 4)
                else:
                    self.vehicles_to_serve = self.calc_vehicles_to_serve()
                
                self.serve_count = 0
                self.serving = True
                self.last_serve_time = current_time
        else:
            # serving in progress
            if current_time - self.last_serve_time > 1.5:
                if self.serve_count < self.vehicles_to_serve:
                    if self.current_serving_lane[2].size() > 0:
                        v = self.current_serving_lane[2].remove_vehicle()
                        if v:
                            self.serve_count += 1
                            self.total_served += 1
                            print(f"Served: {v.id} from {self.current_serving_lane[1]}")
                    else:
                        self.serving = False
                        self.lights.set_red()
                else:
                    self.serving = False
                    self.lights.set_red()
                
                self.last_serve_time = current_time
    
    def draw(self):
        self.canvas.delete("all")
        
        self.draw_road()
        self.draw_vehicles()
        self.draw_traffic_lights()
        self.draw_stats()
        
        # redraw every 100ms
        self.root.after(100, self.draw)
    
    def draw_road(self):
        center_x = 700
        center_y = 425
        junction_size = 200
        road_width = 180  # wider for 3 lanes
        
        # junction box
        self.canvas.create_rectangle(
            center_x - junction_size//2, center_y - junction_size//2,
            center_x + junction_size//2, center_y + junction_size//2,
            fill='#404040', outline='white'
        )
        
        # Road A - Top
        self.canvas.create_rectangle(
            center_x - road_width//2, 0,
            center_x + road_width//2, center_y - junction_size//2,
            fill='gray', outline='white'
        )
        
        # Road B - Left
        self.canvas.create_rectangle(
            0, center_y - road_width//2,
            center_x - junction_size//2, center_y + road_width//2,
            fill='gray', outline='white'
        )
        
        # Road C - Bottom
        self.canvas.create_rectangle(
            center_x - road_width//2, center_y + junction_size//2,
            center_x + road_width//2, 850,
            fill='gray', outline='white'
        )
        
        # Road D - Right
        self.canvas.create_rectangle(
            center_x + junction_size//2, center_y - road_width//2,
            1400, center_y + road_width//2,
            fill='gray', outline='white'
        )
        
        # lane dividers - show 3 lanes clearly
        lane_div = road_width // 3
        
        # vertical lane dividers for A and C
        for offset in [-lane_div, lane_div]:
            for i in range(0, 850, 40):
                self.canvas.create_rectangle(
                    center_x + offset - 2, i, 
                    center_x + offset + 2, i + 20,
                    fill='yellow', outline=''
                )
        
        # horizontal lane dividers for B and D
        for offset in [-lane_div, lane_div]:
            for i in range(0, 1400, 40):
                self.canvas.create_rectangle(
                    i, center_y + offset - 2,
                    i + 20, center_y + offset + 2,
                    fill='yellow', outline=''
                )
    
    def draw_vehicles(self):
        center_x = 700
        center_y = 425
        lane_width = 60
        
        # Road A - top (3 lanes: L1, L2, L3)
        # AL1 - left lane
        vehicles = self.al1_queue.get_all()
        for idx, v in enumerate(vehicles[:8]):
            y_pos = center_y - 300 + (idx * 30)
            self.canvas.create_rectangle(
                center_x - 75, y_pos, center_x - 45, y_pos + 25,
                fill=v.color, outline='black', width=2
            )
            self.canvas.create_text(center_x - 60, y_pos + 12, text=v.id[-3:], fill='black', font=('Arial', 8))
        
        # AL2 - middle lane (PRIORITY)
        vehicles = self.al2_queue.get_all()
        for idx, v in enumerate(vehicles[:8]):
            y_pos = center_y - 300 + (idx * 30)
            self.canvas.create_rectangle(
                center_x - 15, y_pos, center_x + 15, y_pos + 25,
                fill=v.color, outline='black', width=2
            )
            self.canvas.create_text(center_x, y_pos + 12, text=v.id[-3:], fill='black', font=('Arial', 8))
        
        # AL3 - right lane (free left)
        vehicles = self.al3_queue.get_all()
        for idx, v in enumerate(vehicles[:8]):
            y_pos = center_y - 300 + (idx * 30)
            self.canvas.create_rectangle(
                center_x + 45, y_pos, center_x + 75, y_pos + 25,
                fill=v.color, outline='black', width=2
            )
            self.canvas.create_text(center_x + 60, y_pos + 12, text=v.id[-3:], fill='black', font=('Arial', 8))
        
        # Road B - left (3 lanes)
        # BL1
        vehicles = self.bl1_queue.get_all()
        for idx, v in enumerate(vehicles[:8]):
            x_pos = center_x - 300 + (idx * 30)
            self.canvas.create_rectangle(
                x_pos, center_y - 75, x_pos + 25, center_y - 45,
                fill=v.color, outline='black', width=2
            )
            self.canvas.create_text(x_pos + 12, center_y - 60, text=v.id[-3:], fill='black', font=('Arial', 8))
        
        # BL2
        vehicles = self.bl2_queue.get_all()
        for idx, v in enumerate(vehicles[:8]):
            x_pos = center_x - 300 + (idx * 30)
            self.canvas.create_rectangle(
                x_pos, center_y - 15, x_pos + 25, center_y + 15,
                fill=v.color, outline='black', width=2
            )
            self.canvas.create_text(x_pos + 12, center_y, text=v.id[-3:], fill='black', font=('Arial', 8))
        
        # BL3
        vehicles = self.bl3_queue.get_all()
        for idx, v in enumerate(vehicles[:8]):
            x_pos = center_x - 300 + (idx * 30)
            self.canvas.create_rectangle(
                x_pos, center_y + 45, x_pos + 25, center_y + 75,
                fill=v.color, outline='black', width=2
            )
            self.canvas.create_text(x_pos + 12, center_y + 60, text=v.id[-3:], fill='black', font=('Arial', 8))
        
        # Road C - bottom (3 lanes)
        # CL1
        vehicles = self.cl1_queue.get_all()
        for idx, v in enumerate(vehicles[:8]):
            y_pos = center_y + 300 - (idx * 30)
            self.canvas.create_rectangle(
                center_x + 45, y_pos, center_x + 75, y_pos + 25,
                fill=v.color, outline='black', width=2
            )
            self.canvas.create_text(center_x + 60, y_pos + 12, text=v.id[-3:], fill='black', font=('Arial', 8))
        
        # CL2
        vehicles = self.cl2_queue.get_all()
        for idx, v in enumerate(vehicles[:8]):
            y_pos = center_y + 300 - (idx * 30)
            self.canvas.create_rectangle(
                center_x - 15, y_pos, center_x + 15, y_pos + 25,
                fill=v.color, outline='black', width=2
            )
            self.canvas.create_text(center_x, y_pos + 12, text=v.id[-3:], fill='black', font=('Arial', 8))
        
        # CL3
        vehicles = self.cl3_queue.get_all()
        for idx, v in enumerate(vehicles[:8]):
            y_pos = center_y + 300 - (idx * 30)
            self.canvas.create_rectangle(
                center_x - 75, y_pos, center_x - 45, y_pos + 25,
                fill=v.color, outline='black', width=2
            )
            self.canvas.create_text(center_x - 60, y_pos + 12, text=v.id[-3:], fill='black', font=('Arial', 8))
        
        # Road D - right (3 lanes)
        # DL1
        vehicles = self.dl1_queue.get_all()
        for idx, v in enumerate(vehicles[:8]):
            x_pos = center_x + 300 - (idx * 30)
            self.canvas.create_rectangle(
                x_pos, center_y + 45, x_pos + 25, center_y + 75,
                fill=v.color, outline='black', width=2
            )
            self.canvas.create_text(x_pos + 12, center_y + 60, text=v.id[-3:], fill='black', font=('Arial', 8))
        
        # DL2
        vehicles = self.dl2_queue.get_all()
        for idx, v in enumerate(vehicles[:8]):
            x_pos = center_x + 300 - (idx * 30)
            self.canvas.create_rectangle(
                x_pos, center_y - 15, x_pos + 25, center_y + 15,
                fill=v.color, outline='black', width=2
            )
            self.canvas.create_text(x_pos + 12, center_y, text=v.id[-3:], fill='black', font=('Arial', 8))
        
        # DL3
        vehicles = self.dl3_queue.get_all()
        for idx, v in enumerate(vehicles[:8]):
            x_pos = center_x + 300 - (idx * 30)
            self.canvas.create_rectangle(
                x_pos, center_y - 75, x_pos + 25, center_y - 45,
                fill=v.color, outline='black', width=2
            )
            self.canvas.create_text(x_pos + 12, center_y - 60, text=v.id[-3:], fill='black', font=('Arial', 8))
    
    def draw_traffic_lights(self):
        center_x = 700
        center_y = 425
        
        # only lane 2s have traffic lights
        # AL2 light - top
        light_color = 'green' if self.lights.current_lane == "AL2" else 'red'
        self.canvas.create_oval(
            center_x - 20, center_y - 135,
            center_x + 20, center_y - 95,
            fill=light_color, outline='white', width=3
        )
        self.canvas.create_text(center_x, center_y - 80, text="AL2", fill='white', font=('Arial', 11, 'bold'))
        
        # BL2 light - left
        light_color = 'green' if self.lights.current_lane == "BL2" else 'red'
        self.canvas.create_oval(
            center_x - 135, center_y - 20,
            center_x - 95, center_y + 20,
            fill=light_color, outline='white', width=3
        )
        self.canvas.create_text(center_x - 80, center_y, text="BL2", fill='white', font=('Arial', 11, 'bold'))
        
        # CL2 light - bottom
        light_color = 'green' if self.lights.current_lane == "CL2" else 'red'
        self.canvas.create_oval(
            center_x - 20, center_y + 95,
            center_x + 20, center_y + 135,
            fill=light_color, outline='white', width=3
        )
        self.canvas.create_text(center_x, center_y + 150, text="CL2", fill='white', font=('Arial', 11, 'bold'))
        
        # DL2 light - right
        light_color = 'green' if self.lights.current_lane == "DL2" else 'red'
        self.canvas.create_oval(
            center_x + 95, center_y - 20,
            center_x + 135, center_y + 20,
            fill=light_color, outline='white', width=3
        )
        self.canvas.create_text(center_x + 150, center_y, text="DL2", fill='white', font=('Arial', 11, 'bold'))
    
    def draw_stats(self):
        # stats panel
        panel_x = 20
        panel_y = 20
        panel_width = 280
        panel_height = 480
        
        self.canvas.create_rectangle(
            panel_x, panel_y, panel_x + panel_width, panel_y + panel_height,
            fill='#323232', outline='white', width=2
        )
        
        # title
        self.canvas.create_text(
            panel_x + 140, panel_y + 25,
            text="TRAFFIC STATUS", fill='yellow',
            font=('Arial', 16, 'bold')
        )
        
        self.canvas.create_text(
            panel_x + 140, panel_y + 45,
            text="(12 Lanes Total)", fill='cyan',
            font=('Arial', 10)
        )
        
        y_offset = 75
        
        # Road A stats
        self.canvas.create_text(panel_x + 20, panel_y + y_offset, text="ROAD A:", fill='cyan', font=('Arial', 12, 'bold'), anchor='w')
        y_offset += 25
        
        self.canvas.create_text(panel_x + 30, panel_y + y_offset, text=f"AL1: {self.al1_queue.size()}", fill='white', font=('Arial', 10), anchor='w')
        y_offset += 20
        
        al2_color = 'orange' if self.is_priority_mode else 'white'
        self.canvas.create_text(panel_x + 30, panel_y + y_offset, text=f"AL2: {self.al2_queue.size()} (Priority)", fill=al2_color, font=('Arial', 10), anchor='w')
        if self.is_priority_mode:
            self.canvas.create_text(panel_x + 35, panel_y + y_offset + 15, text="[PRIORITY MODE]", fill='red', font=('Arial', 9), anchor='w')
            y_offset += 15
        y_offset += 20
        
        self.canvas.create_text(panel_x + 30, panel_y + y_offset, text=f"AL3: {self.al3_queue.size()} (Free L)", fill='lightgreen', font=('Arial', 10), anchor='w')
        y_offset += 30
        
        # Road B stats
        self.canvas.create_text(panel_x + 20, panel_y + y_offset, text="ROAD B:", fill='cyan', font=('Arial', 12, 'bold'), anchor='w')
        y_offset += 25
        self.canvas.create_text(panel_x + 30, panel_y + y_offset, text=f"BL1: {self.bl1_queue.size()}", fill='white', font=('Arial', 10), anchor='w')
        y_offset += 20
        self.canvas.create_text(panel_x + 30, panel_y + y_offset, text=f"BL2: {self.bl2_queue.size()}", fill='white', font=('Arial', 10), anchor='w')
        y_offset += 20
        self.canvas.create_text(panel_x + 30, panel_y + y_offset, text=f"BL3: {self.bl3_queue.size()} (Free L)", fill='lightgreen', font=('Arial', 10), anchor='w')
        y_offset += 30
        
        # Road C stats
        self.canvas.create_text(panel_x + 20, panel_y + y_offset, text="ROAD C:", fill='cyan', font=('Arial', 12, 'bold'), anchor='w')
        y_offset += 25
        self.canvas.create_text(panel_x + 30, panel_y + y_offset, text=f"CL1: {self.cl1_queue.size()}", fill='white', font=('Arial', 10), anchor='w')
        y_offset += 20
        self.canvas.create_text(panel_x + 30, panel_y + y_offset, text=f"CL2: {self.cl2_queue.size()}", fill='white', font=('Arial', 10), anchor='w')
        y_offset += 20
        self.canvas.create_text(panel_x + 30, panel_y + y_offset, text=f"CL3: {self.cl3_queue.size()} (Free L)", fill='lightgreen', font=('Arial', 10), anchor='w')
        y_offset += 30
        
        # Road D stats
        self.canvas.create_text(panel_x + 20, panel_y + y_offset, text="ROAD D:", fill='cyan', font=('Arial', 12, 'bold'), anchor='w')
        y_offset += 25
        self.canvas.create_text(panel_x + 30, panel_y + y_offset, text=f"DL1: {self.dl1_queue.size()}", fill='white', font=('Arial', 10), anchor='w')
        y_offset += 20
        self.canvas.create_text(panel_x + 30, panel_y + y_offset, text=f"DL2: {self.dl2_queue.size()}", fill='white', font=('Arial', 10), anchor='w')
        y_offset += 20
        self.canvas.create_text(panel_x + 30, panel_y + y_offset, text=f"DL3: {self.dl3_queue.size()} (Free L)", fill='lightgreen', font=('Arial', 10), anchor='w')
        y_offset += 35
        
        # current light status
        if self.lights.current_lane:
            status_text = f"GREEN: {self.lights.current_lane}"
            status_color = 'green'
        else:
            status_text = "All RED"
            status_color = 'red'
        
        self.canvas.create_text(
            panel_x + 20, panel_y + y_offset,
            text=status_text, fill=status_color,
            font=('Arial', 12, 'bold'), anchor='w'
        )
        y_offset += 25
        
        # total served
        self.canvas.create_text(
            panel_x + 20, panel_y + y_offset,
            text=f"Total Served: {self.total_served}",
            fill='white', font=('Arial', 11), anchor='w'
        )
    
    def on_closing(self):
        self.running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficSimulator(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()# edit
# more
# update
# change
# thing
# edit again
# more changes
