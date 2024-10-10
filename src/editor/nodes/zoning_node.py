from src.editor.node import Node
from src.city.zoning import Zoning

class ZoningNode(Node):
    def __init__(self):
        super().__init__("Zoning", inputs=["heightmap", "water_map", "road_network"], outputs=["zoning_map"])
        self.zoning = Zoning(256, 256)

    def process(self, heightmap, water_map, road_network):
        self.zoning.generate_sophisticated_zoning(water_map, road_network)
        return {"zoning_map": self.zoning.zones}

if __name__ == "__main__":
    import numpy as np
    from src.terrain.heightmap_generator import generate_heightmap
    from src.terrain.water_generator import WaterGenerator
    from src.roads.road_network import RoadNetwork

    heightmap = generate_heightmap(256, 256)
    water_gen = WaterGenerator(256, 256)
    _, water_map = water_gen.apply_water_features(heightmap)
    road_network = RoadNetwork(256, 256)
    road_network.generate_organic_network(heightmap, water_map)

    node = ZoningNode()
    result = node.process(heightmap, water_map, road_network.roads)
    print(f"Zoning map shape: {result['zoning_map'].shape}")
    unique, counts = np.unique(result['zoning_map'], return_counts=True)
    for zone, count in zip(unique, counts):
        print(f"Zone {zone}: {count} tiles ({count / (256 * 256) * 100:.2f}%)")