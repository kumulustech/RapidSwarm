from pydantic import BaseModel, Field, IPvAnyAddress
from pydantic_extra_types.mac_address import MacAddress

from .network_interface_type import NetworkInterfaceType


class NetworkInterface(BaseModel):
    mac_address: MacAddress = Field(
        ..., description="MAC address of the network interface"
    )
    ip_address: IPvAnyAddress = None
    is_active: bool = True
    interface_type: NetworkInterfaceType = NetworkInterfaceType.ETHERNET
