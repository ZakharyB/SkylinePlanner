class CityLimits:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    
    def is_within_limits(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

if __name__ == "__main__":
    # Test the CityLimits class
    city = CityLimits(100, 100)
    print(f"Is (50, 50) within limits? {city.is_within_limits(50, 50)}")
    print(f"Is (150, 150) within limits? {city.is_within_limits(150, 150)}")