import numpy as np
from scipy.ndimage import distance_transform_edt

class Zoning:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.zones = np.zeros((height, width), dtype=int)
        
    def set_zone(self, x, y, zone_type):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.zones[y, x] = zone_type
        
    def get_zone(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.zones[y, x]
        return None

    def generate_sophisticated_zoning(self, water_map, road_network, city_center=None):
        # Define zone types
        WATER = 0
        LOW_RES = 1
        MED_RES = 2
        HIGH_RES = 3
        COMMERCIAL = 4
        INDUSTRIAL = 5
        MIXED_USE = 6

        # Initialize with low-density residential
        self.zones = np.full((self.height, self.width), LOW_RES)

        # Set water areas
        self.zones[water_map] = WATER

        # Define city center if not provided
        if city_center is None:
            city_center = (self.width // 2, self.height // 2)

        # Calculate distance from city center
        y, x = np.ogrid[:self.height, :self.width]
        center_dist = np.sqrt((x - city_center[0])**2 + (y - city_center[1])**2)
        max_dist = np.max(center_dist)

        # Create mixed-use and high-density residential near the city center
        center_mask = center_dist < max_dist * 0.1
        self.zones[center_mask] = MIXED_USE
        self.zones[(center_dist < max_dist * 0.2) & (self.zones == LOW_RES)] = HIGH_RES

        # Create medium-density residential in a ring around the center
        self.zones[(center_dist < max_dist * 0.4) & (self.zones == LOW_RES)] = MED_RES

        # Place commercial zones near roads and residential areas
        road_dist = distance_transform_edt(~road_network.roads)
        commercial_mask = (road_dist < 3) & (self.zones >= LOW_RES) & (self.zones <= HIGH_RES)
        self.zones[commercial_mask] = COMMERCIAL

        # Place industrial zones on the outskirts
        industrial_mask = (center_dist > max_dist * 0.7) & (self.zones == LOW_RES)
        self.zones[industrial_mask] = INDUSTRIAL

        # Ensure no zones are placed on roads
        self.zones[road_network.roads] = WATER  # Using WATER as a placeholder for roads

        # Smooth transitions between zones
        self.smooth_transitions()

    def smooth_transitions(self, iterations=2):
        for _ in range(iterations):
            new_zones = self.zones.copy()
            for y in range(1, self.height - 1):
                for x in range(1, self.width - 1):
                    if self.zones[y, x] != 0:  # Skip water/road areas
                        neighborhood = self.zones[y-1:y+2, x-1:x+2].flatten()
                        new_zones[y, x] = np.argmax(np.bincount(neighborhood))
            self.zones = new_zones

if __name__ == "__main__":
    from src.roads.road_network import RoadNetwork
    from src.terrain.water_generator import WaterGenerator
    import matplotlib.pyplot as plt

    width, height = 256, 256
    zoning = Zoning(width, height)
    road_network = RoadNetwork(width, height)
    water_gen = WaterGenerator(width, height)

    # Generate some dummy data
    road_network.generate_organic_network(np.random.rand(height, width), np.zeros((height, width), dtype=bool))
    _, water_map = water_gen.apply_water_features(np.random.rand(height, width))

    zoning.generate_sophisticated_zoning(water_map, road_network)

    # Visualize the zoning
    plt.figure(figsize=(10, 10))
    cmap = plt.cm.colors.ListedColormap(['blue', 'green', 'yellowgreen', 'yellow', 'red', 'purple', 'orange'])
    plt.imshow(zoning.zones, cmap=cmap)
    plt.colorbar(ticks=range(7), label='Zone Type')
    plt.title('Sophisticated Zoning')
    plt.show()

    print("Zoning distribution:")
    unique, counts = np.unique(zoning.zones, return_counts=True)
    for zone, count in zip(unique, counts):
        print(f"Zone {zone}: {count} tiles")