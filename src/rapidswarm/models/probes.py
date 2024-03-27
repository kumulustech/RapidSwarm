import re
import subprocess
from typing import List, Optional, Union

from loguru import logger
from pydantic import BaseModel

from .network_interface import NetworkInterface
from .node import Node


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


class PingResult(BaseModel):
    node: str
    interface: str
    success: bool
    ping_time: Optional[float] = None


class PingProbe(BaseProbe):
    command: str = "ping -c 1"  # This is now just a template.

    def __init__(self, **data):
        super().__init__(**data)
        if not self.nodes:  # If the nodes didn't come pre-populated...
            logger.debug(
                "PingProbe initialized without pre-populated nodes. Expecting nodes to be set later."
            )
            self.nodes = []  # Assume we'll get some later.

    def execute_command(self) -> str:
        """Executes the ping command for each node's network interfaces, including the IP address."""
        results = []
        for node in self.nodes:
            for interface in node.network_interfaces:
                ip_address = interface.ip_address
                command_with_ip = f"{self.command} {ip_address}"
                try:
                    # Use a verbose log message with a specific prefix or pattern
                    logger.debug(
                        f"[VERBOSE] Executing ping for node: {node.id} on interface: {interface.mac_address} with IP: {ip_address}"
                    )
                    output = subprocess.check_output(
                        command_with_ip.split(),
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                    )
                    # Similarly, for successful ping output
                    logger.debug(
                        f"[VERBOSE] Ping successful for node: {node.id} ({interface.mac_address}) with output: {output}"
                    )
                    results.append(
                        {
                            "node": node.id,
                            "interface": interface.mac_address,
                            "output": output,
                        }
                    )
                except subprocess.CalledProcessError as e:
                    logger.debug(
                        f"[VERBOSE] Ping failed for node: {node.id} ({interface.mac_address}) with error: {e.output}"
                    )
                    results.append(
                        {
                            "node": node.id,
                            "interface": interface.mac_address,
                            "output": e.output,
                        }
                    )
        return results

    def parse_output(self, output) -> List[PingResult]:
        parsed_results = []
        for result in output:
            success = "1 packets received" in result["output"]
            ping_time = None
            if success:
                match = re.search(r"time=(\d+\.\d+) ms", result["output"])
                if match:
                    ping_time = float(match.group(1))
            parsed_result = PingResult(
                node=result["node"],
                interface=result["interface"],
                success=success,
                ping_time=ping_time,
            )
            parsed_results.append(parsed_result)
        logger.debug("Parsed ping results: {}", parsed_results)
        return parsed_results
