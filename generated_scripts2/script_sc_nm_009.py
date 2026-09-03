import sys
from flync.model.flync_4_nm.state_management import StateManagementConfig
from flync.model.flync_4_nm.state_management import StateManagementGroup

# Create StateManagementGroup instances
group1 = StateManagementGroup(
    name="VEHICLE",
    nm_pdu="pdu1",
    timing_profile="profile1",
    description="Vehicle state management group",
    extensions={"ext1": "value1"}
)

group2 = StateManagementGroup(
    name="INFOTAINMENT",
    nm_pdu="pdu2",
    timing_profile="profile2",
    description="Infotainment state management group",
    extensions={"ext2": "value2"}
)

group3 = StateManagementGroup(
    name="POWERTRAIN",
    nm_pdu="pdu3",
    timing_profile="profile3",
    description="Powertrain state management group",
    extensions={"ext3": "value3"}
)

# Create StateManagementConfig instance
config = StateManagementConfig(
    groups=[group1, group2, group3]
)

print("SUCCESS")
sys.exit(0)