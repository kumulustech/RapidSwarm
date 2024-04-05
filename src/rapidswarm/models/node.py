from typing import List, Optional
from pydantic import BaseModel, Field

from .gpu import GPU
from .network_interface import NetworkInterface

class NetworkSwitch(BaseModel):
    id: str = Field(..., description="Unique identifier for the network switch")
    model: str = Field(..., description="Model of the network switch")
    ip_address: str = Field(..., description="IP address of the network switch")

class Node(BaseModel):
    id: Optional[str] = Field(None, description="Unique identifier for the node")
    hostname: str = Field(..., description="Hostname of the node")
    network_interfaces: List[NetworkInterface] = Field(
        [], description="List of network interfaces associated with the node"
    )
    gpus: List[GPU] = Field([], description="List of GPUs associated with the node")
    network_switch: Optional[NetworkSwitch] = Field(
        None, description="Associated network switch for the node"
    )