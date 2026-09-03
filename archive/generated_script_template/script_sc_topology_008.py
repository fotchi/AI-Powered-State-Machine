import sys
from pydantic import ValidationError

from flync.model.flync_4_topology.ethernet_topology import ExternalConnection

try:
    external_connection = ExternalConnection(
        id="demo_id",
        ecu1_port_name="demo_ecu1_port_name",
        ecu2_port_name="demo_ecu2_port_name",
    )
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
