import sys
from pydantic import ValidationError
from flync.model.flync_4_topology.bus_topology import CANBusTopology

try:
    can_bus_topology = CANBusTopology(
        bus_name="CAN_X",
        bus_type="can",
        attachments=[
            {"bus_ref": "CAN_Y"},
            {"bus_ref": "CAN_Z"},
            {"bus_ref": "CAN_W"}
        ]
    )
except ValidationError as e:
    print("SUCCESS")
    sys.exit(0)
else:
    print("FAILURE")
    sys.exit(1)