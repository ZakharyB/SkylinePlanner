import tkinter as tk
from tkinter import ttk

class NodeConfigSidebar:
    def __init__(self, master, node_editor):
        self.master = master
        self.node_editor = node_editor
        
        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.editor_frame = tk.Frame(self.main_frame)
        self.editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.node_editor.canvas.master = self.editor_frame
        self.node_editor.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create the sidebar (right side)
        self.sidebar = tk.Frame(self.main_frame, width=350, bg='#2C2C2C', padx=10, pady=10)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.title_label = tk.Label(self.sidebar, text="Node Configuration", fg='white', bg='#2C2C2C', font=('Arial', 14, 'bold'))
        self.title_label.pack(pady=(0, 10))

        self.config_frame = tk.Frame(self.sidebar, bg='#2C2C2C')
        self.config_frame.pack(fill=tk.BOTH, expand=True)

        self.current_node = None

        
    def show_config(self, node):
        print(f"Showing config for node: {node.title}")  # Debug print
        self.clear_config()
        self.current_node = node

        tk.Label(self.config_frame, text=f"Config for {node.title}", fg='white', bg='#2C2C2C', font=('Arial', 12, 'bold')).pack(pady=(0, 10))

        for attr, value in node.get_config_options().items():

            print(f"Adding config option: {attr} = {value}")  # Debug print
            frame = tk.Frame(self.config_frame, bg='#2C2C2C')
            frame.pack(fill=tk.X, pady=5)

            label = tk.Label(frame, text=attr.replace('_', ' ').title() + ':', fg='white', bg='#2C2C2C')
            label.pack(side=tk.LEFT)

            if attr == 'scale':
                entry = tk.Entry(frame)
                entry.insert(0, str(value))
                entry.pack(side=tk.RIGHT)
                entry.bind('<Return>', lambda e, a=attr, w=entry: self.update_config(a, w.get()))

            if isinstance(value, bool):
                var = tk.BooleanVar(value=value)
                widget = ttk.Checkbutton(frame, variable=var, command=lambda a=attr, v=var: self.update_config(a, v.get()))
            elif isinstance(value, int):
                var = tk.IntVar(value=value)
                widget = ttk.Entry(frame, textvariable=var)
                widget.bind('<FocusOut>', lambda e, a=attr, v=var: self.update_config(a, v.get()))
            elif isinstance(value, float):
                var = tk.DoubleVar(value=value)
                widget = ttk.Entry(frame, textvariable=var)
                widget.bind('<FocusOut>', lambda e, a=attr, v=var: self.update_config(a, v.get()))
            else:
                var = tk.StringVar(value=str(value))
                widget = ttk.Entry(frame, textvariable=var)
                widget.bind('<FocusOut>', lambda e, a=attr, v=var: self.update_config(a, v.get()))

            widget.pack(side=tk.RIGHT)

    def clear_config(self):
        print("Clearing config")  # Debug print
        for widget in self.config_frame.winfo_children():
            widget.destroy()

    def update_config(self, attr, value):
        if self.current_node:
            print(f"Updating config: {attr} = {value}")  # Debug print
            self.current_node.update_config({attr: value})
            self.node_editor.update_node(self.current_node)

    def show(self):
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        print("Sidebar shown")  # Debug print

    def hide(self):
        self.sidebar.pack_forget()
        print("Sidebar hidden")  # Debug print