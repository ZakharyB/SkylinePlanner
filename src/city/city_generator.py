import numpy as np
from src.terrain.heightmap_generator import generate_heightmap
from src.terrain.water_generator import WaterGenerator
from src.city.city_limits import CityLimits
from src.city.zoning import Zoning
from src.roads.road_network import RoadNetwork
from src.buildings.building_placement import BuildingPlacer
from src.city.parks_and_landmarks import ParksAndLandmarks

class CityGenerator:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.heightmap = None
        self.water_map = None
        self.city_limits = None
        self.zoning = None
        self.road_network = None
        self.building_placer = None
        self.parks_and_landmarks = None

    def generate_city(self):
        # Generate terrain
        self.heightmap = generate_heightmap(self.width, self.height)

        # Generate water features
        water_gen = WaterGenerator(self.width, self.height)
        self.heightmap, self.water_map = water_gen.apply_water_features(self.heightmap)

        # Create city limits
        self.city_limits = CityLimits(self.width, self.height)

        # Create road network
        self.road_network = RoadNetwork(self.width, self.height)
        self.road_network.generate_organic_network(self.heightmap, self.water_map)

        # Create zoning
        self.zoning = Zoning(self.width, self.height)
        self.zoning.generate_sophisticated_zoning(self.water_map, self.road_network)

        # Generate parks and landmarks
        self.parks_and_landmarks = ParksAndLandmarks(self.width, self.height)
        self.parks_and_landmarks.generate_parks(self.zoning, self.water_map, self.road_network)
        self.parks_and_landmarks.generate_landmarks(self.zoning, self.water_map, self.road_network)

        # Place buildings
        self.building_placer = BuildingPlacer(self.width, self.height)
        self.building_placer.place_buildings_in_zones(self.zoning, self.road_network, self.heightmap, self.water_map)

    def get_city_data(self):
        return {
            'heightmap': self.heightmap,
            'water_map': self.water_map,
            'zoning': self.zoning.zones,
            'roads': self.road_network.roads,
            'main_roads': self.road_network.main_roads,
            'buildings': self.building_placer.get_building_map(),
            'parks': self.parks_and_landmarks.parks,
            'landmarks': self.parks_and_landmarks.landmarks
        }

if __name__ == "__main__":
    generator = CityGenerator(256, 256)
    generator.generate_city()
    print("City generated successfully!")