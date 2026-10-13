import sys
from flync.model.flync_4_topology.bus_topology import CANBusTopology
from pydantic import ValidationError

try:
    can_bus_topology = CANBusTopology(
        bus_name="CAN_X",
        bus_type="can",
        attachments=[
            {"bus_ref": "CAN_X"},
            {"bus_ref": "CAN_X"},
            {"bus_ref": "CAN_X"}
        ]
    )
except ValidationError as e:
    sys.exit(0)

sys.exit(1)