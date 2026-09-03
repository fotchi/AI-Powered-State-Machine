import sys
from flync.model.flync_4_topology.ethernet_topology import ExternalConnection
from pydantic import ValidationError

try:
    obj = ExternalConnection(id="conn1", ecu1_port_name="port1", ecu2_port_name="port2", type="invalid_type")
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
except Exception as exc:
    print(f"UNEXPECTED ERROR: {type(exc).__name__}: {exc}")
    sys.exit(1)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)