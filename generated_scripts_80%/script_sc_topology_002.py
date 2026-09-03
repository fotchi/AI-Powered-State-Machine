import sys
from pydantic import ValidationError
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection

try:
    obj = ExternalConnection(
        type='other_type',
        id='12345',
        ecu1_port_name='port1',
        ecu2_port_name='port2'
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)