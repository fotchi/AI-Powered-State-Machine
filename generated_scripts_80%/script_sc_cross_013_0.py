import sys
from flync.model.flync_4_bus.can_bus import CANBus
from flync.model.flync_4_nm.state_management import StateManagementGroup
from pydantic import ValidationError

scenario = {
    "type": "Negative",
    "description": "CANBus Declares StateManagementGroup Membership Without Mapping the Group NM PDU"
}

canbus_config = {
    "name": "Test CAN Bus",
    "baud_rate": 1000000,
    "fd_enabled": False,
    "state_memberships": [
        {"group_name": "Test Group", "pdu_ref": ""}
    ]
}

try:
    can_bus = CANBus(**canbus_config)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)

state_management_group = StateManagementGroup(
    name="Test Group",
    nm_pdu="NM PDU",
    timing_profile="Timing Profile"
)

print(can_bus.state_memberships[0].group_name)  # Should fail due to missing pdu_ref