import sys
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection
from flync.model.flync_4_communication.flync_channels import FLYNCChannelConfig
from pydantic import ValidationError

flync_channel_config = FLYNCChannelConfig(
    can_buses=[{'name': 'CAN_bus_1', 'baud_rate': 1000000, 'description': 'CAN bus 1'}],
    lin_buses=[{'name': 'LIN_bus_1', 'baud_rate': 20000, 'description': 'LIN bus 1'}],
    ethernet_pdu_containers=[
        {'header': {'id_length_bits': 16, 'length_field_bits': 16}, 'pdu_name': 'ethernet_pdu_1'}
    ]
)

try:
    external_connection = ExternalConnection(
        type='ecu_port_to_ecu_port',
        id='external_connection_id',
        ecu1_port_name='Port_A',
        ecu2_port_name='Port_B'
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

print("SUCCESS")
sys.exit(0)