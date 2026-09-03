import sys
from pydantic import ValidationError
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection

try:
    external_connection = ExternalConnection(
        id="ecu1_to_sensor",
        ecu1_port_name="CAN_X",
        ecu2_port_name="CAN_Y"
    )
except ValidationError as e:
    print("Validation failed:", e)
    sys.exit(1)

print("SUCCESS")
sys.exit(0)