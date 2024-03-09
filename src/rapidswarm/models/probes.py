from typing import List, Union

from pydantic import BaseModel

from .network_interface import NetworkInterface
from .node import Node


class BaseProbe(BaseModel):
    nodes: List[Node]
    interface: Union[NetworkInterface, None] = None
    command: str

    def validate_nodes(self):
        if len(self.nodes) < 1 or len(self.nodes) > 2:
            raise ValueError("A probe must have either one or two nodes.")

    def validate_interface(self):
        if len(self.nodes) == 2 and self.interface is None:
            raise ValueError("A probe with two nodes must specify a network interface.")

    def parse_output(self, output: str):
        raise NotImplementedError(
            "Subclasses must implement the 'parse_output' method."
        )

    def run(self):
        self.validate_nodes()
        self.validate_interface()
        output = self.execute_command()
        return self.parse_output(output)

    def execute_command(self) -> str:
        raise NotImplementedError(
            "Subclasses must implement the 'execute_command' method."
        )
