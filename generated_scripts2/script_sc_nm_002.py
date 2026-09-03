import sys
from flync.model.flync_4_nm.state_management import StateManagementConfig
from flync.model.flync_4_nm.state_management import StateManagementGroup

try:
    group1 = StateManagementGroup(name="VEHICLE", nm_pdu="pdu1", timing_profile="profile1")
    group2 = StateManagementGroup(name="VEHICLE", nm_pdu="pdu2", timing_profile="profile2")
    config = StateManagementConfig(groups=[group1, group2])
except Exception as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)
else:
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)