import matplotlib.pyplot as plt
import numpy as np

class CityVisualizer:
    @staticmethod
    def visualize_city(city_data):
        fig, axs = plt.subplots(2, 2, figsize=(15, 15))
        
        # Visualize heightmap with water
        terrain_with_water = city_data['heightmap'].copy()
        terrain_with_water[city_data['water_map']] = np.min(terrain_with_water)
        axs[0, 0].imshow(terrain_with_water, cmap='terrain')
        axs[0, 0].set_title('Terrain with Water')
        
        # Visualize zoning with parks and landmarks
        zoning_cmap = plt.cm.colors.ListedColormap(['blue', 'green', 'yellowgreen', 'yellow', 'red', 'purple', 'orange', 'darkgreen', 'gold'])
        zoning_with_features = city_data['zoning'].copy()
        zoning_with_features[city_data['parks']] = 7
        zoning_with_features[city_data['landmarks']] = 8
        axs[0, 1].imshow(zoning_with_features, cmap=zoning_cmap)
        axs[0, 1].set_title('Sophisticated Zoning with Parks and Landmarks')
        
        # Visualize roads, buildings, water, parks, and landmarks
        city_map = np.zeros_like(city_data['zoning'])
        city_map[city_data['water_map']] = 1
        city_map[city_data['roads']] = 2
        city_map[city_data['main_roads']] = 3
        city_map[city_data['buildings'] > 0] = city_data['buildings'][city_data['buildings'] > 0] + 3
        city_map[city_data['parks']] = 8
        city_map[city_data['landmarks']] = 9
        city_cmap = plt.cm.colors.ListedColormap(['white', 'blue', 'gray', 'black', 'lightgreen', 'green', 'darkgreen', 'red', 'darkgreen', 'gold'])
        axs[1, 0].imshow(city_map, cmap=city_cmap)
        axs[1, 0].set_title('City Map with Sophisticated Zoning')
        
        # Visualize roads, buildings, water, parks, and landmarks
        city_map = np.zeros_like(city_data['zoning'])
        city_map[city_data['water_map']] = 1
        city_map[city_data['roads']] = 2
        city_map[city_data['main_roads']] = 3
        city_map[city_data['buildings'] > 0] = city_data['buildings'][city_data['buildings'] > 0] + 3
        city_map[city_data['parks']] = 7
        city_map[city_data['landmarks']] = 8
        city_cmap = plt.cm.colors.ListedColormap(['white', 'blue', 'gray', 'black', 'green', 'red', 'purple', 'darkgreen', 'yellow'])
        axs[1, 0].imshow(city_map, cmap=city_cmap)
        axs[1, 0].set_title('City Map with Water, Parks, and Landmarks')
        
        # Visualize 3D terrain with roads, water, parks, and landmarks
        ax_3d = fig.add_subplot(2, 2, 4, projection='3d')
        x, y = np.meshgrid(np.arange(city_data['heightmap'].shape[1]), np.arange(city_data['heightmap'].shape[0]))
        ax_3d.plot_surface(x, y, city_data['heightmap'], cmap='terrain', alpha=0.5)
        
        water_level = np.min(city_data['heightmap']) - 0.05
        ax_3d.scatter(x[city_data['water_map']], y[city_data['water_map']], 
                      water_level, c='blue', s=1, alpha=0.5)
        
        road_height = np.min(city_data['heightmap']) - 0.1
        ax_3d.scatter(x[city_data['roads']], y[city_data['roads']], 
                      city_data['heightmap'][city_data['roads']], c='gray', s=1)
        ax_3d.scatter(x[city_data['main_roads']], y[city_data['main_roads']], 
                      city_data['heightmap'][city_data['main_roads']], c='black', s=1)
        
        park_height = np.max(city_data['heightmap']) + 0.1
        ax_3d.scatter(x[city_data['parks']], y[city_data['parks']], 
                      city_data['heightmap'][city_data['parks']], c='darkgreen', s=1)
        
        landmark_height = np.max(city_data['heightmap']) + 0.2
        ax_3d.scatter(x[city_data['landmarks']], y[city_data['landmarks']], 
                      city_data['heightmap'][city_data['landmarks']], c='yellow', s=1)
        
        ax_3d.set_title('3D Terrain with Roads, Water, Parks, and Landmarks')
        ax_3d.set_zlim(water_level, np.max(city_data['heightmap']) + 0.3)
        
        plt.tight_layout()
        plt.show()

    @staticmethod
    def save_city_image(city_data, filename):
        plt.figure(figsize=(10, 10))
        
        city_map = np.zeros_like(city_data['zoning'])
        city_map[city_data['water_map']] = 1
        city_map[city_data['roads']] = 2
        city_map[city_data['main_roads']] = 3
        city_map[city_data['buildings'] > 0] = city_data['buildings'][city_data['buildings'] > 0] + 3
        city_map[city_data['parks']] = 7
        city_map[city_data['landmarks']] = 8
        
        city_cmap = plt.cm.colors.ListedColormap(['#C0C0C0', '#4169E1', '#808080', '#000000', '#90EE90', '#FF4500', '#800080', '#228B22', '#FFD700'])
        plt.imshow(city_map, cmap=city_cmap)
        plt.axis('off')
        plt.title('Generated City with Parks and Landmarks')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

if __name__ == "__main__":
    from src.city.city_generator import CityGenerator
    
    generator = CityGenerator(256, 256)
    generator.generate_city()
    city_data = generator.get_city_data()
    
    CityVisualizer.visualize_city(city_data)
    CityVisualizer.save_city_image(city_data, 'generated_city_with_parks_and_landmarks.png')