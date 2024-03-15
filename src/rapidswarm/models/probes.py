from typing import List, Union

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


# Either we store built-in probes here, or we split all probes off into their own files.
# If build-in probes remain here, we should move all of the imports to the top.
# Someone with a strong opinion or a case for either one of those should go for it and
# document things in the project Wiki.
import re
import subprocess


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
        results = []
        for node in self.nodes:
            for interface in node.network_interfaces:
                ip_address = interface.ip_address
                command_with_ip = f"{self.command} {ip_address}"  # Include the IP address in the command.
                try:
                    logger.debug(
                        "Executing ping for node: {} on interface: {} with IP: {}",
                        node.id,
                        interface.mac_address,
                        ip_address,
                    )
                    output = subprocess.check_output(
                        command_with_ip.split(),
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                    )
                    logger.info(
                        "Ping successful for node: {} ({}) with output: {}",
                        node.id,
                        interface.mac_address,
                        output,
                    )
                    results.append(
                        {
                            "node": node.id,
                            "interface": interface.mac_address,
                            "output": output,
                        }
                    )
                except subprocess.CalledProcessError as e:
                    logger.warning(
                        "Ping failed for node: {} ({}) with error: {}",
                        node.id,
                        interface.mac_address,
                        e.output,
                    )
                    results.append(
                        {
                            "node": node.id,
                            "interface": interface.mac_address,
                            "output": e.output,
                        }
                    )
        return results

    def parse_output(self, output):
        parsed_results = []
        for result in output:
            success = "1 packets transmitted, 1 received" in result["output"]
            ping_time = None
            if success:
                match = re.search(r"time=(\d+\.\d+) ms", result["output"])
                if match:
                    ping_time = float(match.group(1))
            parsed_results.append(
                {
                    "node": result["node"],
                    "interface": result["interface"],
                    "success": success,
                    "ping_time": ping_time,
                }
            )
        logger.debug("Parsed ping results: {}", parsed_results)
        return parsed_results
