import pytest

from rapidswarm.models.network_interface_type import NetworkInterfaceType


def test_network_interface_type_values():
    assert NetworkInterfaceType.ETHERNET.value == "ethernet"
    assert NetworkInterfaceType.INFINIBAND.value == "infiniband"


def test_network_interface_type_equality():
    assert NetworkInterfaceType.ETHERNET == "ethernet"
    assert NetworkInterfaceType.INFINIBAND == "infiniband"


def test_network_interface_type_inequality():
    assert NetworkInterfaceType.ETHERNET != "infiniband"
    assert NetworkInterfaceType.INFINIBAND != "ethernet"


def test_network_interface_type_string_representation():
    assert str(NetworkInterfaceType.ETHERNET) == "ethernet"
    assert str(NetworkInterfaceType.INFINIBAND) == "infiniband"


def test_network_interface_type_from_value():
    assert NetworkInterfaceType("ethernet") == NetworkInterfaceType.ETHERNET
    assert NetworkInterfaceType("infiniband") == NetworkInterfaceType.INFINIBAND


def test_network_interface_type_invalid_value():
    with pytest.raises(ValueError) as exc_info:
        NetworkInterfaceType("invalid_type")
    assert str(exc_info.value) == "'invalid_type' is not a valid NetworkInterfaceType"
