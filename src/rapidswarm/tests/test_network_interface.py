from ipaddress import IPv4Address

import pytest
from pydantic import ValidationError

from rapidswarm.models.network_interface import NetworkInterface
from rapidswarm.models.network_interface_type import NetworkInterfaceType


def test_network_interface_creation():
    interface = NetworkInterface(
        mac_address="00:11:22:33:44:55",
        ip_address="192.168.0.1",
        is_active=True,
        interface_type=NetworkInterfaceType.ETHERNET,
    )
    assert interface.mac_address == "00:11:22:33:44:55"
    assert interface.ip_address == IPv4Address("192.168.0.1")
    assert interface.is_active
    assert interface.interface_type == NetworkInterfaceType.ETHERNET


def test_network_interface_invalid_mac_address():
    with pytest.raises(ValidationError):
        NetworkInterface(
            mac_address="invalid_mac",
            ip_address="192.168.0.1",
            is_active=True,
            interface_type=NetworkInterfaceType.ETHERNET,
        )
