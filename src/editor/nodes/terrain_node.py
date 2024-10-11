from src.editor.node import Node
from src.terrain.heightmap_generator import generate_heightmap
from src.utils.math_utils import perlin
import numpy as np

class TerrainNode(Node):
    def __init__(self, title):
        super().__init__(title, inputs=[], outputs=['heightmap'])
        self.config = {
            'width': 256,
            'height': 256,
            'scale': 50,  
            'seed': 0
        }

    def get_config_options(self):
        return self.config
    
    def update_config(self, new_config):
        self.config.update(new_config)
        self.process()

    def process(self):
        heightmap = np.zeros((self.config['height'], self.config['width']))
        for y in range(self.config['height']):
            for x in range(self.config['width']):
                heightmap[y, x] = perlin(x / self.config['scale'], y / self.config['scale'], self.config['seed'])
        self.output_data['heightmap'] = heightmap

if __name__ == "__main__":
    node = TerrainNode()
    result = node.process()
    print(f"Heightmap shape: {result['heightmap'].shape}")
    print(f"Heightmap min: {np.min(result['heightmap'])}, max: {np.max(result['heightmap'])}")