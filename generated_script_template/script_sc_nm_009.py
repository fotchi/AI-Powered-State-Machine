import sys

from flync.model.flync_4_nm.state_management import StateManagementConfig
from flync.model.flync_4_nm.state_management import StateManagementGroup

state_management_config = StateManagementConfig(
)
state_management_group = StateManagementGroup(
    name="demo_name",
    nm_pdu="demo_nm_pdu",
    timing_profile="demo_timing_profile",
)

print("SUCCESS")
sys.exit(0)
