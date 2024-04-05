from typing import List

from pydantic import BaseModel

from .node import Node


class BaseScanner(BaseModel):
    def scan(self) -> List[Node]:
        """
        Scans for network nodes and interfaces.

        Returns:
            List[Node]: A list of Node objects discovered during the scan.
        """
        raise NotImplementedError("Subclasses must implement the 'scan' method.")

    def validate(self):
        raise NotImplementedError("Subclasses must implement the 'validate' method.")
