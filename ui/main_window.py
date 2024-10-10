import tkinter as tk
from tkinter import ttk
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.editor.node_editor import NodeEditor
from src.editor.node_editor import NodeEditor
from src.editor.nodes.terrain_node import TerrainNode
from src.editor.nodes.water_node import WaterNode
from src.editor.nodes.road_node import RoadNode
from src.editor.nodes.zoning_node import ZoningNode
from src.editor.nodes.city_node import CityNode

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("City Generator")
        self.master.geometry("1024x768")
        self.master.configure(bg='#2C2C2C')

        self.node_editor = NodeEditor(self.master)

        self.create_menu()
        self.create_toolbar()


    def create_menu(self):
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Save")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

    def create_toolbar(self):
        toolbar = ttk.Notebook(self.master)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        terrain_frame = ttk.Frame(toolbar)
        city_frame = ttk.Frame(toolbar)

        toolbar.add(terrain_frame, text="Terrain")
        toolbar.add(city_frame, text="City")

        ttk.Button(terrain_frame, text="Terrain", command=self.add_terrain_node).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(terrain_frame, text="Water", command=self.add_water_node).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Button(city_frame, text="Roads", command=self.add_road_node).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(city_frame, text="Zoning", command=self.add_zoning_node).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(city_frame, text="City", command=self.add_city_node).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(city_frame, text="Generate", command=self.generate_city).pack(side=tk.LEFT, padx=5, pady=5)



    def add_terrain_node(self):
        self.node_editor.add_node("Terrain")

    def add_water_node(self):
        self.node_editor.add_node("Water")

    def add_road_node(self):
        self.node_editor.add_node("Roads")

    def add_zoning_node(self):
        self.node_editor.add_node("Zoning")

    def add_city_node(self):
        self.node_editor.add_node("City")



    def generate_city(self):
        self.node_editor.generate_city()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()