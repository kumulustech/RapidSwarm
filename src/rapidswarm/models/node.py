from typing import List

from pydantic import BaseModel, Field

from .gpu import GPU
from .network_interface import NetworkInterface


class Node(BaseModel):
    id: str = Field(..., description="Unique identifier for the node")
    hostname: str = Field(..., description="Hostname of the node")
    network_interfaces: List[NetworkInterface] = Field(
        [], description="List of network interfaces associated with the node"
    )
    gpus: List[GPU] = Field([], description="List of GPUs associated with the node")
