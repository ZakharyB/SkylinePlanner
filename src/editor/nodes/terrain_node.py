from dataclasses import dataclass, asdict
from typing import Dict, Any

import numpy as np

from src.editor.node import Node
from src.utils.math_utils import perlin

@dataclass
class TerrainConfig:
    width: int = 256
    height: int = 256
    scale: float = 50.0
    seed: int = 0

class TerrainNode(Node):
    def __init__(self, title: str):
        super().__init__(title, inputs=[], outputs=['heightmap'])
        self.config = TerrainConfig()

    def get_config_options(self) -> Dict[str, Any]:
        return asdict(self.config)
    
    def update_config(self, new_config: Dict[str, Any]) -> None:
        for key, value in new_config.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                raise ValueError(f"Invalid configuration option: {key}")
        self.process()

    def process(self) -> None:
        if self.config.width <= 0 or self.config.height <= 0:
            raise ValueError("Width and height must be positive integers")
        if self.config.scale <= 0:
            raise ValueError("Scale must be a positive number")

        x = np.arange(self.config.width) / self.config.scale
        y = np.arange(self.config.height) / self.config.scale
        xx, yy = np.meshgrid(x, y)
        
        heightmap = perlin(xx, yy, self.config.seed)
        self.output_data['heightmap'] = heightmap

def main() -> None:
    node = TerrainNode("Terrain Generator")
    node.process()
    result = node.output_data['heightmap']
    print(f"Heightmap shape: {result.shape}")
    print(f"Heightmap min: {np.min(result)}, max: {np.max(result)}")

if __name__ == "__main__":
    main()