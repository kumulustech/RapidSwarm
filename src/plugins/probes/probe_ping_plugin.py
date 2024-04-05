import re
import subprocess
from typing import List, Optional

from loguru import logger
from pydantic import BaseModel

from rapidswarm.models.probes import BaseProbe


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
