import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
}

can_bus = CANBus(
    name='CANBus',
    baud_rate=1000000,
    fd_enabled=False,
    frames=[
        {'type': 'CANFrame', 'id': 1, 'data': [1, 2, 3]},
        {'type': 'CANFDFrame', 'id': 2, 'data': [4, 5, 6]},
    ],
)

system_topology = {
    'participating_nodes': [
        {'name': 'ECU_A'},
        {'name': 'ECU_B'},
    ],
    'external_connections': [
        ExternalConnection(
            type='ecu_to_bus',
            id='conn1',
            ecu1_port_name='ECU_A:CAN0',
            ecu2_port_name='ECU_B:CAN0',
        ),
    ],
}

try:
    obj = CANBus(**can_bus.dict())
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)