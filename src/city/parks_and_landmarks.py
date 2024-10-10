import numpy as np

class ParksAndLandmarks:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.parks = np.zeros((height, width), dtype=bool)
        self.landmarks = np.zeros((height, width), dtype=bool)

    def generate_parks(self, zoning, water_map, road_network, num_parks=5, min_size=10, max_size=30):
        for _ in range(num_parks):
            size = np.random.randint(min_size, max_size)
            attempts = 0
            while attempts < 100:
                x = np.random.randint(0, self.width - size)
                y = np.random.randint(0, self.height - size)
                if self.can_place_park(x, y, size, zoning, water_map, road_network):
                    self.parks[y:y+size, x:x+size] = True
                    zoning.zones[y:y+size, x:x+size] = 0  # Set park area to no zoning
                    break
                attempts += 1

    def can_place_park(self, x, y, size, zoning, water_map, road_network):
        area = zoning.zones[y:y+size, x:x+size]
        return (not np.any(water_map[y:y+size, x:x+size]) and
                not np.any(road_network.roads[y:y+size, x:x+size]) and
                np.all(area > 0))  # Ensure we're not placing on water or existing parks

    def generate_landmarks(self, zoning, water_map, road_network, num_landmarks=3, size=5):
        for _ in range(num_landmarks):
            attempts = 0
            while attempts < 100:
                x = np.random.randint(0, self.width - size)
                y = np.random.randint(0, self.height - size)
                if self.can_place_landmark(x, y, size, zoning, water_map, road_network):
                    self.landmarks[y:y+size, x:x+size] = True
                    zoning.zones[y:y+size, x:x+size] = 4  # Set landmark area to special zoning
                    break
                attempts += 1

    def can_place_landmark(self, x, y, size, zoning, water_map, road_network):
        area = zoning.zones[y:y+size, x:x+size]
        return (not np.any(water_map[y:y+size, x:x+size]) and
                not np.any(road_network.roads[y:y+size, x:x+size]) and
                np.all(area > 0) and  # Ensure we're not placing on water or existing parks/landmarks
                np.any(road_network.roads[max(0,y-2):min(self.height,y+size+2), 
                                          max(0,x-2):min(self.width,x+size+2)]))  # Ensure it's near a road

if __name__ == "__main__":
    from src.city.zoning import Zoning
    from src.roads.road_network import RoadNetwork
    from src.terrain.water_generator import WaterGenerator
    
    width, height = 256, 256
    zoning = Zoning(width, height)
    road_network = RoadNetwork(width, height)
    water_gen = WaterGenerator(width, height)
    
    # Generate some dummy data
    zoning.generate_random_zoning(np.zeros((height, width), dtype=bool))
    road_network.generate_organic_network(np.random.rand(height, width), np.zeros((height, width), dtype=bool))
    _, water_map = water_gen.apply_water_features(np.random.rand(height, width))
    
    parks_and_landmarks = ParksAndLandmarks(width, height)
    parks_and_landmarks.generate_parks(zoning, water_map, road_network)
    parks_and_landmarks.generate_landmarks(zoning, water_map, road_network)
    
    print(f"Number of park tiles: {np.sum(parks_and_landmarks.parks)}")
    print(f"Number of landmark tiles: {np.sum(parks_and_landmarks.landmarks)}")