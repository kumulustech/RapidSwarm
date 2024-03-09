from unittest.mock import MagicMock, patch

import pytest

from rapidswarm.models.gpu import GPU
from rapidswarm.models.network_interface import NetworkInterface, NetworkInterfaceType
from rapidswarm.models.node import Node
from rapidswarm.models.probes import BaseProbe


def create_test_node(node_id, hostname):
    test_network_interface = NetworkInterface(
        mac_address="00:1B:44:11:3A:B7",
        ip_address="192.168.1.1",
        is_active=True,
        interface_type=NetworkInterfaceType.ETHERNET,
    )
    test_gpu = GPU(id="gpu0", model="TestModel")

    node = Node(
        id=node_id,
        hostname=hostname,
        network_interfaces=[test_network_interface],
        gpus=[test_gpu],
    )
    return node


class DummyProbe(BaseProbe):
    def parse_output(self, output: str):
        return "parsed output"

    def execute_command(self) -> str:
        return "command output"


def test_probe_with_single_node_does_not_require_interface():
    node = create_test_node("node1", "hostname1")
    probe = DummyProbe(nodes=[node], command="test command")
    # This should not raise any error
    probe.validate_interface()


def test_probe_with_two_nodes_requires_interface():
    node1 = create_test_node("node1", "hostname1")
    node2 = create_test_node("node2", "hostname2")
    probe = DummyProbe(nodes=[node1, node2], command="test command")
    with pytest.raises(ValueError) as exc_info:
        probe.validate_interface()
    assert "A probe with two nodes must specify a network interface." in str(
        exc_info.value
    )


def test_run_method_calls_validation_and_execution_methods():
    node = create_test_node("node1", "hostname1")
    probe = DummyProbe(nodes=[node], command="test command")

    with patch.object(
        DummyProbe, "validate_nodes"
    ) as mock_validate_nodes, patch.object(
        DummyProbe, "validate_interface"
    ) as mock_validate_interface, patch.object(
        DummyProbe, "execute_command", return_value="command output"
    ) as mock_execute_command, patch.object(
        DummyProbe, "parse_output", return_value="parsed output"
    ) as mock_parse_output:

        result = probe.run()

        mock_validate_nodes.assert_called_once()
        mock_validate_interface.assert_called_once()
        mock_execute_command.assert_called_once()
        mock_parse_output.assert_called_once_with("command output")
        assert result == "parsed output"


def test_probe_with_invalid_number_of_nodes():
    node = create_test_node("node1", "hostname1")
    # Test with zero nodes
    with pytest.raises(ValueError) as exc_info_zero:
        DummyProbe(nodes=[], command="test command").validate_nodes()
    assert "A probe must have either one or two nodes." in str(exc_info_zero.value)

    # Test with more than two nodes
    node2 = create_test_node("node2", "hostname2")
    node3 = create_test_node("node3", "hostname3")
    with pytest.raises(ValueError) as exc_info_more:
        DummyProbe(nodes=[node, node2, node3], command="test command").validate_nodes()
    assert "A probe must have either one or two nodes." in str(exc_info_more.value)


def test_dummy_probe_parse_output():
    dummy_probe = DummyProbe(nodes=[], command="dummy command")
    output = "test output"
    parsed_output = dummy_probe.parse_output(output)
    assert (
        parsed_output == "parsed output"
    ), "The parse_output method should return 'parsed output'"


def test_dummy_probe_execute_command():
    dummy_probe = DummyProbe(nodes=[], command="dummy command")
    command_output = dummy_probe.execute_command()
    assert (
        command_output == "command output"
    ), "The execute_command method should return 'command output'"


def test_base_probe_parse_output_raises_not_implemented_error():
    base_probe = BaseProbe(nodes=[], command="dummy command")
    with pytest.raises(NotImplementedError):
        base_probe.parse_output("dummy output")


def test_base_probe_execute_command_raises_not_implemented_error():
    base_probe = BaseProbe(nodes=[], command="dummy command")
    with pytest.raises(NotImplementedError):
        base_probe.execute_command()
