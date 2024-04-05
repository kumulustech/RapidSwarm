import pytest
from rapidswarm.models.node import Node, NetworkSwitch
from rapidswarm.models.network_interface import NetworkInterface, NetworkInterfaceType
from plugins.managers.manager_interconnect_plugin import AllToAllConnectivityTestManager, InterSwitchConnectivityTestManager, IntraSwitchConnectivityTestManager

@pytest.fixture
def nodes_with_switches():
    nodes = []
    switches = {f"switch{1 + i // 16}": NetworkSwitch(id=f"switch{1 + i // 16}", model="GenericSwitchModel", ip_address=f"10.0.0.{1 + i // 16}") for i in range(127)}
    for i in range(127):
        network_interfaces = [
            NetworkInterface(mac_address=f"00:1B:44:11:{i//256:02X}:{i%256:02X}", ip_address=f"192.168.1.{i}", is_active=True, interface_type=NetworkInterfaceType.ETHERNET),
            NetworkInterface(mac_address=f"00:1B:44:11:{(i+1)//256:02X}:{(i+1)%256:02X}", ip_address=f"10.10.1.{i}", is_active=True, interface_type=NetworkInterfaceType.INFINIBAND),
            NetworkInterface(mac_address=f"00:1B:44:11:{(i+2)//256:02X}:{(i+2)%256:02X}", ip_address=f"10.10.2.{i}", is_active=True, interface_type=NetworkInterfaceType.INFINIBAND)
        ]
        switch_id = f"switch{1 + i // 16}"
        node = Node(id=f"node{i}", hostname=f"hostname{i}", network_interfaces=network_interfaces, network_switch=switches[switch_id])
        nodes.append(node)
    return nodes

@pytest.mark.parametrize("manager_class", [
    AllToAllConnectivityTestManager,
    InterSwitchConnectivityTestManager,
    IntraSwitchConnectivityTestManager
])
def test_connectivity_managers_run_method(nodes_with_switches, manager_class):
    """
    Test the run method of connectivity managers to ensure they correctly initiate connectivity tests.
    This test verifies that the run method can be called without errors for different manager types.
    """
    manager = manager_class()
    # Arrange: Use the nodes_with_switches fixture to provide input nodes
    nodes = nodes_with_switches
    
    # Act: Execute the run method of the manager with the provided nodes
    manager.run(nodes)
    
    # Assert: Currently, we're only checking for the absence of exceptions. Further assertions can be added
    # to validate the internal state or outputs of the manager if applicable.
    assert True, "The run method completed without raising an exception."

def test_group_nodes_by_switch_with_mixed_nodes(nodes_with_switches):
    """
    Test the _group_nodes_by_switch method to ensure it correctly groups nodes by their associated switch.
    This test is important to verify that the logic for grouping nodes respects the network topology.
    """
    manager = InterSwitchConnectivityTestManager()
    nodes = nodes_with_switches
    
    # Act: Group nodes by their associated switch
    grouped_nodes = manager._group_nodes_by_switch(nodes)
    
    # Assert: Verify that the grouped nodes match the expected switch assignments
    expected_switches = {f"switch{1 + i // 16}" for i in range(127)}
    assert set(grouped_nodes.keys()) == expected_switches, "Nodes are not correctly grouped by switch."
    for switch, nodes in grouped_nodes.items():
        assert all(node.network_switch.id == switch for node in nodes), f"Not all nodes in group {switch} are correctly associated with their switch."
