from src.editor.node import Node
from src.terrain.heightmap_generator import generate_heightmap
import numpy as np

class TerrainNode(Node):
    def __init__(self):
        super().__init__("Terrain", outputs=["heightmap"])
        self.config = {
            'width': 256,
            'height': 256,
            'roughness': 0.5,
            'seed': 42
        }

    def get_config_options(self):
        return self.config
    
    def update_config(self, new_config):
        self.config.update(new_config)
        self.process()

    def process(self):
        heightmap = generate_heightmap(
            self.config['width'],
            self.config['height'],
            roughness=self.config['roughness'],
            seed=self.config['seed']
        )
        return {"heightmap": heightmap}
    
if __name__ == "__main__":
    node = TerrainNode()
    result = node.process()
    print(f"Heightmap shape: {result['heightmap'].shape}")
    print(f"Heightmap min: {np.min(result['heightmap'])}, max: {np.max(result['heightmap'])}")