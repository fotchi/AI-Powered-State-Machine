import sys
from pydantic import ValidationError
from flync.model.flync_4_ecu.controller import EthernetInterface
from flync.model.flync_4_ecu.controller_topology import InterfaceToInterfaceLink

try:
    link = InterfaceToInterfaceLink(
        type="ethernet",
        id="link1",
        controller_interface="invalid_iface",
        controller_interface2="valid_iface"
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