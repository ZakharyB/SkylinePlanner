import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
import json
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.editor.node_editor import NodeEditor
from src.editor.nodes.terrain_node import TerrainNode
from src.editor.nodes.water_node import WaterNode
from src.editor.nodes.road_node import RoadNode
from src.editor.nodes.zoning_node import ZoningNode
from src.editor.nodes.city_node import CityNode
from src.file_handlers.cityplan_handler import CityPlanHandler
from notifications import NotificationManager
from node_config_sidebar import NodeConfigSidebar

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.style = ttk.Style()
        self.master.title("City Generator")
        self.master.geometry("1920x1080")  
        self.master.configure(bg='#2C2C2C')
        self.current_file = None
        self.unsaved_changes = False 
        self.undo_stack = []
        self.redo_stack = []

        # Create main container
        self.main_container = tk.PanedWindow(self.master, orient=tk.HORIZONTAL, sashwidth=5, bg='#2C2C2C')
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Left panel (for toolbar and node editor)
        self.left_panel = tk.Frame(self.main_container, bg='#2C2C2C')
        self.main_container.add(self.left_panel, width=1600)

        # Right panel (for sidebar)
        self.right_panel = tk.Frame(self.main_container, bg='#3C3F41', width=350)
        self.main_container.add(self.right_panel)

        self.notification_manager = NotificationManager(self.left_panel)

        key = os.environ.get('CITYPLAN_KEY')
        try:
            self.cityplan_handler = CityPlanHandler(key)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid encryption key: {str(e)}")
            self.cityplan_handler = None

        self.create_toolbar()

        # Create a container for NodeEditor
        self.node_editor_container = tk.Frame(self.left_panel)
        self.node_editor_container.pack(fill=tk.BOTH, expand=True)

        # Create NodeEditor inside the container
        self.node_editor = NodeEditor(self.node_editor_container)
        self.node_editor.main_window = self

        # Sidebar
     #   self.sidebar = NodeConfigSidebar(self.right_panel, self.node_editor)
     #   self.sidebar.pack(fill=tk.BOTH, expand=True)
      #  self.node_editor.sidebar = self.sidebar

        self.sidebar = NodeConfigSidebar(self.right_panel, self.node_editor)
        self.node_editor.sidebar = self.sidebar

        # Status bar
        self.status_bar = tk.Frame(self.master, relief=tk.SUNKEN, bd=1, bg='#3C3F41')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(self.status_bar, text="Ready", anchor=tk.W, bg='#3C3F41', fg='white')
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.file_label = tk.Label(self.status_bar, text="No file opened", anchor=tk.E, bg='#3C3F41', fg='white')
        self.file_label.pack(side=tk.RIGHT, padx=5)

        self.generate_button = tk.Button(master, text="Generate City", command=self.generate_city)
        self.generate_button.pack()

        self.create_menu()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        # Main container
        self.main_container = tk.PanedWindow(self.master, orient=tk.HORIZONTAL, sashwidth=5, bg='#2C2C2C')
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Left panel (Node Editor)
        self.left_panel = tk.Frame(self.main_container, bg='#2C2C2C')
        self.main_container.add(self.left_panel, width=1000)

        # Right panel (Sidebar)
        self.right_panel = tk.Frame(self.main_container, bg='#3C3F41', width=400)
        self.main_container.add(self.right_panel)

        # Node Editor
        self.node_editor = NodeEditor(self.left_panel)
        self.node_editor.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self.sidebar = NodeConfigSidebar(self.right_panel, self.node_editor)
        self.sidebar.pack(fill=tk.BOTH, expand=True)

        # Connect node editor and sidebar
        self.node_editor.sidebar = self.sidebar
        self.node_editor.main_window = self

        # Notification manager
        self.notification_manager = NotificationManager(self.master)

        # Status bar
        self.status_bar = tk.Frame(self.master, relief=tk.SUNKEN, bd=1, bg='#3C3F41')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(self.status_bar, text="Ready", anchor=tk.W, bg='#3C3F41', fg='white')
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.file_label = tk.Label(self.status_bar, text="No file opened", anchor=tk.E, bg='#3C3F41', fg='white')
        self.file_label.pack(side=tk.RIGHT, padx=5)

        # CityPlan Handler
        key = os.environ.get('CITYPLAN_KEY')
        try:
            self.cityplan_handler = CityPlanHandler(key)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid encryption key: {str(e)}")
            self.cityplan_handler = None

    def create_menu(self):
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_project)
        file_menu.add_command(label="Open", command=self.open_project)
        file_menu.add_command(label="Save", command=self.save_project)
        file_menu.add_command(label="Save As", command=self.save_project_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export", command=self.export_project)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_closing)

    def create_toolbar(self):
        toolbar = tk.Frame(self.left_panel, bg='#2C2C2C', width=250)
        toolbar.pack(side=tk.LEFT, fill=tk.Y)
        toolbar.pack_propagate(False)

        # Search bar
        search_frame = tk.Frame(toolbar, bg='#2C2C2C')
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        search_entry = tk.Entry(search_frame, bg='#3C3F41', fg='white', insertbackground='white')
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        search_button = ttk.Button(search_frame, text="🔍")
        search_button.pack(side=tk.RIGHT)

        # Categories and nodes
        categories = {
            "Terrain": ["Terrain", "Water", "Elevation", "Biomes"],
            "City": ["Roads", "Zoning", "Buildings", "Parks", "City"],
            "Infrastructure": ["Power", "Water Supply", "Sewage", "Public Transport"],
            "Economy": ["Industry", "Commercial", "Residential", "Tourism"]
        }

        category_frames = {}
        for category, nodes in categories.items():
            category_frame = tk.LabelFrame(toolbar, text=category, bg='#2C2C2C', fg='white')
            category_frame.pack(fill=tk.X, padx=10, pady=5)
            category_frames[category] = category_frame

            for node in nodes:
                node_button = ttk.Button(category_frame, text=node, command=lambda n=node: self.add_node(n))
                node_button.pack(fill=tk.X, padx=2, pady=2)

        # Additional features
        features_frame = tk.LabelFrame(toolbar, text="Features", bg='#2C2C2C', fg='white')
        features_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(features_frame, text="Undo", command=self.undo).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(features_frame, text="Redo", command=self.redo).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(features_frame, text="Zoom In", command=self.zoom_in).pack(fill=tk.X, padx=2, pady=2)
        ttk.Button(features_frame, text="Zoom Out", command=self.zoom_out).pack(fill=tk.X, padx=2, pady=2)

        generate_button = ttk.Button(toolbar, text="Generate City", command=self.generate_city)
        generate_button.pack(fill=tk.X, padx=10, pady=10)

        # Apply custom style
        self.style.configure('TButton', background='#3C3F41', foreground='white')
        self.style.map('TButton', background=[('active', '#4C4F51')])


    def add_node(self, node_type):
        if node_type == "Terrain":
            self.add_terrain_node()
            self.save_state()
        elif node_type == "Water":
            self.add_water_node()
            self.save_state()
        elif node_type == "Roads":
            self.add_road_node()
            self.save_state()
        elif node_type == "Zoning":
            self.add_zoning_node()
            self.save_state()
        elif node_type == "City":
            self.add_city_node()
            self.save_state()


    def undo(self):
        if not self.undo_stack:
            return
        
        current_state = {
            'nodes': [node.to_dict() for node in self.nodes],
            'connections': [conn.to_dict() for conn in self.connections]
        }
        self.redo_stack.append(current_state)
        
        previous_state = self.undo_stack.pop()
        self.load_from_data(previous_state)
        self.node_editor.undo()
        self.notification_manager.show_notification("Undo action performed", type='info')

    def redo(self):
        if not self.redo_stack:
            return
        
        next_state = self.redo_stack.pop()
        
        current_state = {
            'nodes': [node.to_dict() for node in self.nodes],
            'connections': [conn.to_dict() for conn in self.connections]
        }
        self.undo_stack.append(current_state)
        
        self.load_from_data(next_state)
        self.node_editor.redo()
        self.notification_manager.show_notification("Redo action performed", type='info')

    def zoom_in(self):
        # Implement zoom in functionality
        pass

    def zoom_out(self):
        # Implement zoom out functionality
        pass

    def new_project(self):
        if self.unsaved_changes and not self.prompt_save():
            return
        
        self.notification_manager.show_notification("New project created", type='success')
        self.update_status("New project created")
        self.node_editor.clear_all()
        self.current_file = None
        self.unsaved_changes = False

    def open_project(self):
        if self.cityplan_handler is None:
            messagebox.showerror("Error", "Encryption is not properly set up")
            return

        if self.unsaved_changes and not self.prompt_save():
            return

        filetypes = [
            ("City Plan files", "*.cityplan"),
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(filetypes=filetypes)
        if filename:
            try:
                if filename.endswith('.cityplan'):
                    data = self.cityplan_handler.load(filename)
                else:
                    data = self.cityplan_handler.import_from_json(filename)
                self.node_editor.load_from_data(data)
                self.current_file = filename
                self.unsaved_changes = False
                self.notification_manager.show_notification(f"Project opened: {filename}", type='info')
                self.update_status(f"Opened: {filename}")
                self.update_file_label(filename)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {str(e)}")

    def save_project(self):
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_project_as()

    def save_project_as(self):
        filetypes = [
            ("City Plan files", "*.cityplan"),
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
        filename = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=".cityplan")
        if filename:
            self.save_to_file(filename)
            self.current_file = filename

    def save_to_file(self, filename):
        if self.cityplan_handler is None:
            messagebox.showerror("Error", "Encryption is not properly set up")
            return

        try:
            data = self.node_editor.save_to_data()
            if filename.endswith('.cityplan'):
                self.cityplan_handler.save(data, filename)
            else:
                self.cityplan_handler.export_to_json(data, filename)
            self.unsaved_changes = False
            self.notification_manager.show_notification("Project saved successfully", type='success')
            self.update_status("Project saved")
            self.update_file_label(filename)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save project: {str(e)}")

    def export_project(self):
        filetypes = [
            ("JSON files", "*.json"),
            ("All files", "*.*")
        ]
        filename = filedialog.asksaveasfilename(filetypes=filetypes, defaultextension=".json")
        if filename:
            try:
                data = self.node_editor.export_data()
                with open(filename, 'w') as file:
                    json.dump(data, file, indent=2)
                self.notification_manager.show_notification("Project exported successfully", type='success')
                self.update_status("Project exported")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export file: {str(e)}")

    def update_status(self, message):
        self.status_label.config(text=message)

    def update_file_label(self, filename):
        self.file_label.config(text=f"File: {os.path.basename(filename)}")

    def prompt_save(self):
        response = messagebox.askyesnocancel("Unsaved Changes", "Do you want to save your changes?")
        if response is None:  # Cancel
            return False
        elif response:  # Yes
            self.save_project()
        return True  # Continue with the operation

    def save_state(self):
        state = {
            'nodes': [node.to_dict() for node in self.nodes],
            'connections': [conn.to_dict() for conn in self.connections]
        }
        self.undo_stack.append(state)
        self.redo_stack.clear()

    def on_closing(self):
        if self.unsaved_changes:
            response = messagebox.askyesnocancel("Unsaved Changes", "You have unsaved changes. Do you want to save before exiting?")
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self.save_project()
                if self.unsaved_changes:  # If save was cancelled or failed
                    return
        self.master.destroy()

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

    def check_all_nodes_connected(self):
        return self.node_editor.check_all_nodes_connected()


    def generate_city(self):
        if self.check_all_nodes_connected():
            self.node_editor.generate_city()
        else:
            messagebox.showwarning("Incomplete Setup", "Please ensure all nodes are properly connected before generating the city.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()