import numpy as np
from src.utils.math_utils import perlin

def generate_heightmap(width, height, scale=50.0, octaves=6, persistence=0.5, lacunarity=2.0):
    """Generate a heightmap using multiple octaves of Perlin noise."""
    heightmap = np.zeros((height, width))
    for i in range(octaves):
        frequency = lacunarity ** i
        amplitude = persistence ** i
        for y in range(height):
            for x in range(width):
                heightmap[y][x] += perlin(x / scale * frequency, y / scale * frequency) * amplitude
    
    # Normalize the heightmap
    heightmap = (heightmap - np.min(heightmap)) / (np.max(heightmap) - np.min(heightmap))
    return heightmap

if __name__ == "__main__":
    heightmap = generate_heightmap(256, 256)
    print(f"Heightmap shape: {heightmap.shape}")
    print(f"Heightmap min: {np.min(heightmap)}, max: {np.max(heightmap)}")