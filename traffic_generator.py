import random
import time
import json
import os

# vehicle generator - now generates for all 3 lanes per road
class VehicleGenerator:
    def __init__(self):
        self.vehicle_counter = 0
        # all 12 lanes
        self.lanes = [
            "AL1", "AL2", "AL3",  # Road A
            "BL1", "BL2", "BL3",  # Road B
            "CL1", "CL2", "CL3",  # Road C
            "DL1", "DL2", "DL3"   # Road D
        ]
        self.files = {
            "lanea.txt": ["AL1", "AL2", "AL3"],
            "laneb.txt": ["BL1", "BL2", "BL3"],
            "lanec.txt": ["CL1", "CL2", "CL3"],
            "laned.txt": ["DL1", "DL2", "DL3"]
        }
        
        # make sure files exist
        for f in self.files.keys():
            if not os.path.exists(f):
                open(f, 'w').close()
    
    def generate_vehicle(self, lane):
        self.vehicle_counter += 1
        v_data = {
            'id': f"V{self.vehicle_counter}",
            'lane': lane
        }
        return v_data
    
    def write_to_file(self, fname, vehicle_data):
        with open(fname, 'a') as f:
            f.write(json.dumps(vehicle_data) + '\n')
    
    def random_generation(self):
        # generate vehicles for each road file
        for fname, lane_list in self.files.items():
            for lane in lane_list:
                # default vehicles per lane
                num_vehicles = 0
                
                # L1 lanes (incoming) - moderate traffic
                if 'L1' in lane:
                    num_vehicles = random.randint(1, 3)
                
                # AL2 is priority lane - give it more vehicles sometimes to trigger priority mode
                elif lane == "AL2":
                    if random.random() > 0.65:
                        num_vehicles = random.randint(4, 7)  # burst for priority mode
                    else:
                        num_vehicles = random.randint(1, 3)
                
                # L2 lanes (need traffic light) - regular traffic
                elif 'L2' in lane:
                    num_vehicles = random.randint(1, 4)
                
                # L3 lanes (free left turn) - light to moderate traffic
                elif 'L3' in lane:
                    num_vehicles = random.randint(1, 3)
                
                for _ in range(num_vehicles):
                    v = self.generate_vehicle(lane)
                    self.write_to_file(fname, v)
                    print(f"Generated {v['id']} for {lane}")
    
    def run(self):
        print("Vehicle Generator Started...")
        print("Generating vehicles for 12 lanes (3 per road)")
        print("AL2 is priority lane, L3 lanes are free left turn\n")
        
        gen_cycle = 0
        while True:
            gen_cycle += 1
            print(f"\n--- Generation Cycle {gen_cycle} ---")
            
            self.random_generation()
            
            time.sleep(5)  # generate new vehicles every 5 sec

if __name__ == "__main__":
    generator = VehicleGenerator()
    try:
        generator.run()
    except KeyboardInterrupt:
        print("\n\nGenerator stopped by user")# works now
# change
