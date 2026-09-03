import sys
from flync.model.flync_4_nm.state_management import StateManagementConfig
from flync.model.flync_4_nm.state_management import StateManagementGroup

# Create the StateManagementGroup
group = StateManagementGroup(
    name="VEHICLE",
    nm_pdu="PDU_NmMessage",
    timing_profile="standard"
)

# Create the StateManagementConfig
config = StateManagementConfig(
    groups=[group]
)

# Print success message
print("SUCCESS")
sys.exit(0)