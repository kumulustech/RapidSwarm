import csv
import io
import warnings
from typing import List, Union

from pydantic import Field, field_validator
from rapidswarm.models.network_interface import NetworkInterface
from rapidswarm.models.network_interface_type import NetworkInterfaceType
from rapidswarm.models.node import Node
from rapidswarm.models.scanners import BaseScanner

INFINIBAND_MAC_PREFIX = "00:02:c9"
NODE_NAME_FIELD = "node_name"
INTERFACE_NAME_FIELD = "interface_name"
MAC_ADDRESS_FIELD = "mac_address"
IP_ADDRESS_FIELD = "ip_address"
INTERFACE_TYPE_FIELD = "interface_type"
INTERFACES_FIELD = "interfaces"
EXPECTED_HEADERS = [
    NODE_NAME_FIELD,
    INTERFACE_NAME_FIELD,
    MAC_ADDRESS_FIELD,
    IP_ADDRESS_FIELD,
]


class CSVScanner(BaseScanner):
    csv_data: Union[str, None] = Field(
        None, description="Pre-loaded CSV data as a string."
    )
    csv_file: Union[str, None] = Field(
        None,
        description="Path to the CSV file containing node and interface information.",
    )
    expected_headers: List[str] = EXPECTED_HEADERS

    @field_validator("csv_file", "csv_data")
    def validate_csv_input(cls, v, values, **kwargs):
        if v is None and values.get("csv_data") is None:
            raise ValueError("Either 'csv_file' or 'csv_data' must be provided.")
        return v

    def validate(self):
        # Validate the presence of either 'csv_file' or 'csv_data'
        self.validate_csv_input(self.csv_file, {"csv_data": self.csv_data})
        # Validate compatibility with the Node class
        self.validate_node_compatibility()

    def get_interface_type(self, mac_address):
        if mac_address.lower().startswith(INFINIBAND_MAC_PREFIX):
            return NetworkInterfaceType.INFINIBAND
        else:
            return NetworkInterfaceType.ETHERNET

    def validate_node_compatibility(self):
        node_fields = set(Node.model_fields.keys())
        csv_fields = set(self.expected_headers)
        missing_fields = node_fields - csv_fields
        if missing_fields:
            raise ValueError(
                f"CSV headers are missing the following fields expected by the Node class: {', '.join(missing_fields)}"
            )

        extraneous_fields = csv_fields - node_fields
        if extraneous_fields:
            warnings.warn(
                "CSV headers contain the following extraneous fields that won't be "
                f"parsed by the Node class: {', '.join(extraneous_fields)}"
            )

    def scan(self) -> List[Node]:
        nodes_dict = {}

        try:
            if self.csv_data:
                csv_data = io.StringIO(self.csv_data)
            else:
                with open(self.csv_file, "r") as file:
                    csv_data = file
            reader = csv.DictReader(csv_data)

            for row in reader:
                node_id = row[NODE_NAME_FIELD]
                if node_id not in nodes_dict:
                    nodes_dict[node_id] = Node(
                        id=node_id, hostname=node_id, network_interfaces=[]
                    )
                interface = NetworkInterface(
                    mac_address=row[MAC_ADDRESS_FIELD],
                    ip_address=row[IP_ADDRESS_FIELD],
                    interface_type=self.get_interface_type(row[MAC_ADDRESS_FIELD]),
                )
                nodes_dict[node_id].network_interfaces.append(interface)

        except Exception as e:
            raise Exception(f"An error occurred while reading the CSV data: {str(e)}")

        return list(nodes_dict.values())
