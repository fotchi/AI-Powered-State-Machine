import sys
from flync.model.flync_4_nm.state_management import StateManagementConfig, StateManagementGroup
from pydantic import ValidationError

try:
    config = StateManagementConfig(
        groups=[
            StateManagementGroup(name='VEHICLE', nm_pdu='pdu1', timing_profile='profile1'),
            StateManagementGroup(name='VEHICLE', nm_pdu='pdu2', timing_profile='profile2')
        ],
        timing_profiles=[]
    )
    print("ERROR: expected ValidationError but no error was raised")
    sys.exit(1)
except ValidationError as exc:
    print(f"EXPECTED ERROR: {exc}")
    sys.exit(0)