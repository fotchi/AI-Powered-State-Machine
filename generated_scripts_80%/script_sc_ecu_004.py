import sys
from flync.model.flync_4_ecu.switch import Switch, VLANEntry, SwitchPort

from pydantic import ValidationError

scenario = {
    "type": "Negative",
    "description": "Switch configuration with VLAN ID out of allowed range"
}

try:
    vlan_entry = VLANEntry(vlan_id=5000)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

sys.exit(0)