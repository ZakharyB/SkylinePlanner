from typing import List, Dict, Tuple, Optional, Any

class Node:
    def __init__(self, title: str, inputs: Optional[List[str]] = None, outputs: Optional[List[str]] = None):
        self.title: str = title
        self.inputs: List[str] = inputs or []
        self.config: Dict[str, Any] = {}
        self.outputs: List[str] = outputs or []
        self.pos: Tuple[int, int] = (0, 0)
        self.size: Tuple[int, int] = (100, 50)
        self.canvas_id: Optional[int] = None
        self.input_ids: List[int] = []
        self.output_ids: List[int] = []
        self.output_data: Dict[str, Any] = {}

    def get_config_options(self) -> Dict[str, Any]:
        return self.config

    def update_config(self, new_config: Dict[str, Any]) -> None:
        self.config.update(new_config)
        self.process()

    def process(self, **kwargs: Any) -> None:
        pass

class Connection:
    def __init__(self, output_node: Node, output_index: int, input_node: Node, input_index: int):
        self.output_node: Node = output_node
        self.output_index: int = output_index
        self.input_node: Node = input_node
        self.input_index: int = input_index
        self.line_id: Optional[int] = None