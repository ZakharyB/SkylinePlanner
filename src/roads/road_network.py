import numpy as np

class RoadNetwork:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.roads = np.zeros((height, width), dtype=bool)
        self.main_roads = np.zeros((height, width), dtype=bool)
    
    def add_road(self, x, y, is_main=False):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.roads[y, x] = True
            if is_main:
                self.main_roads[y, x] = True
    
    def has_road(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.roads[y, x]
        return False

    def generate_organic_network(self, heightmap, water_map, num_seeds=5, max_roads=1000, max_slope=0.1):
        seeds = [(np.random.randint(0, self.width), np.random.randint(0, self.height)) 
                 for _ in range(num_seeds)]
        
        for seed in seeds:
            self.grow_road_from_seed(seed, heightmap, water_map, max_roads // num_seeds, max_slope, is_main=True)

    def grow_road_from_seed(self, seed, heightmap, water_map, max_roads, max_slope, is_main=False):
        stack = [seed]
        roads_added = 0
        
        while stack and roads_added < max_roads:
            x, y = stack.pop()
            if not self.has_road(x, y) and not water_map[y, x]:
                self.add_road(x, y, is_main)
                roads_added += 1
                
                for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if (0 <= nx < self.width and 0 <= ny < self.height and
                        not water_map[ny, nx] and
                        abs(heightmap[ny, nx] - heightmap[y, x]) <= max_slope):
                        stack.append((nx, ny))

if __name__ == "__main__":
    from src.terrain.heightmap_generator import generate_heightmap
    from src.terrain.water_generator import WaterGenerator
    
    width, height = 256, 256
    heightmap = generate_heightmap(width, height)
    water_gen = WaterGenerator(width, height)
    heightmap, water_map = water_gen.apply_water_features(heightmap)
    
    network = RoadNetwork(width, height)
    network.generate_organic_network(heightmap, water_map)
    print(f"Road network created with shape: {network.roads.shape}")
    print(f"Total road tiles: {np.sum(network.roads)}")
    print(f"Total main road tiles: {np.sum(network.main_roads)}")