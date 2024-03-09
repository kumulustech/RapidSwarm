from enum import Enum


class NetworkInterfaceType(str, Enum):
    ETHERNET = "ethernet"
    INFINIBAND = "infiniband"

    def __str__(self):
        return self.value
