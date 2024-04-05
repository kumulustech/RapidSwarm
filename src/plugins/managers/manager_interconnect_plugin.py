from typing import List
from pydantic import BaseModel
from rapidswarm.models.manager import BaseManager
from rapidswarm.models.node import Node

class AllToAllConnectivityTestManager(BaseManager):
    def run(self, nodes: List[Node]):
        for source_node in nodes:
            for target_node in nodes:
                if source_node != target_node:
                    self._test_connectivity(source_node, target_node)

    def _test_connectivity(self, source_node: Node, target_node: Node):
        # Implement the logic to test connectivity between source_node and target_node
        # This could involve sending packets, checking network metrics, etc.
        # Example placeholder logic:
        print(f"Testing connectivity from {source_node.hostname} to {target_node.hostname}")
        # Perform the actual connectivity test and assert the results

class InterSwitchConnectivityTestManager(BaseManager):
    def run(self, nodes: List[Node]):
        switch_groups = self._group_nodes_by_switch(nodes)
        for source_switch, source_nodes in switch_groups.items():
            for target_switch, target_nodes in switch_groups.items():
                if source_switch != target_switch:
                    self._test_inter_switch_connectivity(source_nodes, target_nodes)

    def _group_nodes_by_switch(self, nodes: List[Node]):
        switch_groups = {}
        for node in nodes:
            switch = node.network_switch.id if node.network_switch else None
            if switch not in switch_groups:
                switch_groups[switch] = []
            switch_groups[switch].append(node)
        return switch_groups

    def _test_inter_switch_connectivity(self, source_nodes: List[Node], target_nodes: List[Node]):
        # Implement the logic to test connectivity between nodes on different switches
        # Example placeholder logic:
        for source_node in source_nodes:
            for target_node in target_nodes:
                print(f"Testing inter-switch connectivity from {source_node.hostname} to {target_node.hostname}")
                # Perform the actual connectivity test and assert the results

class IntraSwitchConnectivityTestManager(BaseManager):
    def run(self, nodes: List[Node]):
        switch_groups = self._group_nodes_by_switch(nodes)
        for switch, switch_nodes in switch_groups.items():
            self._test_intra_switch_connectivity(switch_nodes)

    def _group_nodes_by_switch(self, nodes: List[Node]):
        switch_groups = {}
        for node in nodes:
            switch = node.network_switch.id if node.network_switch else None
            if switch not in switch_groups:
                switch_groups[switch] = []
            switch_groups[switch].append(node)
        return switch_groups

    def _test_intra_switch_connectivity(self, nodes: List[Node]):
        # Implement the logic to test connectivity between nodes on the same switch
        # Example placeholder logic:
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                source_node = nodes[i]
                target_node = nodes[j]
                print(f"Testing intra-switch connectivity from {source_node.hostname} to {target_node.hostname}")
                # Perform the actual connectivity test and assert the results
