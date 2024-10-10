from src.editor.node import Node
from src.buildings.building_placement import BuildingPlacer
from src.city.parks_and_landmarks import ParksAndLandmarks

class CityNode(Node):
    def __init__(self):
        super().__init__("City", inputs=["heightmap", "water_map", "road_network", "zoning_map"], outputs=["city_data"])
        self.building_placer = BuildingPlacer(256, 256)
        self.parks_and_landmarks = ParksAndLandmarks(256, 256)

    def process(self, heightmap, water_map, road_network, zoning_map):
        # Generate parks and landmarks
        self.parks_and_landmarks.generate_parks(zoning_map, water_map, road_network)
        self.parks_and_landmarks.generate_landmarks(zoning_map, water_map, road_network)

        # Place buildings
        self.building_placer.place_buildings_in_zones(zoning_map, road_network, heightmap, water_map)

        city_data = {
            'heightmap': heightmap,
            'water_map': water_map,
            'zoning': zoning_map,
            'roads': road_network,
            'buildings': self.building_placer.get_building_map(),
            'parks': self.parks_and_landmarks.parks,
            'landmarks': self.parks_and_landmarks.landmarks
        }

        return {"city_data": city_data}

if __name__ == "__main__":
    import numpy as np
    from src.terrain.heightmap_generator import generate_heightmap
    from src.terrain.water_generator import WaterGenerator
    from src.roads.road_network import RoadNetwork
    from src.city.zoning import Zoning

    heightmap = generate_heightmap(256, 256)
    water_gen = WaterGenerator(256, 256)
    _, water_map = water_gen.apply_water_features(heightmap)
    road_network = RoadNetwork(256, 256)
    road_network.generate_organic_network(heightmap, water_map)
    zoning = Zoning(256, 256)
    zoning.generate_sophisticated_zoning(water_map, road_network.roads)

    node = CityNode()
    result = node.process(heightmap, water_map, road_network.roads, zoning.zones)
    city_data = result['city_data']
    print("City generation complete. Summary:")
    print(f"Water coverage: {np.sum(city_data['water_map']) / (256 * 256) * 100:.2f}%")
    print(f"Road coverage: {np.sum(city_data['roads']) / (256 * 256) * 100:.2f}%")
    print(f"Building coverage: {np.sum(city_data['buildings'] > 0) / (256 * 256) * 100:.2f}%")
    print(f"Park coverage: {np.sum(city_data['parks']) / (256 * 256) * 100:.2f}%")
    print(f"Number of landmarks: {np.sum(city_data['landmarks'])}")