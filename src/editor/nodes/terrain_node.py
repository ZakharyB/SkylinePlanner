from src.editor.node import Node
from src.terrain.heightmap_generator import generate_heightmap
import numpy as np

class TerrainNode(Node):
    def __init__(self):
        super().__init__("Terrain", outputs=["heightmap"])
        self.width = 256
        self.height = 256

    def process(self):
        heightmap = generate_heightmap(self.width, self.height)
        return {"heightmap": heightmap}
    
if __name__ == "__main__":
    node = TerrainNode()
    result = node.process()
    print(f"Heightmap shape: {result['heightmap'].shape}")
    print(f"Heightmap min: {np.min(result['heightmap'])}, max: {np.max(result['heightmap'])}")