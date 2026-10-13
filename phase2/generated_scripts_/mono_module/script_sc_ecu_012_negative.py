import sys
from pydantic import ValidationError
from flync.model.flync_4_ecu.controller import EthernetInterface

try:
    obj = EthernetInterface(
        name="eth0",
        interface_config={
            "mii_config": {
                "phy": "phy_missing"
            }
        }
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