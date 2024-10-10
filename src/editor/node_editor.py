import tkinter as tk
import logging
from src.editor.node import Node, Connection
from src.editor.nodes.terrain_node import TerrainNode
from src.editor.nodes.water_node import WaterNode
from src.editor.nodes.road_node import RoadNode
from src.editor.nodes.zoning_node import ZoningNode
from src.editor.nodes.city_node import CityNode
from ui.tooltip import Tooltip
from functools import lru_cache

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.info("Message")
logging.error("Error message")
logging.warning("Warning message")



class NodeEditor:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, bg='#2C2C2C')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.nodes = []
        self.connections = []
        self.dragging = False
        self.dragged_node = None
        self.connecting = False
        self.connection_start = None
        self.connection_preview = None
        self.valid_connection = False
        self.selected_node = None
        self.sidebar = None 
        self.main_window = None

        self.zoom_factor = 1.0
        self.pan_start_x = 0
        self.pan_start_y = 0
        self.canvas_offset_x = 0  
        self.canvas_offset_y = 0  

        self.add_hover_effects()
        self.create_minimap()


        self.canvas.bind("<Configure>", lambda e: self.draw_grid())


        self.canvas.bind('<Button-1>', self.on_click)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.canvas.bind('<Button-3>', self.on_right_click)
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)
        self.canvas.bind('<Button-2>', self.start_pan)
        self.canvas.bind('<B2-Motion>', self.pan)

        self.draw_grid()

    @lru_cache(maxsize=1000)
    def get_port_coords(self, node, port_type, index):
        port_id = node.input_ids[index] if port_type.startswith('input') else node.output_ids[index]
        return self.canvas.coords(port_id)

 
    def clear_all(self):
        self.canvas.delete("all")
        self.nodes = []
        self.connections = []
        self.draw_grid()

    def load_from_data(self, data):
        self.clear_all()
        for node_data in data['nodes']:
            node = self.create_node_from_data(node_data)
            self.add_node(node)
        for conn_data in data['connections']:
            self.create_connection_from_data(conn_data)

    def create_node_from_data(self, node_data):
        # Create a node based on the type and data
        node_type = node_data['type']
        if node_type == "Terrain":
            node = TerrainNode()
        elif node_type == "Water":
            node = WaterNode()
        # ... (add other node types)
        else:
            raise ValueError(f"Unknown node type: {node_type}")
        
        node.pos = tuple(node_data['position'])
        node.config = node_data['config']
        return node

    def create_connection_from_data(self, conn_data):
        output_node = next(node for node in self.nodes if node.id == conn_data['output_node_id'])
        input_node = next(node for node in self.nodes if node.id == conn_data['input_node_id'])
        self.create_connection(
            (output_node.output_ids[conn_data['output_index']], output_node.title, f"output_{conn_data['output_index']}"),
            (input_node.input_ids[conn_data['input_index']], input_node.title, f"input_{conn_data['input_index']}")
        )

    def save_to_data(self):
        return {
            'nodes': [self.node_to_data(node) for node in self.nodes],
            'connections': [self.connection_to_data(conn) for conn in self.connections]
        }

    def node_to_data(self, node):
        return {
            'id': node.id,
            'type': node.__class__.__name__,
            'position': list(node.pos),
            'config': node.config
        }

    def connection_to_data(self, connection):
        return {
            'output_node_id': connection.output_node.id,
            'output_index': connection.output_index,
            'input_node_id': connection.input_node.id,
            'input_index': connection.input_index
        }

    def export_data(self):
        # This method could be more complex, generating the final city data
        return self.save_to_data()
    
    def add_hover_effects(self):
        self.canvas.tag_bind('node', '<Enter>', self.on_node_hover)
        self.canvas.tag_bind('node', '<Leave>', self.on_node_leave)
        self.canvas.tag_bind('port', '<Enter>', self.on_port_hover)
        self.canvas.tag_bind('port', '<Leave>', self.on_port_leave)
        self.canvas.tag_bind('connection', '<Enter>', self.on_connection_hover)
        self.canvas.tag_bind('connection', '<Leave>', self.on_connection_leave)

    def on_node_hover(self, event):
        item = self.canvas.find_withtag('current')[0]
        self.canvas.itemconfig(item, fill='#4C4F51')

    def on_node_leave(self, event):
        item = self.canvas.find_withtag('current')[0]
        self.canvas.itemconfig(item, fill='#3C3F41')

    def on_port_hover(self, event):
        item = self.canvas.find_withtag('current')[0]
        self.canvas.itemconfig(item, width=3)

    def on_port_leave(self, event):
        item = self.canvas.find_withtag('current')[0]
        self.canvas.itemconfig(item, width=2)

    def on_connection_hover(self, event):
        item = self.canvas.find_withtag('current')[0]
        self.canvas.itemconfig(item, width=3, fill='#FFD700')

    def on_connection_leave(self, event):
        item = self.canvas.find_withtag('current')[0]
        self.canvas.itemconfig(item, width=2, fill='#D4D4D4')

    def add_node(self, node_type):
        if node_type == "Terrain":
            node = TerrainNode()
        elif node_type == "Water":
            node = WaterNode()
        elif node_type == "Roads":
            node = RoadNode()
        elif node_type == "Zoning":
            node = ZoningNode()
        elif node_type == "City":
            node = CityNode()
        else:
            raise ValueError(f"Unknown node type: {node_type}")
        
        self.main_window.unsaved_changes = True

        # Set initial position in canvas coordinates
        max_ports = max(len(node.inputs), len(node.outputs))
        min_height = 100  # Minimum height of the node
        height = max(min_height, 20 + max_ports * 20)  # 20px for title, 20px per port
        node.size = (150, height)  # Adjust width as needed

        # Set initial position in canvas coordinates
        canvas_x = len(self.nodes) * 170 + 50 + self.canvas_offset_x  # Increased spacing between nodes
        canvas_y = 50 + self.canvas_offset_y
        node.pos = self.canvas_to_node_coords(canvas_x, canvas_y)
        
        self.main_window.update_status(f"Added {node.title} node")
        self.main_window.notification_manager.show_notification(f"Added {node.title} node", type='info')

        self.nodes.append(node)
        self.draw_node(node)

    def draw_node(self, node):
        x, y = self.node_to_canvas_coords(*node.pos)
        w, h = node.size
        corner_radius = 10

        # Helper function to create rounded corners
        def create_rounded_rectangle(x1, y1, x2, y2, radius):
            points = [
                x1+radius, y1,
                x1+radius, y1,
                x2-radius, y1,
                x2-radius, y1,
                x2, y1,
                x2, y1+radius,
                x2, y1+radius,
                x2, y2-radius,
                x2, y2-radius,
                x2, y2,
                x2-radius, y2,
                x2-radius, y2,
                x1+radius, y2,
                x1+radius, y2,
                x1, y2,
                x1, y2-radius,
                x1, y2-radius,
                x1, y1+radius,
                x1, y1+radius,
                x1, y1
            ]
            return points

        # Create main node rectangle with rounded corners
    #    node.canvas_id = self.canvas.create_polygon(
        #    create_rounded_rectangle(x, y, x+w, y+h, corner_radius),
        #    fill='#3C3F41', outline='#5E6060', width=2, tags=(node.title, 'node')
      #  )

        # Create main node rectangle and title bar with a single polygon
        points = create_rounded_rectangle(x, y, x+w, y+h, corner_radius)
        node.canvas_id = self.canvas.create_polygon(
        points,
        fill='#3C3F41', outline='#5E6060', width=2, tags=(node.title, 'node')
        )

        # Create title bar with rounded top corners
        title_height = 20
        self.canvas.create_text(x+w/2, y+title_height/2, text=node.title, fill='white', font=('Arial', 10, 'bold'), tags=(node.title, 'node'))

       # title_height = 20
   #     self.canvas.create_polygon(
       #     create_rounded_rectangle(x, y, x+w, y+title_height, corner_radius),
    #        fill='#4A4A4A', outline='#5E6060', tags=(node.title, 'node')
   #     )
        self.canvas.create_text(x+w/2, y+title_height/2, text=node.title, fill='white', font=('Arial', 10, 'bold'), tags=(node.title, 'node'))

        # Calculate spacing for input and output ports
        input_spacing = (h - title_height) / (len(node.inputs) + 1)
        output_spacing = (h - title_height) / (len(node.outputs) + 1)

        # Draw input ports
        for i, input_name in enumerate(node.inputs):
            iy = y + title_height + (i + 1) * input_spacing
            input_id = self.canvas.create_oval(x-6, iy-6, x+6, iy+6, fill='#6A9955', outline='#4EC9B0', width=2, tags=(node.title, f'input_{i}', 'port'))
            self.canvas.create_text(x+15, iy, text=input_name, fill='#D4D4D4', anchor='w', font=('Arial', 8), tags=(node.title, 'node'))
            node.input_ids.append(input_id)
            Tooltip(self.canvas, f"Input: {input_name}", canvas_item=input_id)

        # Draw output ports
        for i, output_name in enumerate(node.outputs):
            oy = y + title_height + (i + 1) * output_spacing
            output_id = self.canvas.create_oval(x+w-6, oy-6, x+w+6, oy+6, fill='#D16969', outline='#CE9178', width=2, tags=(node.title, f'output_{i}', 'port'))
            self.canvas.create_text(x+w-15, oy, text=output_name, fill='#D4D4D4', anchor='e', font=('Arial', 8), tags=(node.title, 'node'))
            node.output_ids.append(output_id)
            Tooltip(self.canvas, f"Output: {output_name}", canvas_item=output_id)

    def on_click(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(canvas_x, canvas_y)[0]
        tags = self.canvas.gettags(item)
        
        if not self.connecting:
            self.select_node(event)

        if 'port' in tags:
            port_type = next((tag for tag in tags if tag.startswith('input_') or tag.startswith('output_')), None)
            if port_type:
                if port_type.startswith('output_'):
                    self.connecting = True
                    self.connection_start = (item, tags[0], port_type)
                else:
                    connected_output = self.find_connected_output(item)
                    if connected_output:
                        self.connecting = True
                        self.connection_start = connected_output
                        self.remove_connection_to_input(item)
        elif 'node' in tags:
            for node in self.nodes:
                if node.title in tags:
                    self.select_node(event)
                    self.dragging = True
                    self.dragged_node = node
                    self.drag_start = (canvas_x, canvas_y)
        else:
            self.select_node(event)

    def select_node(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(canvas_x, canvas_y)[0]
        tags = self.canvas.gettags(item)
        
        print(f"Clicked item: {item}, Tags: {tags}")  # Debug print

        if 'node' in tags:
            for node in self.nodes:
                if node.title in tags:
                    self.selected_node = node
                    print(f"Selected node: {node.title}")  # Debug print
                    if self.sidebar:
                        print("Showing config in sidebar")  # Debug print
                        self.sidebar.show_config(node)
                    else:
                        print("Sidebar not initialized")  # Debug print
                    break
        else:
            self.selected_node = None
            if self.sidebar:
                print("Clearing sidebar config")  # Debug print
                self.sidebar.clear_config()
            else:
                print("Sidebar not initialized")  # Debug print

    def update_node(self, node):
        # Trigger a re-draw of the node (if needed)
        self.draw_node(node)
        # Update connections
        self.update_connections()
        # Trigger processing of downstream nodes
        self.process_downstream(node)

    def process_downstream(self, start_node):
        visited = set()
        queue = [start_node]

        while queue:
            current_node = queue.pop(0)
            if current_node in visited:
                continue

            visited.add(current_node)
            current_node.process()

            # Find all nodes that depend on the current node
            for connection in self.connections:
                if connection.output_node == current_node:
                    queue.append(connection.input_node)

    def on_drag(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        if self.dragging and self.dragged_node:
            dx = canvas_x - self.drag_start[0]
            dy = canvas_y - self.drag_start[1]
            
            # Move all elements of the node together
            self.canvas.move(self.dragged_node.title, dx, dy)
            
            self.drag_start = (canvas_x, canvas_y)
            self.dragged_node.pos = (self.dragged_node.pos[0] + dx / self.zoom_factor, 
                                    self.dragged_node.pos[1] + dy / self.zoom_factor)
            
            self.update_connections_for_node(self.dragged_node)
        elif self.connecting:
            self.update_connection_preview(canvas_x, canvas_y)


            

    def update_connections_for_node(self, node):
        for connection in self.connections:
            if connection.input_node == node or connection.output_node == node:
                self.update_single_connection(connection)

    def update_single_connection(self, connection):
        output_coords = self.canvas.coords(connection.output_node.output_ids[connection.output_index])
        input_coords = self.canvas.coords(connection.input_node.input_ids[connection.input_index])
        
        cx1 = output_coords[0] + (input_coords[0] - output_coords[0]) * 0.5
        cy1 = output_coords[1]
        cx2 = input_coords[0] - (input_coords[0] - output_coords[0]) * 0.5
        cy2 = input_coords[1]
        
        self.canvas.coords(
            connection.line_id,
            output_coords[0], output_coords[1],
            cx1, cy1, cx2, cy2,
            input_coords[0], input_coords[1]
        )

    def update_connection_preview(self, x, y):
        start_coords = self.canvas.coords(self.connection_start[0])
        if self.connection_preview:
            self.canvas.coords(self.connection_preview, start_coords[0], start_coords[1], x, y)
        else:
            self.connection_preview = self.canvas.create_line(
                start_coords[0], start_coords[1], x, y,
                fill='#D4D4D4', width=2, smooth=True, tags='temp_connection'
            )
        
        # Check if the current position is over a valid port
        item = self.canvas.find_closest(x, y)[0]
        tags = self.canvas.gettags(item)
        self.valid_connection = 'port' in tags and self.is_valid_connection(self.connection_start[2], tags)
        
        # Update preview line color based on validity
        color = '#00FF00' if self.valid_connection else '#FF0000'
        self.canvas.itemconfig(self.connection_preview, fill=color)

    def is_valid_connection(self, start_port_type, end_tags):
        if start_port_type.startswith('output_'):
            return any(tag.startswith('input_') for tag in end_tags)
        elif start_port_type.startswith('input_'):
            return any(tag.startswith('output_') for tag in end_tags)
        return False

    def on_release(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        if self.dragging:
            self.dragging = False
            self.dragged_node = None
        elif self.connecting:
            if self.valid_connection:
                item = self.canvas.find_closest(canvas_x, canvas_y)[0]
                tags = self.canvas.gettags(item)
                port_type = next((tag for tag in tags if tag.startswith('input_') or tag.startswith('output_')), None)
                if port_type:
                    self.create_connection(self.connection_start, (item, tags[0], port_type))
            
            self.connecting = False
            self.connection_start = None
            self.canvas.delete('temp_connection')
            self.connection_preview = None
            self.valid_connection = False

    def on_right_click(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(canvas_x, canvas_y)[0]
        tags = self.canvas.gettags(item)

        if 'connection' in tags:
            self.remove_connection(item)
        elif 'node' in tags:
            for node in self.nodes:
                if node.title in tags:
                    self.remove_node(node)
                    break

    def create_connection(self, start, end):
        try:
            start_node = next(node for node in self.nodes if node.title == start[1])
            end_node = next(node for node in self.nodes if node.title == end[1])
            
            if start[2].startswith('output_') and end[2].startswith('input_'):
                output_node, input_node = start_node, end_node
                output_index = int(start[2].split('_')[1])
                input_index = int(end[2].split('_')[1])
            elif start[2].startswith('input_') and end[2].startswith('output_'):
                output_node, input_node = end_node, start_node
                output_index = int(end[2].split('_')[1])
                input_index = int(start[2].split('_')[1])
            else:
                raise ValueError("Invalid connection: Both ports must be of different types (input/output)")
            
            # Check if the input port already has a connection
            existing_connection = next((c for c in self.connections 
                                        if c.input_node == input_node and c.input_index == input_index), None)
            if existing_connection:
                self.remove_connection(existing_connection.line_id)
            
            self.main_window.unsaved_changes = True
            connection = Connection(output_node, output_index, input_node, input_index)
            self.connections.append(connection)
            self.draw_connection(connection)
        except StopIteration:
            print("Error: Could not find start or end node for connection")
        except ValueError as e:
            print(f"Error creating connection: {e}")
        except Exception as e:
            print(f"Unexpected error creating connection: {e}")

    def draw_connection(self, connection):
        try:
            output_coords = self.canvas.coords(connection.output_node.output_ids[connection.output_index])
            input_coords = self.canvas.coords(connection.input_node.input_ids[connection.input_index])
            
            # Calculate control points for the bezier curve
            cx1 = output_coords[0] + (input_coords[0] - output_coords[0]) * 0.5
            cy1 = output_coords[1]
            cx2 = input_coords[0] - (input_coords[0] - output_coords[0]) * 0.5
            cy2 = input_coords[1]
            
            connection.line_id = self.canvas.create_line(
                output_coords[0], output_coords[1],
                cx1, cy1, cx2, cy2,
                input_coords[0], input_coords[1],
                smooth=True, width=2, fill='#D4D4D4', tags='connection',
                splinesteps=50
            )
        except IndexError:
            print("Error: Invalid port index when drawing connection")
        except Exception as e:
            print(f"Unexpected error drawing connection: {e}")

    def update_connections(self):
        for connection in self.connections:
            output_coords = self.get_port_coords(connection.output_node, 'output', connection.output_index)
            input_coords = self.get_port_coords(connection.input_node, 'input', connection.input_index)
            
            cx1 = output_coords[0] + (input_coords[0] - output_coords[0]) * 0.5
            cy1 = output_coords[1]
            cx2 = input_coords[0] - (input_coords[0] - output_coords[0]) * 0.5
            cy2 = input_coords[1]
            
            self.canvas.coords(
                connection.line_id,
                output_coords[0], output_coords[1],
                cx1, cy1, cx2, cy2,
                input_coords[0], input_coords[1]
            )
   # except Exception as e:
       # logging.error(f"Error updating connection: {e}")

    def remove_connection(self, line_id):
        connection = next((c for c in self.connections if c.line_id == line_id), None)
        if connection:
            self.connections.remove(connection)
            self.canvas.delete(line_id)
            self.main_window.unsaved_changes = True

    def remove_node(self, node):
        # Remove all connections associated with this node
        connections_to_remove = [c for c in self.connections if c.input_node == node or c.output_node == node]
        for connection in connections_to_remove:
            self.remove_connection(connection.line_id)



        self.main_window.update_status(f"Removed {node.title} node")
        self.main_window.notification_manager.show_notification(f"Removed {node.title} node", type='info')
        
        # Remove the node from the list and delete its canvas items
        self.main_window.unsaved_changes = True
        self.nodes.remove(node)
        self.canvas.delete(node.title)

        for port_type in ['input', 'output']:
            for i in range(len(node.inputs if port_type == 'input' else node.outputs)):
                self.get_port_coords.cache_clear()

    def remove_connection_to_input(self, input_port_id):
        connection = next((c for c in self.connections if c.input_node.input_ids[c.input_index] == input_port_id), None)
        if connection:
            self.remove_connection(connection.line_id)

    def find_connected_output(self, input_port_id):
        connection = next((c for c in self.connections if c.input_node.input_ids[c.input_index] == input_port_id), None)
        if connection:
            output_node = connection.output_node
            output_port_id = output_node.output_ids[connection.output_index]
            return (output_port_id, output_node.title, f'output_{connection.output_index}')
        return None

    def draw_grid(self):
        grid_size = 20
        for x in range(0, self.canvas.winfo_width(), grid_size):
            self.canvas.create_line(x, 0, x, self.canvas.winfo_height(), fill="#3A3A3A")
        for y in range(0, self.canvas.winfo_height(), grid_size):
            self.canvas.create_line(0, y, self.canvas.winfo_width(), y, fill="#3A3A3A")

    def create_minimap(self):
        self.minimap = tk.Canvas(self.master, width=150, height=150, bg='#1E1E1E')
        self.minimap.place(relx=1, rely=1, anchor='se')
        self.update_minimap()

    def update_minimap(self):
        self.minimap.delete('all')
        scale = min(150 / self.canvas.winfo_width(), 150 / self.canvas.winfo_height())
        for node in self.nodes:
            x, y = node.pos
            w, h = node.size
            self.minimap.create_rectangle(x*scale, y*scale, (x+w)*scale, (y+h)*scale, fill='#3C3F41', outline='#5E6060')
        self.minimap.after(100, self.update_minimap)

    def zoom(self, event):
        if event.delta > 0:
            self.canvas.scale('all', event.x, event.y, 1.1, 1.1)
        elif event.delta < 0:
            self.canvas.scale('all', event.x, event.y, 0.9, 0.9)
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def on_mousewheel(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        
        # Store old scale for calculating offset
        old_scale = self.zoom_factor
        
        # Zoom
        if event.delta > 0:
            self.zoom_factor *= 1.1
        else:
            self.zoom_factor /= 1.1
        
        # Calculate offset to keep the point under the cursor in the same place
        self.canvas_offset_x += (canvas_x - self.canvas_offset_x) * (1 - old_scale / self.zoom_factor)
        self.canvas_offset_y += (canvas_y - self.canvas_offset_y) * (1 - old_scale / self.zoom_factor)
        
        # Apply zoom
        self.canvas.scale('all', canvas_x, canvas_y, self.zoom_factor / old_scale, self.zoom_factor / old_scale)
        
        # Update scroll region
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def start_pan(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def pan(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)
        self.canvas_offset_x = self.canvas.canvasx(0)
        self.canvas_offset_y = self.canvas.canvasy(0)
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))

    def canvas_to_node_coords(self, x, y):
        return ((x - self.canvas_offset_x) / self.zoom_factor, 
                (y - self.canvas_offset_y) / self.zoom_factor)

    def node_to_canvas_coords(self, x, y):
        return (x * self.zoom_factor + self.canvas_offset_x, 
                y * self.zoom_factor + self.canvas_offset_y)
    
    def process_nodes(self):
        sorted_nodes = self.topological_sort()
        for node in sorted_nodes:
            inputs = {}
            for connection in self.connections:
                if connection.input_node == node:
                    input_name = node.inputs[connection.input_index]
                    output_name = connection.output_node.outputs[connection.output_index]
                    inputs[input_name] = connection.output_node.output_data.get(output_name)
            
            node.output_data = node.process(**inputs)

    def topological_sort(self):
        sorted_nodes = []
        temp_marks = set()
        perm_marks = set()

        def visit(node):
            if node in perm_marks:
                return
            if node in temp_marks:
                raise ValueError("Graph is not a DAG")
            
            temp_marks.add(node)
            
            for connection in self.connections:
                if connection.output_node == node:
                    visit(connection.input_node)
            
            temp_marks.remove(node)
            perm_marks.add(node)
            sorted_nodes.insert(0, node)

        for node in self.nodes:
            if node not in perm_marks:
                visit(node)

        return sorted_nodes

    def generate_city(self):
        try:
            self.process_nodes()
            city_node = next((node for node in self.nodes if isinstance(node, CityNode)), None)
            if city_node and 'city_data' in city_node.output_data:
                city_data = city_node.output_data['city_data']
                from src.visualization.city_visualizer import CityVisualizer
                CityVisualizer.visualize_city(city_data)
            else:
                print("City data not found. Make sure you have a City node connected properly.")
        except Exception as e:
            print(f"An error occurred while generating the city: {str(e)}")