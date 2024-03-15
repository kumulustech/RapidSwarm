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


# Either we store built-in probes here, or we split all probes off into their own files.
# If build-in probes remain here, we should move all of the imports to the top.
# Someone with a strong opinion or a case for either one of those should go for it and
# document things in the project Wiki.
import re
import subprocess


class PingProbe(BaseProbe):
    command: str = (
        "ping -c 1"  # Default ping command. In theory could override with anything.
    )

    def __init__(self, **data):
        super().__init__(**data)
        if not self.nodes:  # If the nodes didn't come pre-populated...
            self.nodes = []  # Assume we'll get some later.

    def execute_command(self) -> str:
        results = []
        for node in self.nodes:
            for interface in node.network_interfaces:
                ip_address = interface.ip_address
                try:
                    output = subprocess.check_output(
                        ["ping", "-c", "1", str(ip_address)],
                        stderr=subprocess.STDOUT,
                        universal_newlines=True,
                    )
                    results.append(
                        {
                            "node": node.id,
                            "interface": interface.mac_address,
                            "output": output,
                        }
                    )
                except subprocess.CalledProcessError as e:
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
        return parsed_results
