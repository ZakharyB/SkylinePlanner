class Node:
    def __init__(self, title, inputs=None, outputs=None):
        self.title = title
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.pos = (0, 0)
        self.size = (100, 50)
        self.canvas_id = None
        self.input_ids = []
        self.output_ids = []
        self.output_data = {}  # This will store the processed data

    def process(self, **kwargs):
        # This method will be overridden by specific node types
        pass

class Connection:
    def __init__(self, output_node, output_index, input_node, input_index):
        self.output_node = output_node
        self.output_index = output_index
        self.input_node = input_node
        self.input_index = input_index
        self.line_id = None