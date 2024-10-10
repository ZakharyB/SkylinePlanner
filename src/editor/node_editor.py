import tkinter as tk
from src.editor.node import Node, Connection
from src.editor.nodes.terrain_node import TerrainNode
from src.editor.nodes.water_node import WaterNode
from src.editor.nodes.road_node import RoadNode
from src.editor.nodes.zoning_node import ZoningNode
from src.editor.nodes.city_node import CityNode
from ui.tooltip import Tooltip

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
        
        # Set initial position in canvas coordinates
        canvas_x = len(self.nodes) * 120 + 50 + self.canvas_offset_x
        canvas_y = 50 + self.canvas_offset_y
        node.pos = self.canvas_to_node_coords(canvas_x, canvas_y)
        
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
        node.canvas_id = self.canvas.create_polygon(
            create_rounded_rectangle(x, y, x+w, y+h, corner_radius),
            fill='#3C3F41', outline='#5E6060', width=2, tags=(node.title, 'node')
        )

        # Create title bar with rounded top corners
        title_height = 20
        self.canvas.create_polygon(
            create_rounded_rectangle(x, y, x+w, y+title_height, corner_radius),
            fill='#4A4A4A', outline='#5E6060', tags=(node.title, 'node')
        )
        self.canvas.create_text(x+w/2, y+title_height/2, text=node.title, fill='white', font=('Arial', 10, 'bold'), tags=(node.title, 'node'))

        # Draw input and output ports
        for i, input_name in enumerate(node.inputs):
            iy = y + title_height + (i+1) * (h-title_height) / (len(node.inputs) + 1)
            input_id = self.canvas.create_oval(x-6, iy-6, x+6, iy+6, fill='#6A9955', outline='#4EC9B0', width=2, tags=(node.title, f'input_{i}', 'port'))
            self.canvas.create_text(x+15, iy, text=input_name, fill='#D4D4D4', anchor='w', font=('Arial', 8), tags=(node.title, 'node'))
            node.input_ids.append(input_id)

        for i, output_name in enumerate(node.outputs):
            oy = y + title_height + (i+1) * (h-title_height) / (len(node.outputs) + 1)
            output_id = self.canvas.create_oval(x+w-6, oy-6, x+w+6, oy+6, fill='#D16969', outline='#CE9178', width=2, tags=(node.title, f'output_{i}', 'port'))
            self.canvas.create_text(x+w-15, oy, text=output_name, fill='#D4D4D4', anchor='e', font=('Arial', 8), tags=(node.title, 'node'))
            node.output_ids.append(output_id)

        # Add tooltips for ports
        for i, input_name in enumerate(node.inputs):
            Tooltip(self.canvas, f"Input: {input_name}", canvas_item=input_id)

        for i, output_name in enumerate(node.outputs):
            Tooltip(self.canvas, f"Output: {output_name}", canvas_item=output_id)

    def on_click(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(canvas_x, canvas_y)[0]
        tags = self.canvas.gettags(item)
        
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
                    self.dragging = True
                    self.dragged_node = node
                    self.drag_start = (canvas_x, canvas_y)
                    break

    def on_drag(self, event):
        if self.dragging and self.dragged_node:
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            
            # Calculate the actual distance moved in canvas coordinates
            dx = (canvas_x - self.drag_start[0])
            dy = (canvas_y - self.drag_start[1])
            
            # Move the node
            self.canvas.move(self.dragged_node.title, dx, dy)
            self.drag_start = (canvas_x, canvas_y)
            
            # Update node position
            self.dragged_node.pos = (self.dragged_node.pos[0] + dx, self.dragged_node.pos[1] + dy)
            
            self.update_connections()
        elif self.connecting:
            self.canvas.delete('temp_connection')
            start_coords = self.canvas.coords(self.connection_start[0])
            canvas_x = self.canvas.canvasx(event.x)
            canvas_y = self.canvas.canvasy(event.y)
            self.canvas.create_line(start_coords[0], start_coords[1], canvas_x, canvas_y, 
                                    fill='#D4D4D4', width=2, smooth=True, tags='temp_connection')

    def on_release(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        if self.dragging:
            self.dragging = False
            self.dragged_node = None
        elif self.connecting:
            item = self.canvas.find_closest(canvas_x, canvas_y)[0]
            tags = self.canvas.gettags(item)
            if 'port' in tags:
                port_type = next((tag for tag in tags if tag.startswith('input_') or tag.startswith('output_')), None)
                if port_type and port_type.startswith('input_') and self.connection_start[2].startswith('output_'):
                    self.create_connection(self.connection_start, (item, tags[0], port_type))
            self.connecting = False
            self.connection_start = None
            self.canvas.delete('temp_connection')

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
        start_node = next(node for node in self.nodes if node.title == start[1])
        end_node = next(node for node in self.nodes if node.title == end[1])
        
        output_node, input_node = start_node, end_node
        output_index = int(start[2].split('_')[1])
        input_index = int(end[2].split('_')[1])
        
        # Remove any existing connection to this input
        self.remove_connection_to_input(end[0])
        
        connection = Connection(output_node, output_index, input_node, input_index)
        self.connections.append(connection)
        self.draw_connection(connection)

    def draw_connection(self, connection):
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

    def update_connections(self):
        for connection in self.connections:
            output_coords = self.canvas.coords(connection.output_node.output_ids[connection.output_index])
            input_coords = self.canvas.coords(connection.input_node.input_ids[connection.input_index])
            self.canvas.coords(
                connection.line_id,
                output_coords[0], output_coords[1],
                input_coords[0], input_coords[1]
            )

    def remove_connection(self, line_id):
        connection = next((c for c in self.connections if c.line_id == line_id), None)
        if connection:
            self.connections.remove(connection)
            self.canvas.delete(line_id)

    def remove_node(self, node):
        # Remove all connections associated with this node
        connections_to_remove = [c for c in self.connections if c.input_node == node or c.output_node == node]
        for connection in connections_to_remove:
            self.remove_connection(connection.line_id)

        # Remove the node from the list and delete its canvas items
        self.nodes.remove(node)
        self.canvas.delete(node.title)

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