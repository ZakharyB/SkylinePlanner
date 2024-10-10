import tkinter as tk

class Tooltip:
    def __init__(self, widget, text, canvas_item=None):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.canvas_item = canvas_item
        
        if canvas_item:
            self.widget.tag_bind(canvas_item, "<Enter>", self.show_tooltip)
            self.widget.tag_bind(canvas_item, "<Leave>", self.hide_tooltip)
        else:
            self.widget.bind("<Enter>", self.show_tooltip)
            self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.canvas_item:
            bbox = self.widget.bbox(self.canvas_item)
            if not bbox:
                return
            x = bbox[0] + self.widget.winfo_rootx()
            y = bbox[1] + self.widget.winfo_rooty()
        else:
            x = event.x_root
            y = event.y_root

        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x+10}+{y+10}")

        label = tk.Label(self.tooltip, text=self.text, background="#ffffe0", relief="solid", borderwidth=1)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
