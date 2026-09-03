import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_ecu.port import ECUPort
from pydantic import ValidationError

scenario = {
    'type': 'Negative',
    'description': 'CANBus Participating Node References ECU with Missing ECUPort'
}

canbus_config = {
    "name": "my_can_bus",
    "baud_rate": 1000000,
    "fd_enabled": True,
    "fd_baud_rate": 500000,
    "frames": [
        {"type": "CANFrame", "id": 123, "data": [1, 2, 3]},
        {"type": "CANFDFrame", "id": 456, "data": [4, 5, 6]}
    ],
    "state_memberships": [{"ref": "my_state"}]
}

ecu_config = {
    "name": "my_ecu",
    "ports": []
}

try:
    canbus = CANBus(**canbus_config)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

port = ECUPort(name="my_port", mdi_config=BASET1())
print("SUCCESS")
sys.exit(0)