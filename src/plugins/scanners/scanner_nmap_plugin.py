import subprocess
import xml.etree.ElementTree as ET
from typing import List

from pydantic import validator

from rapidswarm.models.node import Node
from rapidswarm.models.scanners import BaseScanner


class NmapScanner(BaseScanner):
    target_range: str  # TODO: Validate the target range in the format x.y.z.a/b
    scan_options: str = "-sn"  # Default to a simple host discovery scan
    # TODO: That's probably not the right scan option.

    @validator("target_range")
    def check_nmap_exists(cls, v):
        """
        Validates that Nmap is installed and available in the system PATH.

        This validator runs before creating an instance of NmapScanner, ensuring
        that Nmap is available for use. It attempts to run `nmap --version` to
        check for Nmap's presence. If Nmap is not found, it raises a ValueError.
        We're not actually validating the target range here, but instead using
        the validator decorator to check for the presence of Nmap in the system
        PATH. This is a common pattern for validating the presence of external
        dependencies in Pydantic models.

        Args:
            v (str): The target range value provided to the NmapScanner instance.

        Returns:
            str: The validated target range value, unchanged if Nmap is found.

        Raises:
            ValueError: If Nmap is not installed or not found in PATH.
        """
        try:
            subprocess.check_output(["nmap", "--version"])
        except FileNotFoundError:
            raise ValueError("Nmap is not installed or not found in PATH.")
        return v

    def scan(self) -> List[Node]:
        """
        Executes an Nmap scan with the specified target range and options,
        then parses the XML output to create and return a list of Node objects.
        """
        command = f"nmap {self.scan_options} {self.target_range} -oX -"
        result = subprocess.check_output(command.split())
        return self.parse_nmap_output(result)

    def parse_nmap_output(self, xml_output: bytes) -> List[Node]:
        """
        Parses the XML output from Nmap and creates Node objects.

        Args:
            xml_output (bytes): The XML output from an Nmap scan.

        Returns:
            List[Node]: A list of Node objects created from the scan results.
        """
        root = ET.fromstring(xml_output)
        nodes = []
        for host in root.findall("host"):
            # TODO: Parsing logic goes here.
            nodes.append(Node(...))
        return nodes

    def validate(self):
        """
        Validates the NmapScanner configurations.

        This method can be used to implement additional validation logic specific
        to NmapScanner configurations. This method is called automatically by
        Pydantic during model instantiation.
        """
        # Validation logic goes here.
        pass
