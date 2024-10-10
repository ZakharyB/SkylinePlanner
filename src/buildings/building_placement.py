import numpy as np

class Building:
    def __init__(self, x, y, width, height, building_type):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = building_type

class BuildingPlacer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.buildings = []
    
    def place_building(self, x, y, building_width, building_height, building_type):
        new_building = Building(x, y, building_width, building_height, building_type)
        self.buildings.append(new_building)
        return True

    def is_area_clear(self, x, y, width, height, water_map):
        if np.any(water_map[y:y+height, x:x+width]):
            return False
        for building in self.buildings:
            if (x < building.x + building.width and x + width > building.x and
                y < building.y + building.height and y + height > building.y):
                return False
        return True

    def place_buildings_in_zones(self, zoning, road_network, heightmap, water_map):
        for y in range(self.height):
            for x in range(self.width):
                if not road_network.has_road(x, y) and not water_map[y, x] and heightmap[y, x] < 0.7:
                    zone = zoning.get_zone(x, y)
                    if zone == 1:  # Residential
                        if self.is_area_clear(x, y, 2, 2, water_map):
                            self.place_building(x, y, 2, 2, "residential")
                    elif zone == 2:  # Commercial
                        if self.is_area_clear(x, y, 3, 3, water_map):
                            self.place_building(x, y, 3, 3, "commercial")
                    elif zone == 3:  # Industrial
                        if self.is_area_clear(x, y, 4, 4, water_map):
                            self.place_building(x, y, 4, 4, "industrial")

    def get_building_map(self):
        building_map = np.zeros((self.height, self.width), dtype=int)
        for building in self.buildings:
            building_map[building.y:building.y+building.height, 
                         building.x:building.x+building.width] = self.get_building_type_id(building.type)
        return building_map

    @staticmethod
    def get_building_type_id(building_type):
        return {"residential": 1, "commercial": 2, "industrial": 3}.get(building_type, 0)

if __name__ == "__main__":
    from src.terrain.heightmap_generator import generate_heightmap
    from src.terrain.water_generator import WaterGenerator
    from src.city.zoning import Zoning
    from src.roads.road_network import RoadNetwork

    width, height = 256, 256
    heightmap = generate_heightmap(width, height)
    water_gen = WaterGenerator(width, height)
    heightmap, water_map = water_gen.apply_water_features(heightmap)
    
    zoning = Zoning(width, height)
    zoning.generate_random_zoning(water_map)
    
    network = RoadNetwork(width, height)
    network.generate_organic_network(heightmap, water_map)

    placer = BuildingPlacer(width, height)
    placer.place_buildings_in_zones(zoning, network, heightmap, water_map)
    print(f"Buildings placed. Total buildings: {len(placer.buildings)}")