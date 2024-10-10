import tkinter as tk
from tkinter import ttk
from tkinter.font import Font
from tkinter import filedialog, messagebox
import json
from notifications import NotificationManager
from node_config_sidebar import NodeConfigSidebar
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
from src.file_handlers.cityplan_handler import CityPlanHandler

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.style = ttk.Style()
        self.master.title("City Generator")
        self.master.geometry("1024x768")
        self.master.configure(bg='#2C2C2C')
        self.current_file = None
        self.unsaved_changes = False  # Add this line


        # Create main frame
        self.main_frame = tk.Frame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.notification_manager = NotificationManager(self.main_frame)

        key = os.environ.get('CITYPLAN_KEY')
        try:
            self.cityplan_handler = CityPlanHandler(key)
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid encryption key: {str(e)}")
            self.cityplan_handler = None

        self.node_editor = NodeEditor(self.main_frame)
        self.node_editor.main_window = self
        #self.node_editor = NodeEditor(self.main_frame)
        #self.node_editor.pack(fill=tk.BOTH, expand=True)

        self.sidebar = NodeConfigSidebar(self.master, self.node_editor)
        self.node_editor.sidebar = self.sidebar

        self.status_bar = tk.Frame(self.master, relief=tk.SUNKEN, bd=1)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(self.status_bar, text="Ready", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.file_label = tk.Label(self.status_bar, text="No file opened", anchor=tk.E)
        self.file_label.pack(side=tk.RIGHT, padx=5)

        self.create_menu()
        self.create_toolbar()

        self.sidebar.show()

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)


        
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

    def new_project(self):
        if self.unsaved_changes:
            if not self.prompt_save():
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

        if self.unsaved_changes:
            if not self.prompt_save():
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
            self.notification_manager.show_notification("Project saved successfully", type='success')
            self.update_status("Project saved")
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
            messagebox.showinfo("Success", "Project saved successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

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
                messagebox.showinfo("Success", "Project exported successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export file: {str(e)}")

    def update_status(self, message):
        self.status_label.config(text=message)

    def update_file_label(self, filename):
        self.file_label.config(text=f"File: {filename}")

    def prompt_save(self):
        response = messagebox.askyesnocancel("Unsaved Changes", "Do you want to save your changes?")
        if response is None:  # Cancel
            return False
        elif response:  # Yes
            self.save_project()
        return True  # Continue with the operation

    def on_closing(self):
        if self.unsaved_changes:
            response = self.notification_manager.show_notification(
                "You have unsaved changes. Do you want to save before exiting?",
                type='warning'
            )
            if response is None:  # Cancel
                return
            elif response:  # Yes
                self.save_project()
                if self.unsaved_changes:  # If save was cancelled or failed
                    return
        self.master.destroy()

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