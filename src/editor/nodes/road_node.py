from src.editor.node import Node
from src.roads.road_network import RoadNetwork
import numpy as np

class RoadNode(Node):
    def __init__(self):
        super().__init__("Roads", inputs=["heightmap", "water_map"], outputs=["road_network"])
        self.road_network = RoadNetwork(256, 256)

    def process(self, heightmap, water_map):
        self.road_network.generate_organic_network(heightmap, water_map)
        return {"road_network": self.road_network.roads}

if __name__ == "__main__":
    from src.terrain.heightmap_generator import generate_heightmap
    from src.terrain.water_generator import WaterGenerator

    heightmap = generate_heightmap(256, 256)
    water_gen = WaterGenerator(256, 256)
    _, water_map = water_gen.apply_water_features(heightmap)

    node = RoadNode()
    result = node.process(heightmap, water_map)
    print(f"Road network shape: {result['road_network'].shape}")
    print(f"Road coverage: {np.sum(result['road_network']) / (256 * 256) * 100:.2f}%")