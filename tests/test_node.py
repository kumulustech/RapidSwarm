from pydantic import ValidationError
from rapidswarm.models.node import NetworkSwitch, Node

def test_network_switch_missing_field():
  # Arrange
  switch_data = {
    "id": "sw1",
    "ip_address": "10.0.0.1"
  }

  # Act & Assert
  try:
    switch = NetworkSwitch(**switch_data)
    assert False, "Expected ValidationError"
  except ValidationError:
    pass

def test_valid_node_all_fields():
  # Arrange
  switch = NetworkSwitch(id="sw1", model="Cisco9300", ip_address="10.0.0.1") 
  node_data = {
    "id": "n1",  
    "hostname": "node1",
    "network_interfaces": [],
    "gpus": [],
    "network_switch": switch
  }
  # Act  
  node = Node(**node_data)

  # Assert
  assert node.id == "n1"
  assert node.hostname == "node1"
  assert node.network_interfaces == []
  assert node.gpus == []
  assert node.network_switch == switch

def test_node_optional_fields_none():
  # Arrange
  node_data = {  
    "hostname": "node1",
    "id": None,
    "network_interfaces": [],
    "gpus": [],
    "network_switch": None
  }
  
  # Act
  node = Node(**node_data)
  
  # Assert
  assert node.id is None
  assert node.network_interfaces == [] 
  assert node.gpus == []
  assert node.network_switch is None