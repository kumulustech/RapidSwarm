import subprocess
from typing import List

from pydantic import validator

from .network_interface import NetworkInterface
from .node import Node
from .scanners import BaseScanner


class ARPScanner(BaseScanner):
    interface: str
    target_range: str

    @validator("interface")
    def check_arp_scan_availability(cls, v):
        """
        Validates that arp-scan is installed and can be executed with the given interface.

        Args:
            v (str): The network interface to be used for the ARP scan.

        Raises:
            ValueError: If arp-scan is not installed or cannot access the network interface.
        """
        # Check if arp-scan is installed
        try:
            subprocess.check_output(["arp-scan", "--version"], text=True)
        except FileNotFoundError:
            raise ValueError(
                "arp-scan is not installed. Please install arp-scan to use this scanner."
            )

        # Attempt to run arp-scan on the specified interface to check for permission issues
        try:
            subprocess.check_output(
                ["sudo", "arp-scan", "--interface", v, "--localnet"],
                text=True,
                stderr=subprocess.STDOUT,
            )
        except subprocess.CalledProcessError as e:
            raise ValueError(
                f"Failed to run arp-scan on interface '{v}'. Ensure you have the necessary permissions. Error: {e.output}"
            )

        return v

    def scan(self) -> List[Node]:
        """
        Executes an ARP scan over the specified interface and target range,
        then parses the output to create and return a list of Node objects.

        Returns:
            List[Node]: A list of Node objects discovered during the ARP scan.
        """
        command = f"sudo arp-scan --interface={self.interface} {self.target_range}"
        result = subprocess.check_output(command.split(), text=True)
        return self.parse_arp_output(result)

    def parse_arp_output(self, arp_output: str) -> List[Node]:
        """
        Parses the output from an ARP scan and creates Node objects.

        Args:
            arp_output (str): The output from an ARP scan.

        Returns:
            List[Node]: A list of Node objects created from the scan results.
        """
        nodes = []
        for line in arp_output.splitlines():
            if (
                line
                and not line.startswith("Interface:")
                and not line.startswith("Starting")
                and not line.startswith("Ending")
            ):
                parts = line.split()
                if len(parts) >= 2:
                    ip_address, mac_address = parts[0], parts[1]
                    node = Node(
                        id=mac_address,
                        hostname=ip_address,
                        network_interfaces=[
                            NetworkInterface(
                                mac_address=mac_address, ip_address=ip_address
                            )
                        ],
                    )
                    nodes.append(node)
        return nodes
