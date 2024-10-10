import numpy as np
from scipy.ndimage import gaussian_filter

class WaterGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def generate_river(self, heightmap, start_point=None, meander=0.3, river_width=3):
        if start_point is None:
            start_point = (np.random.randint(0, self.width), 0)

        river = np.zeros((self.height, self.width), dtype=bool)
        x, y = start_point

        while 0 <= y < self.height - 1:
            river[y, max(0, x-river_width//2):min(self.width, x+river_width//2+1)] = True
            
            # Move downhill
            next_y = y + 1
            possible_x = [x-1, x, x+1]
            possible_x = [px for px in possible_x if 0 <= px < self.width]
            next_x = min(possible_x, key=lambda px: heightmap[next_y, px])
            
            # Add meandering
            if np.random.random() < meander:
                next_x += np.random.choice([-1, 1])
                next_x = max(0, min(self.width-1, next_x))
            
            x, y = next_x, next_y

        return river

    def generate_lake(self, heightmap, size_factor=0.05):
        lake_size = int(self.width * self.height * size_factor)
        lake_seed = np.argpartition(heightmap.flatten(), lake_size)[:lake_size]
        lake = np.zeros((self.height, self.width), dtype=bool)
        lake.flat[lake_seed] = True
        
        # Smooth the lake edges
        lake = gaussian_filter(lake.astype(float), sigma=2) > 0.5
        
        return lake

    def apply_water_features(self, heightmap):
        river = self.generate_river(heightmap)
        lake = self.generate_lake(heightmap)
        
        water_map = river | lake
        
        # Lower the heightmap where there's water
        heightmap[water_map] = np.minimum(heightmap[water_map], np.min(heightmap) * 1.1)
        
        return heightmap, water_map

if __name__ == "__main__":
    from src.terrain.heightmap_generator import generate_heightmap
    import matplotlib.pyplot as plt

    width, height = 256, 256
    heightmap = generate_heightmap(width, height)
    
    water_gen = WaterGenerator(width, height)
    heightmap, water_map = water_gen.apply_water_features(heightmap)

    plt.figure(figsize=(10, 5))
    plt.subplot(121)
    plt.imshow(heightmap, cmap='terrain')
    plt.title('Terrain with Water Features')
    plt.subplot(122)
    plt.imshow(water_map, cmap='Blues')
    plt.title('Water Map')
    plt.show()