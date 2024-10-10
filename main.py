from src.city.city_generator import CityGenerator
from src.visualization.city_visualizer import CityVisualizer

def main():
    width, height = 256, 256

    # Generate the city
    generator = CityGenerator(width, height)
    generator.generate_city()
    city_data = generator.get_city_data()

    # Visualize the city
    CityVisualizer.visualize_city(city_data)

if __name__ == "__main__":
    main()