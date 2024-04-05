from typing import List, Union

from loguru import logger
from pydantic import BaseModel

from rapidswarm.models.network_interface import NetworkInterface
from rapidswarm.models.node import Node


class BaseProbe(BaseModel):
    nodes: List[Node]
    interface: Union[NetworkInterface, None] = None
    command: str

    def validate_nodes(self):
        if len(self.nodes) < 1 or len(self.nodes) > 2:
            logger.error(
                "Probe validation failed: A probe must have either one or two nodes."
            )
            raise ValueError("A probe must have either one or two nodes.")

    def validate_interface(self):
        """Validates the network interface for probes with two nodes."""
        if len(self.nodes) == 2 and self.interface is None:
            logger.error(
                "Probe validation failed: A probe with two nodes must specify a network interface."
            )
            raise ValueError("A probe with two nodes must specify a network interface.")

    def parse_output(self, output: str):
        """Placeholder for parsing output. Must be implemented by subclasses."""
        raise NotImplementedError(
            "Subclasses must implement the 'parse_output' method."
        )

    def run(self):
        """Runs the probe, including validation, command execution, and output parsing."""
        logger.info("Running probe with command: {}", self.command)
        self.validate_nodes()
        self.validate_interface()
        output = self.execute_command()
        return self.parse_output(output)

    def execute_command(self) -> str:
        """Placeholder for executing command. Must be implemented by subclasses."""
        raise NotImplementedError(
            "Subclasses must implement the 'execute_command' method."
        )
