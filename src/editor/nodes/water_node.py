from src.editor.node import Node
from src.terrain.water_generator import WaterGenerator

class WaterNode(Node):
    def __init__(self):
        super().__init__("Water", inputs=["heightmap"], outputs=["water_map", "updated_heightmap"])
        self.water_generator = WaterGenerator(256, 256)

    def process(self, heightmap):
        updated_heightmap, water_map = self.water_generator.apply_water_features(heightmap)
        return {"water_map": water_map, "updated_heightmap": updated_heightmap}

if __name__ == "__main__":
    import numpy as np
    from src.terrain.heightmap_generator import generate_heightmap

    heightmap = generate_heightmap(256, 256)
    node = WaterNode()
    result = node.process(heightmap)
    print(f"Water map shape: {result['water_map'].shape}")
    print(f"Water coverage: {np.sum(result['water_map']) / (256 * 256) * 100:.2f}%")